"""
Stockling - 한국투자증권 오픈API v2 기반 주식 자동매매 시스템
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
import os
import traceback
from datetime import datetime, timedelta

# 로컬 모듈 임포트
from .database import get_db, engine, Base, User
from .schemas import UserCreate, UserLogin
from .auth import get_current_user, create_access_token, get_password_hash, verify_password
from .korea_investment import get_korea_investment_client, get_paper_trading_client, get_real_trading_client

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Stockling API v2", version="2.0.0")

# 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 보안 설정
security = HTTPBearer(auto_error=False)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """메인 페이지"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """로그인 페이지"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """회원가입 페이지"""
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/profit", response_class=HTMLResponse)
async def profit_page(request: Request, user: User | None = Depends(get_current_user)):
    """수익 현황 페이지 (관리자 전용)"""
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자만 접근할 수 있습니다."
        )
    
    return templates.TemplateResponse("profit.html", {
        "request": request, 
        "user": user,
        "is_admin": user.is_admin
    })

@app.get("/picks", response_class=HTMLResponse)
async def picks_page(request: Request, user: User | None = Depends(get_current_user)):
    """추천 종목 페이지"""
    return templates.TemplateResponse("picks.html", {"request": request, "user": user})

# API 엔드포인트들
@app.post("/api/signup")
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """회원가입 API"""
    try:
        # 이메일 중복 확인
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 등록된 이메일입니다."
            )
        
        # 비밀번호 확인
        if user_data.password != user_data.password_confirm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비밀번호가 일치하지 않습니다."
            )
        
        # 비밀번호 해싱
        hashed_password = get_password_hash(user_data.password)
        
        # 사용자 생성
        new_user = User(
            email=user_data.email,
            password=hashed_password,
            is_admin=False  # 일반 사용자는 관리자가 아님
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {"message": "회원가입이 완료되었습니다."}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"회원가입 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="회원가입 중 오류가 발생했습니다."
        )

@app.post("/api/login")
async def login(user_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    """로그인 API"""
    try:
        # 사용자 확인
        user = db.query(User).filter(User.email == user_data.email).first()
        if not user or not verify_password(user_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="이메일 또는 비밀번호가 올바르지 않습니다."
            )
        
        # JWT 토큰 생성
        access_token = create_access_token(data={"sub": user.email})
        
        # 쿠키에 토큰 저장
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # 개발환경에서는 False, 프로덕션에서는 True
            samesite="lax",
            max_age=24 * 60 * 60  # 24시간
        )
        
        return {
            "message": "로그인이 완료되었습니다.",
            "user": {
                "email": user.email,
                "is_admin": user.is_admin
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"로그인 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그인 중 오류가 발생했습니다."
        )

@app.post("/api/logout")
async def logout(response: Response):
    """로그아웃 API"""
    response.delete_cookie("access_token")
    return {"message": "로그아웃이 완료되었습니다."}

@app.delete("/api/user")
async def delete_user(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """회원탈퇴 API"""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요합니다."
        )
    
    try:
        db.delete(user)
        db.commit()
        return {"message": "회원탈퇴가 완료되었습니다."}
        
    except Exception as e:
        db.rollback()
        print(f"회원탈퇴 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="회원탈퇴 중 오류가 발생했습니다."
        )

@app.get("/api/profit")
async def get_profit(user: User | None = Depends(get_current_user)):
    """수익 정보 조회 API (관리자 전용)"""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요합니다."
        )

    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자만 수익 정보를 조회할 수 있습니다."
        )

    # 모의투자와 실투자 데이터를 모두 가져오기
    result = {
        "paper": None,  # 모의투자
        "real": None,   # 실투자
        "timestamp": datetime.now().isoformat()
    }
    
    # 모의투자 데이터 조회
    try:
        print("📊 모의투자 데이터 조회 시작...")
        paper_api = get_paper_trading_client()
        if paper_api:
            paper_result = paper_api.get_account_summary()
            if paper_result["success"]:
                result["paper"] = paper_result["data"]
                print("✅ 모의투자 데이터 조회 성공")
            else:
                print(f"❌ 모의투자 데이터 조회 실패: {paper_result['error']}")
        else:
            print("❌ 모의투자 API 클라이언트 생성 실패")
    except Exception as e:
        print(f"❌ 모의투자 데이터 조회 중 오류: {e}")
        traceback.print_exc()
    
    # 실투자 데이터 조회
    try:
        print("📊 실투자 데이터 조회 시작...")
        real_api = get_real_trading_client()
        if real_api:
            real_result = real_api.get_account_summary()
            if real_result["success"]:
                result["real"] = real_result["data"]
                print("✅ 실투자 데이터 조회 성공")
            else:
                print(f"❌ 실투자 데이터 조회 실패: {real_result['error']}")
        else:
            print("❌ 실투자 API 클라이언트 생성 실패")
    except Exception as e:
        print(f"❌ 실투자 데이터 조회 중 오류: {e}")
        traceback.print_exc()
    
    return result

@app.get("/api/current-price/{symbol}")
async def get_current_price(symbol: str, user: User | None = Depends(get_current_user)):
    """현재가 조회 API"""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요합니다."
        )
    
    try:
        # 기본적으로 모의투자 API 사용
        api = get_paper_trading_client()
        if not api:
            api = get_real_trading_client()
        
        if not api:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="API 클라이언트를 생성할 수 없습니다."
            )
        
        result = api.get_current_price(symbol)
        
        if result.get('rt_cd') == '0':
            return {
                "success": True,
                "data": result['output'],
                "trading_mode": api.trading_mode
            }
        else:
            return {
                "success": False,
                "error": result.get('msg1', '현재가 조회 실패'),
                "trading_mode": api.trading_mode
            }
            
    except Exception as e:
        print(f"현재가 조회 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="현재가 조회 중 오류가 발생했습니다."
        )

@app.post("/api/order/buy")
async def place_buy_order(
    symbol: str,
    quantity: int,
    price: Optional[int] = None,
    order_type: str = "지정가",
    user: User | None = Depends(get_current_user)
):
    """매수 주문 API (관리자 전용)"""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요합니다."
        )
    
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자만 주문을 실행할 수 있습니다."
        )
    
    try:
        # 현재 TRADING_MODE에 따라 API 선택
        trading_mode = os.getenv("TRADING_MODE", "paper")
        api = get_korea_investment_client(trading_mode)
        
        if not api:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="API 클라이언트를 생성할 수 없습니다."
            )
        
        result = api.place_buy_order(symbol, quantity, price, order_type)
        
        if result.get('rt_cd') == '0':
            return {
                "success": True,
                "message": f"{symbol} 매수 주문이 성공했습니다.",
                "order_info": result['output'],
                "trading_mode": api.trading_mode
            }
        else:
            return {
                "success": False,
                "error": result.get('msg1', '매수 주문 실패'),
                "trading_mode": api.trading_mode
            }
            
    except Exception as e:
        print(f"매수 주문 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="매수 주문 중 오류가 발생했습니다."
        )

@app.post("/api/order/sell")
async def place_sell_order(
    symbol: str,
    quantity: int,
    price: Optional[int] = None,
    order_type: str = "지정가",
    user: User | None = Depends(get_current_user)
):
    """매도 주문 API (관리자 전용)"""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요합니다."
        )
    
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자만 주문을 실행할 수 있습니다."
        )
    
    try:
        # 현재 TRADING_MODE에 따라 API 선택
        trading_mode = os.getenv("TRADING_MODE", "paper")
        api = get_korea_investment_client(trading_mode)
        
        if not api:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="API 클라이언트를 생성할 수 없습니다."
            )
        
        result = api.place_sell_order(symbol, quantity, price, order_type)
        
        if result.get('rt_cd') == '0':
            return {
                "success": True,
                "message": f"{symbol} 매도 주문이 성공했습니다.",
                "order_info": result['output'],
                "trading_mode": api.trading_mode
            }
        else:
            return {
                "success": False,
                "error": result.get('msg1', '매도 주문 실패'),
                "trading_mode": api.trading_mode
            }
            
    except Exception as e:
        print(f"매도 주문 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="매도 주문 중 오류가 발생했습니다."
        )

@app.get("/api/orders")
async def get_orders(user: User | None = Depends(get_current_user)):
    """주문/체결 조회 API (관리자 전용)"""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요합니다."
        )
    
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자만 주문 정보를 조회할 수 있습니다."
        )
    
    try:
        # 현재 TRADING_MODE에 따라 API 선택
        trading_mode = os.getenv("TRADING_MODE", "paper")
        api = get_korea_investment_client(trading_mode)
        
        if not api:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="API 클라이언트를 생성할 수 없습니다."
            )
        
        result = api.get_order_status()
        
        if result.get('rt_cd') == '0':
            return {
                "success": True,
                "data": result,
                "trading_mode": api.trading_mode
            }
        else:
            return {
                "success": False,
                "error": result.get('msg1', '주문 조회 실패'),
                "trading_mode": api.trading_mode
            }
            
    except Exception as e:
        print(f"주문 조회 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="주문 조회 중 오류가 발생했습니다."
        )

# 서버 시작 시 관리자 계정 자동 생성
@app.on_event("startup")
async def startup_event():
    """서버 시작 시 실행되는 이벤트"""
    print("🚀 Stockling API v2 서버 시작...")
    
    # 관리자 계정 자동 생성
    try:
        from .database import SessionLocal
        from .auth import get_password_hash
        
        db = SessionLocal()
        
        admin_email = os.getenv("ADMIN_EMAIL")
        admin_password = os.getenv("ADMIN_PASSWORD")
        
        if admin_email and admin_password:
            # 기존 관리자 계정 확인
            existing_admin = db.query(User).filter(User.email == admin_email).first()
            
            if not existing_admin:
                # 새 관리자 계정 생성
                hashed_password = get_password_hash(admin_password)
                admin_user = User(
                    email=admin_email,
                    password=hashed_password,
                    is_admin=True
                )
                
                db.add(admin_user)
                db.commit()
                print(f"✅ 관리자 계정 생성 완료: {admin_email}")
            else:
                print(f"ℹ️ 기존 관리자 계정 확인: {admin_email}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ 관리자 계정 생성 중 오류: {e}")
    
    print("✅ 서버 시작 완료")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 


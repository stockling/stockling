from fastapi import FastAPI, Request, Depends, HTTPException, status, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import uvicorn
from contextlib import asynccontextmanager

from .database import get_db, create_tables, User
from .auth import (
    validate_email, 
    validate_password, 
    check_email_exists, 
    authenticate_user
)
from .schemas import UserCreate, UserLogin, EmailCheck
from .security import create_access_token, decode_access_token, get_password_hash

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션의 시작과 종료 시 수행할 작업을 정의하는 lifespan 이벤트 핸들러입니다.
    시작 시: 데이터베이스 테이블을 생성합니다.
    """
    create_tables()
    yield
    # 애플리케이션 종료 시 필요한 정리 작업이 있다면 여기에 추가합니다.

app = FastAPI(lifespan=lifespan)

# 정적 파일 경로 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 템플릿 경로 설정
templates = Jinja2Templates(directory="templates")

# 현재 로그인된 사용자 정보를 가져오는 의존성
def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    email = decode_access_token(token)
    if not email:
        return None
    
    user = db.query(User).filter(User.email == email).first()
    return user

@app.get("/", response_class=HTMLResponse)
def read_index(request: Request, user: User | None = Depends(get_current_user)):
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

@app.get("/login", response_class=HTMLResponse)
def read_login(request: Request, user: User | None = Depends(get_current_user)):
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("login.html", {"request": request, "user": None})

@app.get("/signup", response_class=HTMLResponse)
def read_signup(request: Request, user: User | None = Depends(get_current_user)):
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("signup.html", {"request": request, "user": None})

@app.get("/profit", response_class=HTMLResponse)
def read_profit(request: Request, user: User | None = Depends(get_current_user)):
    return templates.TemplateResponse("profit.html", {"request": request, "user": user})

@app.get("/picks", response_class=HTMLResponse)
def read_recommendations(request: Request, user: User | None = Depends(get_current_user)):
    return templates.TemplateResponse("picks.html", {"request": request, "user": user})

# API 엔드포인트들
@app.post("/api/check-email")
def check_email(email_data: EmailCheck, db: Session = Depends(get_db)):
    """이메일 중복 확인"""
    if not validate_email(email_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효하지 않은 이메일 형식입니다."
        )
    
    exists = check_email_exists(db, email_data.email)
    return {"exists": exists}

@app.post("/api/signup")
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """회원가입"""
    # 이메일 형식 검증
    if not validate_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효하지 않은 이메일 형식입니다."
        )
    
    # 이메일 중복 확인
    if check_email_exists(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 이메일입니다."
        )
    
    # 비밀번호 형식 검증
    is_valid, message = validate_password(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # 비밀번호 확인
    if user_data.password != user_data.password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비밀번호가 일치하지 않습니다."
        )
    
    # 사용자 생성
    hashed_password = get_password_hash(user_data.password)
    db_user = User(email=user_data.email, password=hashed_password)
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return {"message": "회원가입이 완료되었습니다."}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="회원가입 중 오류가 발생했습니다."
        )

@app.post("/api/login")
def login(response: Response, user_data: UserLogin, db: Session = Depends(get_db)):
    """로그인 후 토큰을 쿠키에 저장"""
    user = authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다."
        )
    
    # 액세스 토큰 생성
    access_token = create_access_token(data={"sub": user.email})
    
    # 토큰을 httponly 쿠키에 저장
    response.set_cookie(key="access_token", value=access_token, httponly=True, samesite='lax')
    
    return {"message": "로그인되었습니다."}

@app.post("/api/logout")
def logout():
    """로그아웃 API. 토큰 쿠키를 삭제합니다."""
    response = JSONResponse(status_code=status.HTTP_200_OK, content={"message": "로그아웃 성공"})
    response.delete_cookie(key="access_token")
    return response

@app.delete("/api/user")
def delete_user(
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user)
):
    """회원 탈퇴 API. 사용자 정보를 삭제하고 토큰 쿠키를 제거합니다."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증되지 않은 사용자입니다."
        )
    
    # 데이터베이스에서 사용자 삭제
    db.delete(user)
    db.commit()
    
    # 응답 생성 및 쿠키 삭제
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(key="access_token")
    return response

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True) 
"""
한국투자증권 오픈API v2 - 공식 개발자 가이드 기반
주식 자동매매 프로그램을 위한 완전한 API 구현
"""

import os
import json
import time
import datetime
import requests
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from pathlib import Path

# .env 파일 로드
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class KoreaInvestmentAPI:
    """
    한국투자증권 오픈API v2 클래스
    공식 개발자 가이드에 따른 완전한 구현
    """
    
    def __init__(self, trading_mode: str = "paper"):
        """
        한국투자증권 API 초기화
        
        Args:
            trading_mode: "paper" (모의투자) 또는 "real" (실투자)
        """
        self.trading_mode = trading_mode.upper()
        # 모의투자/실투자 도메인 분기
        if self.trading_mode == "PAPER":
            self.base_url = "https://openapivts.koreainvestment.com:29443"
            self.api_key = os.getenv("KIS_APP_KEY_PAPER")
            self.api_secret = os.getenv("KIS_APP_SECRET_PAPER")
            self.account_no = os.getenv("KIS_ACCOUNT_NO_PAPER")
            self.account_code = os.getenv("KIS_ACCOUNT_CODE_PAPER")
            self.is_mock = True
        elif self.trading_mode == "REAL":
            self.base_url = "https://openapi.koreainvestment.com:9443"
            self.api_key = os.getenv("KIS_APP_KEY_REAL")
            self.api_secret = os.getenv("KIS_APP_SECRET_REAL")
            self.account_no = os.getenv("KIS_ACCOUNT_NO_REAL")
            self.account_code = os.getenv("KIS_ACCOUNT_CODE_REAL")
            self.is_mock = False
        else:
            raise ValueError("trading_mode는 'paper' 또는 'real'이어야 합니다.")
        
        # 설정 검증
        if not all([self.api_key, self.api_secret, self.account_no, self.account_code]):
            raise ValueError(f"[{self.trading_mode} 모드] API 설정이 완료되지 않았습니다.")
        
        # 토큰 캐시
        self.access_token = None
        self.token_expires_at = None
        
        print(f"✅ 한국투자증권 API 초기화 완료 ({self.trading_mode} 모드)")
        print(f"   계좌번호: {self.account_no}-{self.account_code}")
        print(f"   API Key: {self.api_key[:10]}..." if self.api_key else "   API Key: None")
        print(f"   API Secret: {self.api_secret[:10]}..." if self.api_secret else "   API Secret: None")
    
    def _get_access_token(self) -> str:
        """
        Access Token 발급 (캐시 지원)
        
        Returns:
            Access Token 문자열
        """
        # 캐시된 토큰이 유효한지 확인
        if (self.access_token and self.token_expires_at and 
            time.time() < self.token_expires_at - 60):  # 1분 여유
            return self.access_token
        
        print("🔄 Access Token 발급 중...")
        
        url = f"{self.base_url}/oauth2/tokenP"
        headers = {"content-type": "application/json"}
        body = {
            "grant_type": "client_credentials",
            "appkey": self.api_key,
            "appsecret": self.api_secret
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(body))
            response.raise_for_status()
            
            data = response.json()
            self.access_token = data['access_token']
            
            # 만료시간 설정 (24시간)
            self.token_expires_at = time.time() + 24 * 60 * 60
            
            print("✅ Access Token 발급 성공")
            return self.access_token
            
        except Exception as e:
            print(f"❌ Access Token 발급 실패: {e}")
            raise
    
    def _make_request(self, method: str, endpoint: str, headers: Dict = None, 
                     params: Dict = None, data: Dict = None) -> Dict:
        """
        API 요청 공통 메서드
        
        Args:
            method: HTTP 메서드 ("GET", "POST")
            endpoint: API 엔드포인트
            headers: 추가 헤더
            params: URL 파라미터
            data: 요청 데이터
            
        Returns:
            API 응답 데이터
        """
        access_token = self._get_access_token()
        
        url = f"{self.base_url}{endpoint}"
        
        # 기본 헤더 설정
        request_headers = {
            "Content-Type": "application/json",
            "authorization": f"Bearer {access_token}",
            "appKey": self.api_key,
            "appSecret": self.api_secret,
        }
        
        if headers:
            request_headers.update(headers)
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=request_headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, headers=request_headers, 
                                       data=json.dumps(data) if data else None)
            else:
                raise ValueError(f"지원하지 않는 HTTP 메서드: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ API 요청 실패: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"   응답 내용: {e.response.text}")
            raise
    
    def get_account_balance(self) -> Dict[str, Any]:
        """
        계좌 잔고 조회
        
        Returns:
            잔고 정보 딕셔너리
        """
        print("📊 계좌 잔고 조회 중...")
        
        endpoint = "/uapi/domestic-stock/v1/trading/inquire-balance"
        # 모의투자/실투자 tr_id 분기
        if self.is_mock:
            tr_id = "VTTC8434R"  # 모의투자 tr_id
        else:
            tr_id = "TTTC8434R"  # 실투자 tr_id
        headers = {
            "tr_id": tr_id,  # 실전/모의투자 잔고 조회
            "custtype": "P"  # 개인
        }
        params = {
            "CANO": self.account_no,
            "ACNT_PRDT_CD": self.account_code,
            "AFHR_FLPR_YN": "N",  # 시간외 여부
            "OFL_YN": "",  # 오프라인 여부
            "INQR_DVSN": "01",  # 조회구분 (01: 종목별)
            "UNPR_DVSN": "01",  # 단가구분 (01: 평균단가)
            "FUND_STTL_ICLD_YN": "N",  # 펀드결제분 포함여부
            "FNCG_AMT_AUTO_RDPT_YN": "N",  # 융자금액 자동상환여부
            "PRCS_DVSN": "01",  # 처리구분 (01: 전일)
            "CTX_AREA_FK100": "",  # 연속조회검색조건
            "CTX_AREA_NK100": ""   # 연속조회키
        }
        
        try:
            result = self._make_request("GET", endpoint, headers=headers, params=params)
            
            if result.get('rt_cd') == '0':
                print("✅ 잔고 조회 성공")
                return result
            else:
                print(f"❌ 잔고 조회 실패: {result.get('msg1', '알 수 없는 오류')}")
                return result
                
        except Exception as e:
            print(f"❌ 잔고 조회 중 오류 발생: {e}")
            raise
    
    def get_current_price(self, symbol: str) -> Dict[str, Any]:
        """
        현재가 조회
        
        Args:
            symbol: 종목코드 (6자리)
            
        Returns:
            현재가 정보 딕셔너리
        """
        print(f"💰 {symbol} 현재가 조회 중...")
        
        endpoint = "/uapi/domestic-stock/v1/quotations/inquire-price"
        headers = {
            "tr_id": "FHKST01010100"  # 주식 현재가 시세
        }
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",  # 시장분류코드 (J: 주식)
            "FID_INPUT_ISCD": symbol  # 종목코드
        }
        
        try:
            result = self._make_request("GET", endpoint, headers=headers, params=params)
            
            if result.get('rt_cd') == '0':
                print(f"✅ {symbol} 현재가 조회 성공")
                return result
            else:
                print(f"❌ {symbol} 현재가 조회 실패: {result.get('msg1', '알 수 없는 오류')}")
                return result
                
        except Exception as e:
            print(f"❌ 현재가 조회 중 오류 발생: {e}")
            raise
    
    def place_buy_order(self, symbol: str, quantity: int, price: int = None, 
                       order_type: str = "지정가") -> Dict[str, Any]:
        """
        매수 주문
        
        Args:
            symbol: 종목코드
            quantity: 주문수량
            price: 주문가격 (시장가 주문 시 None)
            order_type: 주문구분 ("지정가", "시장가")
            
        Returns:
            주문 결과 딕셔너리
        """
        print(f"📈 {symbol} 매수 주문 중... ({order_type}, {quantity}주)")
        
        endpoint = "/uapi/domestic-stock/v1/trading/order-cash"
        
        # 주문구분 설정
        if order_type == "지정가":
            ord_dvsn = "00"
            tr_id = "TTTC0802U"  # 주식 현금 매수 주문
        elif order_type == "시장가":
            ord_dvsn = "01"
            tr_id = "TTTC0802U"
        else:
            raise ValueError("주문구분은 '지정가' 또는 '시장가'여야 합니다.")
        
        headers = {
            "tr_id": tr_id,
            "custtype": "P"
        }
        
        data = {
            "CANO": self.account_no,
            "ACNT_PRDT_CD": self.account_code,
            "PDNO": symbol,
            "ORD_DVSN": ord_dvsn,
            "ORD_QTY": str(quantity),
            "ORD_UNPR": str(price) if price else "0"
        }
        
        try:
            result = self._make_request("POST", endpoint, headers=headers, data=data)
            
            if result.get('rt_cd') == '0':
                print(f"✅ {symbol} 매수 주문 성공")
                return result
            else:
                print(f"❌ {symbol} 매수 주문 실패: {result.get('msg1', '알 수 없는 오류')}")
                return result
                
        except Exception as e:
            print(f"❌ 매수 주문 중 오류 발생: {e}")
            raise
    
    def place_sell_order(self, symbol: str, quantity: int, price: int = None, 
                        order_type: str = "지정가") -> Dict[str, Any]:
        """
        매도 주문
        
        Args:
            symbol: 종목코드
            quantity: 주문수량
            price: 주문가격 (시장가 주문 시 None)
            order_type: 주문구분 ("지정가", "시장가")
            
        Returns:
            주문 결과 딕셔너리
        """
        print(f"📉 {symbol} 매도 주문 중... ({order_type}, {quantity}주)")
        
        endpoint = "/uapi/domestic-stock/v1/trading/order-cash"
        
        # 주문구분 설정
        if order_type == "지정가":
            ord_dvsn = "00"
            tr_id = "TTTC0801U"  # 주식 현금 매도 주문
        elif order_type == "시장가":
            ord_dvsn = "01"
            tr_id = "TTTC0801U"
        else:
            raise ValueError("주문구분은 '지정가' 또는 '시장가'여야 합니다.")
        
        headers = {
            "tr_id": tr_id,
            "custtype": "P"
        }
        
        data = {
            "CANO": self.account_no,
            "ACNT_PRDT_CD": self.account_code,
            "PDNO": symbol,
            "ORD_DVSN": ord_dvsn,
            "ORD_QTY": str(quantity),
            "ORD_UNPR": str(price) if price else "0"
        }
        
        try:
            result = self._make_request("POST", endpoint, headers=headers, data=data)
            
            if result.get('rt_cd') == '0':
                print(f"✅ {symbol} 매도 주문 성공")
                return result
            else:
                print(f"❌ {symbol} 매도 주문 실패: {result.get('msg1', '알 수 없는 오류')}")
                return result
                
        except Exception as e:
            print(f"❌ 매도 주문 중 오류 발생: {e}")
            raise
    
    def cancel_order(self, org_no: str, order_no: str, quantity: int) -> Dict[str, Any]:
        """
        주문 취소
        
        Args:
            org_no: 원주문번호
            order_no: 주문번호
            quantity: 취소수량
            
        Returns:
            취소 결과 딕셔너리
        """
        print(f"❌ 주문 취소 중... (주문번호: {order_no})")
        
        endpoint = "/uapi/domestic-stock/v1/trading/order-cash"
        headers = {
            "tr_id": "TTTC0803U",  # 주식 현금 주문 취소
            "custtype": "P"
        }
        
        data = {
            "CANO": self.account_no,
            "ACNT_PRDT_CD": self.account_code,
            "KRX_FWDG_ORD_ORGNO": org_no,
            "ORGN_ODNO": order_no,
            "ORD_DVSN": "00",
            "ORD_QTY": str(quantity)
        }
        
        try:
            result = self._make_request("POST", endpoint, headers=headers, data=data)
            
            if result.get('rt_cd') == '0':
                print(f"✅ 주문 취소 성공")
                return result
            else:
                print(f"❌ 주문 취소 실패: {result.get('msg1', '알 수 없는 오류')}")
                return result
                
        except Exception as e:
            print(f"❌ 주문 취소 중 오류 발생: {e}")
            raise
    
    def get_order_status(self) -> Dict[str, Any]:
        """
        주문/체결 조회
        
        Returns:
            주문/체결 정보 딕셔너리
        """
        print("📋 주문/체결 조회 중...")
        
        endpoint = "/uapi/domestic-stock/v1/trading/inquire-order"
        headers = {
            "tr_id": "TTTC8001R",  # 주식 주문/체결 조회
            "custtype": "P"
        }
        params = {
            "CANO": self.account_no,
            "ACNT_PRDT_CD": self.account_code,
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": ""
        }
        
        try:
            result = self._make_request("GET", endpoint, headers=headers, params=params)
            
            if result.get('rt_cd') == '0':
                print("✅ 주문/체결 조회 성공")
                return result
            else:
                print(f"❌ 주문/체결 조회 실패: {result.get('msg1', '알 수 없는 오류')}")
                return result
                
        except Exception as e:
            print(f"❌ 주문/체결 조회 중 오류 발생: {e}")
            raise
    
    def get_account_summary(self) -> Dict[str, Any]:
        """
        계좌 요약 정보 조회 (잔고 + 보유종목)
        
        Returns:
            계좌 요약 정보 딕셔너리
        """
        print("📊 계좌 요약 정보 조회 중...")
        
        try:
            # 잔고 조회
            balance_data = self.get_account_balance()
            
            if balance_data.get('rt_cd') != '0':
                return {
                    "success": False,
                    "error": balance_data.get('msg1', '잔고 조회 실패'),
                    "data": None
                }
            
            # 데이터 파싱
            output1 = balance_data.get('output1', [])  # 보유종목
            output2 = balance_data.get('output2', [])  # 계좌요약
            
            # 계좌 요약 정보
            account_summary = {
                "total_balance": 0,      # 총 평가금액
                "total_profit": 0,       # 총 평가손익
                "total_purchase_amount": 0,  # 총 매입금액
                "available_cash": 0,     # 주문가능현금
                "holdings": [],          # 보유종목 목록
                "account_info": {
                    "account_no": f"{self.account_no}-{self.account_code}",
                    "trading_mode": self.trading_mode,
                    "is_mock": self.is_mock
                }
            }
            
            # 계좌 요약 정보 파싱
            if output2 and len(output2) > 0:
                summary = output2[0]
                account_summary["total_balance"] = int(float(summary.get('tot_evlu_amt', 0)))
                account_summary["total_profit"] = int(float(summary.get('evlu_pfls_smtl_amt', 0)))
                account_summary["total_purchase_amount"] = int(float(summary.get('pchs_amt_smtl_amt', 0)))
                account_summary["available_cash"] = int(float(summary.get('ord_psbl_cash', 0)))
            
            # 보유종목 정보 파싱
            for holding in output1:
                symbol = holding.get('pdno', '')
                if symbol:  # 종목코드가 있는 경우만
                    purchase_price = int(float(holding.get('pchs_avg_pric', 0)))
                    quantity = int(float(holding.get('hldg_qty', 0)))
                    current_price = int(float(holding.get('prpr', 0)))
                    profit = int(float(holding.get('evlu_pfls_amt', 0)))
                    total_value = int(float(holding.get('evlu_amt', 0)))
                    
                    # 수익률 계산
                    profit_rate = 0
                    if purchase_price > 0:
                        profit_rate = ((current_price - purchase_price) / purchase_price) * 100
                    
                    account_summary["holdings"].append({
                        "symbol": symbol,
                        "name": holding.get('prdt_name', ''),
                        "quantity": quantity,
                        "purchase_price": purchase_price,
                        "current_price": current_price,
                        "profit": profit,
                        "profit_rate": round(profit_rate, 2),
                        "total_value": total_value
                    })
            
            print("✅ 계좌 요약 정보 조회 성공")
            return {
                "success": True,
                "error": None,
                "data": account_summary
            }
            
        except Exception as e:
            print(f"❌ 계좌 요약 정보 조회 중 오류 발생: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }

# 편의 함수들
# --- 싱글턴 인스턴스 캐싱 추가 ---
_paper_api_instance = None
_real_api_instance = None

def get_korea_investment_client(trading_mode: str = None) -> Optional[KoreaInvestmentAPI]:
    """
    한국투자증권 API 클라이언트 생성
    
    Args:
        trading_mode: "paper" 또는 "real" (None이면 환경변수에서 읽음)
        
    Returns:
        KoreaInvestmentAPI 인스턴스 또는 None
    """
    if trading_mode is None:
        trading_mode = os.getenv("TRADING_MODE", "paper")
    try:
        return KoreaInvestmentAPI(trading_mode)
    except Exception as e:
        print(f"❌ API 클라이언트 생성 실패: {e}")
        return None

# 싱글턴으로 인스턴스 재사용

def get_paper_trading_client() -> Optional[KoreaInvestmentAPI]:
    """모의투자용 API 클라이언트 싱글턴 반환"""
    global _paper_api_instance
    if _paper_api_instance is None:
        _paper_api_instance = get_korea_investment_client("paper")
    return _paper_api_instance

def get_real_trading_client() -> Optional[KoreaInvestmentAPI]:
    """실투자용 API 클라이언트 싱글턴 반환"""
    global _real_api_instance
    if _real_api_instance is None:
        _real_api_instance = get_korea_investment_client("real")
    return _real_api_instance

# 자동매매 봇 예시 클래스
class StockTradingBot:
    """
    주식 자동매매 봇 예시 클래스
    """
    
    def __init__(self, trading_mode: str = "paper"):
        self.api = get_korea_investment_client(trading_mode)
        self.trading_strategy = None
        
    def set_trading_strategy(self, strategy_func):
        """
        거래 전략 설정
        
        Args:
            strategy_func: 거래 전략 함수
        """
        self.trading_strategy = strategy_func
    
    def run_strategy(self):
        """
        거래 전략 실행
        """
        if not self.trading_strategy:
            print("❌ 거래 전략이 설정되지 않았습니다.")
            return
        
        try:
            # 계좌 정보 조회
            account_info = self.api.get_account_summary()
            if not account_info["success"]:
                print(f"❌ 계좌 정보 조회 실패: {account_info['error']}")
                return
            
            # 거래 전략 실행
            self.trading_strategy(self.api, account_info["data"])
            
        except Exception as e:
            print(f"❌ 거래 전략 실행 중 오류: {e}")

# 간단한 거래 전략 예시
def simple_moving_average_strategy(api, account_data):
    """
    단순 이동평균 전략 예시
    """
    print("📈 단순 이동평균 전략 실행 중...")
    
    # 관심 종목 리스트
    target_stocks = ['005930', '000660', '035420']  # 삼성전자, SK하이닉스, NAVER
    
    for symbol in target_stocks:
        try:
            # 현재가 조회
            price_data = api.get_current_price(symbol)
            if price_data.get('rt_cd') != '0':
                continue
            
            current_price = int(price_data['output']['stck_prpr'])
            print(f"   {symbol} 현재가: {current_price:,}원")
            
            # 여기에 실제 거래 로직 구현
            # 예: 이동평균 계산, 매수/매도 조건 확인 등
            
        except Exception as e:
            print(f"   {symbol} 처리 중 오류: {e}")

if __name__ == "__main__":
    # 사용 예시
    print("🚀 한국투자증권 API 테스트 시작")
    
    # API 클라이언트 생성
    api = get_korea_investment_client()
    if not api:
        print("❌ API 클라이언트 생성 실패")
        exit(1)
    
    # 계좌 요약 정보 조회
    result = api.get_account_summary()
    if result["success"]:
        data = result["data"]
        print(f"📊 계좌 정보:")
        print(f"   계좌번호: {data['account_info']['account_no']}")
        print(f"   투자모드: {data['account_info']['trading_mode']}")
        print(f"   총 평가금액: {data['total_balance']:,}원")
        print(f"   총 평가손익: {data['total_profit']:,}원")
        print(f"   보유종목 수: {len(data['holdings'])}개")
        
        for holding in data['holdings']:
            print(f"   📈 {holding['name']}({holding['symbol']}): "
                  f"{holding['quantity']}주, "
                  f"수익률 {holding['profit_rate']}%")
    else:
        print(f"❌ 계좌 정보 조회 실패: {result['error']}")
    
    print("✅ 테스트 완료") 
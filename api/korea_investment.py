import os
import mojito
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from pathlib import Path
from mojito import KoreaInvestment

# .env 파일 로드
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class KoreaInvestmentAPI:
    """한국투자증권 API 연동 클래스"""
    
    def __init__(self, api_key: str, api_secret: str, acc_no: str, mock: bool = False):
        """
        한국투자증권 API 초기화
        
        Args:
            api_key: API 키
            api_secret: API 시크릿
            acc_no: 계좌번호
            mock: 모의투자 여부 (기본값: False)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.acc_no = acc_no
        self.mock = mock
        
        # 모히토 브로커 객체 생성
        self.broker = KoreaInvestment(
            api_key=api_key,
            api_secret=api_secret,
            acc_no=acc_no,
            mock=mock
        )
    
    def get_current_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        현재가 조회
        
        Args:
            symbol: 종목코드 (6자리)
            
        Returns:
            현재가 정보 딕셔너리 또는 None
        """
        try:
            resp = self.broker.fetch_price(symbol)
            if resp.get('rt_cd') == '0':
                return resp.get('output')
            print(f"현재가 조회 실패: {resp}")
            return None
        except Exception as e:
            print(f"현재가 조회 오류: {e}")
            return None
    
    def get_balance(self) -> Optional[Dict[str, Any]]:
        """
        잔고 조회
        
        Returns:
            잔고 정보 딕셔너리 또는 None
        """
        try:
            resp = self.broker.fetch_balance()
            # rt_cd가 '0'이거나, rt_cd가 없어도 output1이나 output2가 있으면 성공
            if resp.get('rt_cd') == '0' or resp.get('output1') is not None or resp.get('output2') is not None:
                return resp
            print(f"잔고 조회 실패: {resp}")
            return None
        except Exception as e:
            print(f"잔고 조회 오류: {e}")
            return None
    
    def get_holdings(self) -> list:
        """
        보유 종목 조회
        
        Returns:
            보유 종목 리스트
        """
        try:
            resp = self.broker.fetch_balance()
            # rt_cd가 '0'이거나, rt_cd가 없어도 output1이 있으면 성공
            if resp.get('rt_cd') == '0' or resp.get('output1') is not None:
                return resp.get('output1', [])
            return []
        except Exception as e:
            print(f"보유 종목 조회 오류: {e}")
            return []
    
    def get_ohlcv(self, symbol: str, timeframe: str = 'D', adj_price: bool = True) -> Optional[Dict[str, Any]]:
        """
        OHLCV 데이터 조회
        
        Args:
            symbol: 종목코드
            timeframe: 시간단위 ('D': 일봉, 'W': 주봉, 'M': 월봉)
            adj_price: 수정주가 적용 여부
            
        Returns:
            OHLCV 데이터 또는 None
        """
        try:
            resp = self.broker.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                adj_price=adj_price
            )
            if resp.get('rt_cd') == '0':
                return resp
            return None
        except Exception as e:
            print(f"OHLCV 조회 오류: {e}")
            return None
    
    def create_limit_buy_order(self, symbol: str, price: int, quantity: int) -> Optional[Dict[str, Any]]:
        """
        지정가 매수 주문
        
        Args:
            symbol: 종목코드
            price: 매수가격
            quantity: 매수수량
            
        Returns:
            주문 결과 또는 None
        """
        try:
            resp = self.broker.create_limit_buy_order(
                symbol=symbol,
                price=price,
                quantity=quantity
            )
            if resp.get('rt_cd') == '0':
                return resp
            return None
        except Exception as e:
            print(f"매수 주문 오류: {e}")
            return None
    
    def create_limit_sell_order(self, symbol: str, price: int, quantity: int) -> Optional[Dict[str, Any]]:
        """
        지정가 매도 주문
        
        Args:
            symbol: 종목코드
            price: 매도가격
            quantity: 매도수량
            
        Returns:
            주문 결과 또는 None
        """
        try:
            resp = self.broker.create_limit_sell_order(
                symbol=symbol,
                price=price,
                quantity=quantity
            )
            if resp.get('rt_cd') == '0':
                return resp
            return None
        except Exception as e:
            print(f"매도 주문 오류: {e}")
            return None
    
    def create_market_buy_order(self, symbol: str, quantity: int) -> Optional[Dict[str, Any]]:
        """
        시장가 매수 주문
        
        Args:
            symbol: 종목코드
            quantity: 매수수량
            
        Returns:
            주문 결과 또는 None
        """
        try:
            resp = self.broker.create_market_buy_order(
                symbol=symbol,
                quantity=quantity
            )
            if resp.get('rt_cd') == '0':
                return resp
            return None
        except Exception as e:
            print(f"시장가 매수 주문 오류: {e}")
            return None
    
    def create_market_sell_order(self, symbol: str, quantity: int) -> Optional[Dict[str, Any]]:
        """
        시장가 매도 주문
        
        Args:
            symbol: 종목코드
            quantity: 매도수량
            
        Returns:
            주문 결과 또는 None
        """
        try:
            resp = self.broker.create_market_sell_order(
                symbol=symbol,
                quantity=quantity
            )
            if resp.get('rt_cd') == '0':
                return resp
            return None
        except Exception as e:
            print(f"시장가 매도 주문 오류: {e}")
            return None
    
    def cancel_order(self, org_no: str, order_no: str, quantity: int, total: bool) -> Optional[Dict[str, Any]]:
        """
        주문 취소
        
        Args:
            org_no: 한국거래소 전송주문 조직번호
            order_no: 원주문번호
            quantity: 취소수량
            total: 전체 취소 여부
            
        Returns:
            취소 결과 또는 None
        """
        try:
            resp = self.broker.cancel_order(
                org_no=org_no,
                order_no=order_no,
                quantity=quantity,
                total=total
            )
            if resp.get('rt_cd') == '0':
                return resp
            return None
        except Exception as e:
            print(f"주문 취소 오류: {e}")
            return None
    
    def modify_order(self, org_no: str, order_no: str, order_type: str, price: int, quantity: int, total: bool) -> Optional[Dict[str, Any]]:
        """
        주문 정정
        
        Args:
            org_no: 한국거래소 전송주문 조직번호
            order_no: 원주문번호
            order_type: 주문타입
            price: 정정가격
            quantity: 정정수량
            total: 전체 정정 여부
            
        Returns:
            정정 결과 또는 None
        """
        try:
            resp = self.broker.modify_order(
                org_no=org_no,
                order_no=order_no,
                order_type=order_type,
                price=price,
                quantity=quantity,
                total=total
            )
            if resp.get('rt_cd') == '0':
                return resp
            return None
        except Exception as e:
            print(f"주문 정정 오류: {e}")
            return None

def get_korea_investment_client() -> Optional[KoreaInvestmentAPI]:
    """
    TRADING_MODE 환경 변수에 따라 적절한 한국투자증권 API 클라이언트를 반환합니다.
    """
    trading_mode = os.getenv("TRADING_MODE", "paper").upper() # 기본값은 'paper'

    if trading_mode == 'PAPER':
        suffix = '_PAPER'
        is_mock = True
    elif trading_mode == 'REAL':
        suffix = '_REAL'
        is_mock = False
    else:
        print(f"Invalid TRADING_MODE: {trading_mode}. Must be 'paper' or 'real'.")
        return None

    api_key = os.getenv(f"KIS_APP_KEY{suffix}")
    api_secret = os.getenv(f"KIS_APP_SECRET{suffix}")
    account_no = os.getenv(f"KIS_ACCOUNT_NO{suffix}")
    account_code = os.getenv(f"KIS_ACCOUNT_CODE{suffix}")

    if not all([api_key, api_secret, account_no, account_code]):
        print(f"[{trading_mode} mode] KIS environment variables are not set properly.")
        return None
    
    full_account_no = f"{account_no}-{account_code}"

    try:
        return KoreaInvestmentAPI(
            api_key=api_key,
            api_secret=api_secret,
            acc_no=full_account_no,
            mock=is_mock
        )
    except Exception as e:
        print(f"Failed to create KoreaInvestmentAPI client: {e}")
        return None 
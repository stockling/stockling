# Stockling v2 - 한국투자증권 오픈API v2 기반 주식 자동매매 시스템

## 🚀 개요

Stockling v2는 한국투자증권 오픈API의 **공식 개발자 가이드**에 따라 완전히 새롭게 구현된 주식 자동매매 시스템입니다. 기존의 mojito 라이브러리 의존성을 제거하고, 한국투자증권의 공식 REST API를 직접 호출하여 더 안정적이고 확장 가능한 시스템을 구축했습니다.

## ✨ 주요 개선사항

### 🔧 기술적 개선
- **공식 API 직접 호출**: mojito 라이브러리 제거, 한국투자증권 REST API 직접 사용
- **토큰 캐싱 시스템**: Access Token 자동 갱신 및 캐싱으로 성능 향상
- **에러 핸들링 강화**: 상세한 오류 메시지와 로깅 시스템
- **타입 안전성**: TypeScript 스타일의 타입 힌트 적용

### 📊 기능 개선
- **실시간 데이터**: 30초마다 자동 새로고침
- **이중 계좌 지원**: 모의투자와 실투자 계좌 동시 조회
- **상세한 수익 분석**: 종목별 수익률, 평가손익 등 상세 정보
- **주문 기능**: 매수/매도 주문 API 완전 구현

### 🎨 UI/UX 개선
- **모던한 대시보드**: Tailwind CSS 기반 반응형 디자인
- **실시간 업데이트**: 자동 새로고침 및 로딩 인디케이터
- **직관적인 탭 시스템**: 모의투자/실투자 전환
- **색상 코딩**: 수익/손실에 따른 시각적 피드백

## 🏗️ 시스템 아키텍처

```
Stockling v2
├── Frontend (HTML/CSS/JavaScript)
│   ├── 대시보드 (profit_v2.html)
│   ├── 로그인/회원가입
│   └── 반응형 UI
├── Backend (FastAPI)
│   ├── API v2 엔드포인트
│   ├── 사용자 인증
│   └── 데이터 처리
├── 한국투자증권 API v2
│   ├── 토큰 관리
│   ├── 계좌 조회
│   ├── 주문 처리
│   └── 시세 조회
└── Database (MySQL)
    ├── 사용자 관리
    └── 세션 관리
```

## 📋 설치 및 설정

### 1. 저장소 클론
```bash
git clone <repository-url>
cd stockling-setup
```

### 2. 가상환경 설정
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정 (.env)
```env
# 데이터베이스 설정
DATABASE_URL="mysql+pymysql://root:password@localhost:3306/stockling"

# JWT 설정
SECRET_KEY="your-secret-key-here"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 관리자 계정
ADMIN_EMAIL="admin@example.com"
ADMIN_PASSWORD="admin_password"

# 투자 모드 (paper: 모의투자, real: 실투자)
TRADING_MODE="paper"

# 모의투자 API 설정
KIS_APP_KEY_PAPER="your-paper-api-key"
KIS_APP_SECRET_PAPER="your-paper-api-secret"
KIS_ACCOUNT_NO_PAPER="12345678"
KIS_ACCOUNT_CODE_PAPER="01"

# 실투자 API 설정
KIS_APP_KEY_REAL="your-real-api-key"
KIS_APP_SECRET_REAL="your-real-api-secret"
KIS_ACCOUNT_NO_REAL="12345678"
KIS_ACCOUNT_CODE_REAL="01"
```

### 5. 데이터베이스 생성
```sql
CREATE DATABASE stockling CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6. 서버 실행
```bash
# v2 서버 실행 (포트 8001)
uvicorn api.main_v2:app --reload --host 0.0.0.0 --port 8001

# 기존 v1 서버 실행 (포트 8000)
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## 🔑 한국투자증권 API 설정 가이드

### 1. API 키 발급
1. [한국투자증권 개발자센터](https://developers.koreainvestment.com) 접속
2. 회원가입 및 로그인
3. 애플리케이션 등록
4. API 키 및 시크릿 발급

### 2. 계좌 정보 확인
- **계좌번호**: 8자리 숫자 (예: 12345678)
- **계좌상품코드**: 2자리 숫자 (보통 "01")
- **전체 계좌번호**: 12345678-01

### 3. 모의투자 vs 실투자
- **모의투자**: 실제 돈 없이 거래 연습 (안전)
- **실투자**: 실제 돈으로 거래 (위험)

## 🎯 주요 기능

### 📊 실시간 계좌 현황
- 총 평가금액
- 총 평가손익
- 수익률 계산
- 주문가능현금
- 보유 종목 목록

### 📈 종목별 상세 정보
- 종목코드 및 종목명
- 보유수량
- 매수가 및 현재가
- 평가손익 및 수익률
- 평가금액

### 🔄 자동 새로고침
- 30초마다 자동 데이터 업데이트
- 수동 새로고침 버튼
- 로딩 인디케이터

### 🔐 보안 기능
- JWT 토큰 기반 인증
- 관리자 권한 분리
- HTTPS 통신 (프로덕션)

## 🚀 API 엔드포인트

### 인증 관련
- `POST /api/signup` - 회원가입
- `POST /api/login` - 로그인
- `POST /api/logout` - 로그아웃
- `DELETE /api/user` - 회원탈퇴

### 계좌 정보
- `GET /api/profit` - 수익 정보 조회 (관리자 전용)
- `GET /api/current-price/{symbol}` - 현재가 조회

### 주문 처리 (관리자 전용)
- `POST /api/order/buy` - 매수 주문
- `POST /api/order/sell` - 매도 주문
- `GET /api/orders` - 주문/체결 조회

## 💻 사용 방법

### 1. 서버 시작
```bash
uvicorn api.main_v2:app --reload --host 0.0.0.0 --port 8001
```

### 2. 웹 브라우저 접속
```
http://localhost:8001
```

### 3. 관리자 로그인
- 이메일: `.env` 파일의 `ADMIN_EMAIL`
- 비밀번호: `.env` 파일의 `ADMIN_PASSWORD`

### 4. 수익 현황 확인
- `/profit` 페이지에서 실시간 계좌 현황 확인
- 모의투자/실투자 탭 전환
- 30초마다 자동 업데이트

## 🔧 개발자 가이드

### 새로운 API 클래스 사용법
```python
from api.korea_investment_v2 import get_korea_investment_client

# 모의투자 클라이언트 생성
paper_client = get_korea_investment_client('paper')

# 실투자 클라이언트 생성
real_client = get_korea_investment_client('real')

# 계좌 요약 정보 조회
result = paper_client.get_account_summary()
if result["success"]:
    data = result["data"]
    print(f"총 평가금액: {data['total_balance']:,}원")
    print(f"총 평가손익: {data['total_profit']:,}원")
```

### 자동매매 봇 예시
```python
from api.korea_investment_v2 import StockTradingBot

# 봇 생성
bot = StockTradingBot('paper')

# 거래 전략 설정
def my_strategy(api, account_data):
    # 여기에 거래 로직 구현
    pass

bot.set_trading_strategy(my_strategy)
bot.run_strategy()
```

## 🛠️ 문제 해결

### 일반적인 오류

#### 1. API 키 오류
```
❌ API 클라이언트 생성 실패: [PAPER 모드] API 설정이 완료되지 않았습니다.
```
**해결방법**: `.env` 파일의 API 키 설정 확인

#### 2. 계좌번호 오류
```
❌ 잔고 조회 실패: 계좌번호가 올바르지 않습니다.
```
**해결방법**: 계좌번호와 계좌상품코드 확인

#### 3. 토큰 만료 오류
```
❌ Access Token 발급 실패: 401 Unauthorized
```
**해결방법**: API 키와 시크릿 재확인

### 디버깅 모드
```python
# 상세한 로그 출력
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 성능 최적화

### 1. 토큰 캐싱
- Access Token 24시간 캐싱
- 자동 갱신 시스템

### 2. 요청 최적화
- 불필요한 API 호출 최소화
- 배치 처리 지원

### 3. 메모리 관리
- 효율적인 데이터 구조
- 가비지 컬렉션 최적화

## 🔮 향후 계획

### 단기 계획
- [ ] 실시간 웹소켓 지원
- [ ] 모바일 앱 개발
- [ ] 알림 시스템 구현

### 중기 계획
- [ ] 고급 차트 기능
- [ ] 백테스팅 시스템
- [ ] 포트폴리오 분석

### 장기 계획
- [ ] AI 기반 매매 전략
- [ ] 다중 브로커 지원
- [ ] 클라우드 배포

## 📞 지원 및 문의

- **GitHub Issues**: [이슈 등록](https://github.com/your-repo/issues)
- **한국투자증권 개발자센터**: [https://developers.koreainvestment.com](https://developers.koreainvestment.com)
- **API 문서**: [https://apiportal.koreainvestment.com](https://apiportal.koreainvestment.com)

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

---

**⚠️ 주의사항**: 이 시스템은 교육 및 개발 목적으로 제작되었습니다. 실제 투자에 사용하기 전에 충분한 테스트와 검증이 필요합니다. 투자 손실에 대한 책임은 사용자에게 있습니다. 
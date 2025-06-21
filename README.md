# Stockling - 주식 자동매매 시스템

Stockling은 한국투자증권 오픈API를 활용하여 **단일 마스터 계정**의 수익 현황을 조회하고, 추후 자동매매 기능을 구현하기 위한 기반 시스템입니다.
현재는 MVP 구현 중이므로, 단일 관리자 계정의 소유주만 본인 계좌 현황을 확인할 수 있게 만들었습니다.

## 주요 기능

- 🔐 사용자 인증 시스템 (회원가입/로그인)
- 🔑 **관리자 계정 자동 생성**: `.env` 파일에 지정된 정보로 서버 시작 시 관리자 계정을 자동으로 생성합니다.
- 📊 **관리자 전용 수익 현황**: 관리자 계정으로 로그인해야만 마스터 계좌의 실시간 수익 현황을 조회할 수 있습니다.
- 🔗 한국투자증권 API 연동 (모의/실전 투자 모드 지원)
- 📱 반응형 웹 인터페이스

## 기술 스택

- **Backend**: FastAPI, SQLAlchemy, Python
- **Frontend**: HTML, CSS (Tailwind CSS), JavaScript
- **Database**: MySQL
- **API**: 한국투자증권 오픈API (`mojito` 라이브러리)
- **Security**: JWT, 비밀번호 해싱

## 설치 및 설정

### 1. 저장소 클론
```bash
git clone <repository-url>
cd stockling-setup
```

### 2. 가상환경 생성 및 활성화
```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정
- 프로젝트 루트에 `.env` 파일을 생성하고 아래 내용을 참고하여 채워주세요.
- GitHub Actions를 사용하는 경우, 해당 저장소의 `Settings > Secrets and variables > Actions`에 아래 변수들을 등록하세요.

```env
# 데이터베이스 설정 (사용자 환경에 맞게 수정)
DATABASE_URL="mysql+pymysql://root:password@localhost:3306/dbname"

# JWT 토큰 설정
SECRET_KEY="your-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440 # 24시간

# 관리자 계정 설정 (서버 시작 시 이 정보로 계정이 생성/확인됩니다)
ADMIN_EMAIL="admin@example.com"
ADMIN_PASSWORD="admin_password"

# --- 한국투자증권 API 설정 ---

# 'paper': 모의투자, 'real': 실전투자
TRADING_MODE="paper" 

# [모의투자 계정 정보]
KIS_APP_KEY_PAPER="your-paper-api-key"
KIS_APP_SECRET_PAPER="your-paper-api-secret"
KIS_ACCOUNT_NO_PAPER="your-paper-account-no" # 계좌번호 앞 8자리
KIS_ACCOUNT_CODE_PAPER="01" # 계좌번호 뒤 2자리

# [실전투자 계정 정보]
KIS_APP_KEY_REAL="your-live-api-key"
KIS_APP_SECRET_REAL="your-live-api-secret"
KIS_ACCOUNT_NO_REAL="your-live-account-no" # 계좌번호 앞 8자리
KIS_ACCOUNT_CODE_REAL="01" # 계좌번호 뒤 2자리
```

### 5. 데이터베이스 생성
MySQL 서버에 접속하여 `stockling-db` 데이터베이스를 생성합니다. (이미 생성했다면 생략)
```sql
CREATE DATABASE stockling CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6. 애플리케이션 실행
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```
서버가 `http://localhost:8000`에서 실행됩니다.

## 사용 방법

1.  **서버 실행**: `uvicorn` 명령어로 서버를 실행하면, `.env` 파일에 설정된 `ADMIN_EMAIL`과 `ADMIN_PASSWORD`로 관리자 계정이 데이터베이스에 자동으로 생성됩니다.
2.  **관리자 로그인**: 웹사이트에 접속하여 위에서 설정한 관리자 계정으로 로그인합니다.
3.  **수익 현황 확인**: `/profit` 페이지로 이동하면, `.env` 파일의 `TRADING_MODE`에 따라 설정된 마스터 계좌의 실시간 수익 현황이 표시됩니다. 일반 사용자는 이 페이지에 접근할 수 없습니다.

## API 엔드포인트

- `POST /api/signup`: 일반 사용자 회원가입
- `POST /api/login`: 로그인 (일반/관리자)
- `POST /api/logout`: 로그아웃
- `DELETE /api/user`: 회원탈퇴 (로그인한 사용자 본인)
- `GET /api/profit`: **(관리자 전용)** 수익 정보 조회

## 보안 기능

- **JWT 토큰 기반 인증**: `httponly` 쿠키를 사용하여 안전하게 토큰을 관리합니다.
- **비밀번호 해싱**: `bcrypt`를 사용하여 사용자의 비밀번호를 안전하게 해싱하여 저장합니다.
- **관리자 권한 분리**: 일반 사용자와 관리자의 접근 권한을 분리하여 민감한 정보(수익 현황)를 보호합니다.

## 개발 환경

### 필수 패키지
- `fastapi`
- `uvicorn`
- `sqlalchemy`
- `pymysql`
- `python-dotenv`
- `passlib`
- `python-jose`
- `bcrypt`
- `mojito`

### 개발 도구
- Python 3.8+
- MySQL 8.0+
- Git

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 기여하기

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## 문의사항

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해 주세요. 
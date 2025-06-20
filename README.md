# Stockling - 자동매매 플랫폼

## 프로젝트 설정

### 1. 가상환경 생성 및 활성화
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정
- 프로젝트 최상위 디렉토리에 `.env` 파일을 생성하고, 아래 내용을 자신의 데이터베이스 환경에 맞게 수정하여 추가합니다.
- 이 파일은 Git에 포함되지 않으므로 민감한 정보를 안전하게 보관할 수 있습니다.

```env
# .env 파일 예시
DATABASE_URL="mysql+pymysql://YOUR_USERNAME:YOUR_PASSWORD@YOUR_HOST:PORT/YOUR_DB_NAME"
```

- 예를 들어, 사용자 이름이 `root`이고 비밀번호가 `123456`, 호스트가 `localhost:3307`, 데이터베이스 이름이 `stockling_db`인 경우 아래와 같이 작성합니다.
```env
# .env 파일 작성 예시
DATABASE_URL="mysql+pymysql://root:123456@localhost:3307/stockling_db"
```

### 4. 애플리케이션 실행
```bash
uvicorn api.main:app --reload
```

## 기능

### 회원가입
- 이메일을 아이디로 사용
- 이메일 중복 확인
- 비밀번호: 영문소문자 + 숫자 조합, 6~20자
- 비밀번호 확인 기능

### 로그인
- 이메일과 비밀번호로 로그인
- 비밀번호 해싱을 통한 보안

### 페이지
- 홈페이지 (`/`)
- 추천종목 (`/picks`)
- 수익확인 (`/profit`)
- 로그인 (`/login`)
- 회원가입 (`/signup`)

## API 엔드포인트

- `POST /api/check-email`: 이메일 중복 확인
- `POST /api/signup`: 회원가입
- `POST /api/login`: 로그인

## 기술 스택

- **Backend**: FastAPI, SQLAlchemy
- **Database**: MySQL
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **Authentication**: Passlib (bcrypt) 
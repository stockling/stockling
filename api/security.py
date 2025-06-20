import os
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext

# 환경변수 또는 기본값으로 보안 설정
SECRET_KEY = os.getenv("SECRET_KEY", "a_super_secret_key_that_should_be_in_an_env_file_for_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24시간(1일)으로 변경

# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """일반 비밀번호와 해시된 비밀번호를 비교합니다."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """일반 비밀번호를 해시 처리합니다."""
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    """액세스 토큰을 생성합니다."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> str | None:
    """
    액세스 토큰을 디코딩하여 사용자 이메일을 반환합니다.
    유효하지 않으면 None을 반환합니다.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None 
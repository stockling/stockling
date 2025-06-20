import re
from sqlalchemy.orm import Session
from .database import User
from .security import verify_password

# 비밀번호 해싱 설정
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def verify_password(plain_password, hashed_password):
#     """비밀번호 검증"""
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password):
#     """비밀번호 해싱"""
#     return pwd_context.hash(password)

def validate_email(email):
    """이메일 형식 검증"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """비밀번호 형식 검증 (영문 소문자 + 숫자, 길이 : 6자 이상 ~ 20자 이하)"""
    if len(password) < 6 or len(password) > 20:
        return False, "비밀번호는 6~20자 사이여야 합니다."
    
    if not re.match(r'^[a-z0-9]+$', password):
        return False, "비밀번호는 영문 소문자와 숫자만 사용 가능합니다."
    
    if not re.search(r'[a-z]', password):
        return False, "비밀번호는 최소 하나의 영문 소문자를 포함해야 합니다."
    
    if not re.search(r'[0-9]', password):
        return False, "비밀번호는 최소 하나의 숫자를 포함해야 합니다."
    
    return True, "유효한 비밀번호입니다."

def check_email_exists(db: Session, email: str):
    """이메일 중복 확인"""
    user = db.query(User).filter(User.email == email).first()
    return user is not None

def authenticate_user(db: Session, email: str, password: str):
    """사용자 인증"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user 
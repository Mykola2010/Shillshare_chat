from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from app.config import settings
import binascii

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    try:
        password.encode('utf-8').decode('utf-8')
    except UnicodeDecodeError:
        cleaned_password = password.encode('utf-8', errors='replace').decode('utf-8')
        password_bytes = cleaned_password.encode('utf-8')
    else:
        password_bytes = password.encode('utf-8')

    return pwd_context.hash(password_bytes)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        plain_password.encode('utf-8').decode('utf-8')
    except UnicodeDecodeError:
        cleaned_password = plain_password.encode('utf-8', errors='replace').decode('utf-8')
        plain_password_bytes = cleaned_password.encode('utf-8')
    else:
        plain_password_bytes = plain_password.encode('utf-8')

    return pwd_context.verify(plain_password_bytes, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
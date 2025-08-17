from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from .config import settings

_password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return _password_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _password_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_minutes: Optional[int] = None) -> str:
    expire_delta = timedelta(minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(tz=timezone.utc) + expire_delta
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None

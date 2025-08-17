from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..db.session import SessionLocal
from ..core.security import decode_token
from ..models.user import User, UserRole

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(_oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_token(token)
    if payload is None or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    email = payload["sub"]
    user: Optional[User] = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado")
    return user


def require_roles(*roles: UserRole):
    def wrapper(user: User = Depends(get_current_user)) -> User:
        if roles and user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
        return user

    return wrapper

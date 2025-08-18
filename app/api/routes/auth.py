from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from ...schemas.user import UserCreate, UserOut, LoginRequest, Token
from ...models.user import User, UserRole
from ...core.security import hash_password, verify_password, create_access_token
from fastapi.responses import JSONResponse
from ..deps import get_db
from datetime import datetime, timedelta, timezone
from jose import jwt
@router.post("/logout")
def logout():
    resp = JSONResponse(content={"message": "ok"})
    resp.set_cookie(key="access_token", value="", max_age=0, expires=0, path="/")
    return resp
import json
import os

router = APIRouter()
_attempts: dict[str, list[float]] = {}
_lockout_until: dict[str, float] = {}


@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email já cadastrado")
    user = User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        role=user_in.role or UserRole.operador,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    from ...core.config import settings

    ip = request.client.host if request.client else "unknown"
    key_ip = f"ip:{ip}"
    key_user = f"user:{data.email.lower()}"
    now = datetime.now(timezone.utc).timestamp()

    # Verifica lockout
    for key in (key_ip, key_user):
        until = _lockout_until.get(key, 0)
        if now < until:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Tente novamente mais tarde")

    window = settings.LOGIN_WINDOW_SECONDS
    max_attempts = settings.LOGIN_MAX_ATTEMPTS
    lockout = settings.LOGIN_LOCKOUT_SECONDS

    def _register_attempt(k: str, success: bool) -> None:
        arr = _attempts.setdefault(k, [])
        cutoff = now - window
        arr[:] = [t for t in arr if t >= cutoff]
        if not success:
            arr.append(now)
            if len(arr) >= max_attempts:
                _lockout_until[k] = now + lockout
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        _register_attempt(key_ip, False)
        _register_attempt(key_user, False)
        import logging
        logging.getLogger("auth").warning(
            f"login_failed ip={ip} user={data.email}"
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
    _attempts.pop(key_user, None)
    _lockout_until.pop(key_user, None)
    token = create_access_token(subject=user.email)
    # Define cookie HttpOnly para reduzir risco XSS
    response = JSONResponse(content=Token(access_token=token).model_dump())
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False if not __import__('app.core.config', fromlist=['settings']).core.config.settings.COOKIE_SECURE else True,
        samesite="Lax",
        max_age=60 * 60 * 2,
        path="/",
    )
    return response


@router.post("/password/forgot")
def forgot_password(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Responder 200 por segurança
        return {"message": "Se existir, um email de recuperação será enviado."}
    # Gera token de redefinição com expiração curta (30 min)
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    from ...core.config import settings
    token = jwt.encode(
        {"sub": user.email, "purpose": "reset", "exp": expire},
        settings.PASSWORD_RESET_SECRET,
        algorithm="HS256",
    )
    os.makedirs("data", exist_ok=True)
    with open("data/password_reset_tokens.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({"email": user.email, "token": token, "created_at": datetime.utcnow().isoformat()}) + "\n")
    return {"message": "Token de recuperação gerado e salvo em data/password_reset_tokens.jsonl"}


@router.post("/password/reset")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    # Valida token
    try:
        from ...core.config import settings
        payload = jwt.decode(token, settings.PASSWORD_RESET_SECRET, algorithms=["HS256"])  # Deve casar com a geração
    except Exception:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")
    if payload.get("purpose") != "reset" or "sub" not in payload:
        raise HTTPException(status_code=400, detail="Token inválido")
    email = payload["sub"]
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    user.hashed_password = hash_password(new_password)
    db.add(user)
    db.commit()
    return {"message": "Senha redefinida com sucesso"}

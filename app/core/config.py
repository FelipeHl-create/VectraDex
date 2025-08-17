import secrets
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str | None = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    ALGORITHM: str = "HS256"
    DATABASE_URL: str = "sqlite:///./vectradex.db"
    CORS_ORIGINS: str = ""
    COOKIE_SECURE: bool = False
    HSTS_ENABLED: bool = False
    # Segredo separado para fluxo de recuperação de senha
    PASSWORD_RESET_SECRET: str | None = None

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()  # Singleton

# Gerar segredos randômicos em runtime se não forem definidos (evita defaults fracos)
if not settings.SECRET_KEY:
    settings.SECRET_KEY = secrets.token_urlsafe(48)
if not settings.PASSWORD_RESET_SECRET:
    settings.PASSWORD_RESET_SECRET = secrets.token_urlsafe(48)

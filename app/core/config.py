from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    ALGORITHM: str = "HS256"
    DATABASE_URL: str = "sqlite:///./vectradex.db"
    CORS_ORIGINS: str = "*"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()  # Singleton

from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    APP_NAME: str = "AI Interview Assessment"
    DEBUG: bool = False
    API_V1_PREFIX: str = ""

    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/careerai"

    SECRET_KEY: str = "change-me-in-production-use-a-secure-random-key-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    AI_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"
    GEMINI_MODEL: str = "gemini-2.5-flash"

    AZURE_STORAGE_CONNECTION_STRING: str = ""
    AZURE_STORAGE_CONTAINER: str = "careerai-media"

    FRONTEND_URL: str = "http://127.0.0.1:5173"

    RAPIDAPI_KEY: str = ""

    IPQS_API_KEY: str = ""

    ADMIN_SECRET: str = "elevra-admin-secret-change-in-production"

    model_config = {
        "env_file": str(ENV_FILE),
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()
settings = get_settings()
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str = "redis://redis:6379/0"
    SECRET_KEY: str
    MAX_PAGES_PER_JOB: int = 50
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3001"]

    class Config:
        env_file = ".env"

settings = Settings()

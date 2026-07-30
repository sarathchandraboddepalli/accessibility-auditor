from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://auditor:changeme@db:5432/accessibility_auditor"
    REDIS_URL: str = "redis://redis:6379/0"
    SECRET_KEY: str = "dev-secret-key"
    MAX_PAGES_PER_JOB: int = 50

    class Config:
        env_file = ".env"

settings = Settings()

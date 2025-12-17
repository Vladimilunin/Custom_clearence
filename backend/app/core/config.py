from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")
    
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/tamozh_db"
    GEMINI_API_KEY: str | None = None
    OPENROUTER_API_KEY: str | None = None
    SILICONFLOW_API_KEY: str | None = None

    # S3 / R2 Settings
    S3_ENDPOINT: str | None = None
    S3_ACCESS_KEY: str | None = None
    S3_SECRET_KEY: str | None = None
    S3_BUCKET_NAME: str | None = None
    S3_PUBLIC_DOMAIN: str | None = None

settings = Settings()

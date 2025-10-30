from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="ignore"  # Allow extra fields from .env without error
    )

    PROJECT_NAME: str = "DekeData API"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str


settings = Settings()

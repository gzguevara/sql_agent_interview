from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = PROJECT_ROOT / "target-dashboard.db"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    google_api_key: str = Field(..., alias="GOOGLE_API_KEY")
    google_oauth_client_id: str = Field(default="", alias="GOOGLE_OAUTH_CLIENT_ID")
    allowed_emails: str = Field(default="", alias="ALLOWED_EMAILS")
    model_name: str = Field(
        default="google_genai:gemini-2.5-flash-lite",
        alias="MODEL_NAME",
    )
    database_url: str = Field(
        default=f"sqlite:///{DEFAULT_DB_PATH.as_posix()}",
        alias="DATABASE_URL",
    )
    app_name: str = Field(default="target-dashboard-agent", alias="APP_NAME")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")


def get_settings() -> Settings:
    return Settings()

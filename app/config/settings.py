from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    telegram_bot_token: str = ""
    telegram_allowed_user_id: int | None = None
    llm_provider: str = "gemini"
    llm_api_key: str = ""
    llm_model: str = "gemini-2.5-flash"
    database_url: str = "sqlite:///./data/assistant.db"
    timezone: str = "Asia/Kolkata"
    telegram_mode: str = Field(default="polling", pattern="^(polling|webhook)$")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

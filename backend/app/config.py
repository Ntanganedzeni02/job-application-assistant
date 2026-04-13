"""
Central configuration — reads from .env file automatically.
Never hardcode secrets. Access them via get_settings().
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"

    # App
    app_env: str = "development"
    app_port: int = 8000

    # CORS
    allowed_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def origins_list(self) -> list[str]:
        """Parse comma-separated origins into a list."""
        return [o.strip() for o in self.allowed_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings — reads .env once and reuses.
    Use as a FastAPI dependency: settings = Depends(get_settings)
    """
    return Settings()
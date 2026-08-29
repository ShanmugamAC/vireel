"""Application settings loaded from environment variables / .env file."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application configuration.

    Values are loaded from environment variables first, falling back to a
    local `.env` file. See `.env.example` for the full list of variables.
    """

    # App
    APP_NAME: str = "Vireel"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/vireel"

    # Auth / JWT
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OpenAI (Whisper + GPT pipeline)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Video pipeline
    MEDIA_ROOT: str = "media"
    # Path to a Netscape-format cookies.txt exported from a real, logged-in
    # YouTube browser session. YouTube increasingly blocks anonymous requests
    # from datacenter/VPS IPs ("Sign in to confirm you're not a bot"); a
    # cookies file from a real account works around this. Optional — leave
    # blank to fetch without cookies (works for many videos, but not all).
    YT_COOKIES_FILE: str = ""

    # Frontend / CORS
    VITE_API_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:5173"
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

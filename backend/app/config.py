from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )
    API_STR: str = "/api/v1"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    HOST: str
    PORT: int
    DB_USER: str
    DB_NAME: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    FRONTEND_HOST: str

    # LLM API Keys (Optional - can be provided by users via frontend)
    GEMINI_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None

    # Search API Keys
    SERPER_API_KEY: str | None = None  # Google Search via Serper
    TAVILY_API_KEY: str | None = None  # Tavily Search

    # Default LLM Provider
    DEFAULT_LLM_PROVIDER: str = "gemini"  # Options: gemini, openai, anthropic

    # Gemini File Search Configuration (for RAG)
    GEMINI_FILE_SEARCH_MODEL: str = "gemini-2.5-flash"  # Model for RAG queries (gemini-2.5-flash or gemini-2.5-pro)
    GEMINI_STORE_SIZE_LIMIT_GB: int = 20  # Recommended size limit per store
    GEMINI_MAX_FILE_SIZE_MB: int = 100  # Max file size for upload

    SECRET_KEY: str
    EXPIRES_DELTA: int

    # Gmail Email API (Optional)
    TOKEN_FILE: str = "app/service/gmail/token.json"
    CREDENTIALS_FILE: str = "app/service/gmail/credentials.json"
    SCOPES: list[str] = ["https://www.googleapis.com/auth/gmail.send"]
    FROM_EMAIL: str | None = None  # Email address to send from (optional, required only for password reset)
    RESET_TOKEN_EXPIRE_MINUTES: int = 60


settings = Settings()

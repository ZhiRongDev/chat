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
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    # LLM API Keys
    GEMINI_API_KEY: str
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None

    # Search API Keys
    SERPER_API_KEY: str | None = None  # Google Search via Serper
    TAVILY_API_KEY: str | None = None  # Tavily Search

    # Default LLM Provider
    DEFAULT_LLM_PROVIDER: str = "gemini"  # Options: gemini, openai, anthropic

    SECRET_KEY: str
    EXPIRES_DELTA: int


settings = Settings()

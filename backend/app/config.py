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

    # LLM API Keys (Optional - can be provided by users via frontend)
    GEMINI_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None

    # Search API Keys
    SERPER_API_KEY: str | None = None  # Google Search via Serper
    TAVILY_API_KEY: str | None = None  # Tavily Search

    # Default LLM Provider
    DEFAULT_LLM_PROVIDER: str = "gemini"  # Options: gemini, openai, anthropic

    # RAG Configuration
    EMBEDDING_PROVIDER: str | None = None  # Options: openai, google (auto-detected if None)
    EMBEDDING_MODEL: str | None = None  # Model name (uses default if None)
    VECTOR_STORE_TYPE: str = "faiss"  # Options: faiss, chromadb
    CHUNK_SIZE: int = 512  # Token size for document chunks
    CHUNK_OVERLAP: int = 50  # Token overlap between chunks
    RAG_TOP_K: int = 5  # Default number of documents to retrieve
    RAG_MIN_SCORE: float = 0.3  # Minimum relevance score threshold

    SECRET_KEY: str
    EXPIRES_DELTA: int

    # Gmail Email API
    TOKEN_FILE: str = "app/service/gmail/token.json"
    CREDENTIALS_FILE: str = "app/service/gmail/credentials.json"
    SCOPES: list[str] = ["https://www.googleapis.com/auth/gmail.send"]
    FROM_EMAIL: str = "jordan990301@gmail.com"
    RESET_TOKEN_EXPIRE_MINUTES: int = 60


settings = Settings()

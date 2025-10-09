from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )
    API_STR: str = "/api/v1"
    ALGORITHM: str = 'HS256' 
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SECRET_KEY: str
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
    GEMINI_API_KEY: str


settings = Settings()

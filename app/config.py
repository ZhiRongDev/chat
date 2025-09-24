from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )
    API_STR: str = "/api/v1"
    HOST: str
    PORT: int
    DB_USER: str
    DB_NAME: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    FRONTEND_HOST: str

settings = Settings()

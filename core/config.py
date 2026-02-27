from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Resume Analyzer"
    DASHSCOPE_API_KEY: str = "" # To be provided via env variable or .env file
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()

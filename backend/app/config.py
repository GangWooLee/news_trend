from pydantic import BaseSettings

class Settings(BaseSettings):
    NAVER_CLIENT_ID:     str
    NAVER_CLIENT_SECRET: str
    DB_URL:              str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
import os
from pydantic_settings import BaseSettings
from pydantic import computed_field

class Settings(BaseSettings):
    UPLOAD_DIR: str = "/app/uploads"
    
    DATABASE_URL: str

    @computed_field
    @property
    def DATABASE_URL_WITH_DRIVER(self) -> str:
        if self.DATABASE_URL.startswith("postgresql+psycopg://"):
            return self.DATABASE_URL
        return self.DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
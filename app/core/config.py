import os
from pydantic_settings import BaseSettings
from pydantic import computed_field

class Settings(BaseSettings):
    
    DATABASE_URL: str

    @computed_field
    @property
    def DATABASE_URL_WITH_DRIVER(self) -> str:
        return self.DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")

    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
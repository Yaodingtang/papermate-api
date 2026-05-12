from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    # App
    APP_NAME: str = "PaperMate"
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/papermate.db"
    
    # JWT
    JWT_SECRET: str = "papermate-jwt-secret-key-2024"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 168
    
    # AI
    AI_API_KEY: str = ""
    AI_MODEL_ID: str = "astron-code-latest"
    AI_API_URL: str = "https://maas-coding-api.cn-huabei-1.xf-yun.com/v2"
    
    # CORS
    CORS_ORIGINS: str = '["http://localhost:3000","http://localhost:3001"]'
    
    # Debug
    DEBUG: bool = True
    
    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.CORS_ORIGINS)

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

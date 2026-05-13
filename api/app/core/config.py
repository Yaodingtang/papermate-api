from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import json
import os


class Settings(BaseSettings):
    # App
    APP_NAME: str = "PaperMate"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/papermate.db"

    # JWT - 必须从环境变量设置，无默认值
    JWT_SECRET: str = Field(default_factory=lambda: os.getenv("JWT_SECRET", ""))
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 168

    # AI
    AI_API_KEY: str = Field(default_factory=lambda: os.getenv("AI_API_KEY", ""))
    AI_MODEL_ID: str = "astron-code-latest"
    AI_API_URL: str = "https://maas-coding-api.cn-huabei-1.xf-yun.com/v2"

    # CORS
    CORS_ORIGINS: str = '["http://localhost:3000","http://localhost:3001"]'

    # Debug
    DEBUG: bool = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 启动时检查必要的配置
        if not self.JWT_SECRET:
            raise ValueError("JWT_SECRET 必须在环境变量中设置")

    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.CORS_ORIGINS)

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

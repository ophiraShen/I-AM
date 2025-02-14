#I-AM/project/backend/app/config.py
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import validator
from pathlib import Path

class Settings(BaseSettings):
    # 基础配置
    PROJECT_NAME: str = "I-AM API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # API 密钥配置
    DEEPSEEK_API_KEY: Optional[str] = None
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"  # 在生产环境中应该从环境变量获取
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # 数据库配置
    SQLITE_DB_PATH: str = "sqlite+aiosqlite:///./iam.db"
    
    # CORS配置
    BACKEND_CORS_ORIGINS: list = ["*"]  # 在生产环境中应该限制来源
    
    # 文件存储配置
    UPLOAD_DIR: Path = Path("uploads")
    MEDITATION_AUDIO_DIR: Path = UPLOAD_DIR / "meditation"
    
    @validator("MEDITATION_AUDIO_DIR", "UPLOAD_DIR")
    def create_directory(cls, v):
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 
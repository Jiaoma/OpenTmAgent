from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "OpenTmAgent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    DATABASE_URL: str = "sqlite:///./data/opentmagent.db"
    
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_HOURS: int = 24
    
    ADMIN_PASSWORD_MIN_LENGTH: int = 6
    
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama2"
    
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/opentmagent.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

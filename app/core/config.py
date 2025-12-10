from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/biocalc_db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Application
    APP_NAME: str = "BioCalc API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Fossil fuel reference (kg CO₂eq/MJ)
    FOSSIL_REFERENCE_DIESEL: float = 0.0940
    FOSSIL_REFERENCE_GASOLINE: float = 0.0887
    FOSSIL_REFERENCE_GNV: float = 0.0774
    FOSSIL_REFERENCE_WEIGHTED: float = 0.0867  # Média ponderada

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "biocalc.suporte@gmail.com"
    SMTP_PASSWORD: str = "zpra lnaz ndvc rycn"
    EMAILS_FROM_EMAIL: str = "noreply@biocalc.com"
    EMAILS_FROM_NAME: str = "BioCalc"

    FRONTEND_URL: str = "http://localhost:3000"

    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

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
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://carecontinuum:carecontinuum_dev_pass@localhost:5432/carecontinuum"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]
    
    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "noreply@carecontinuum.com"
    
    # SMS
    SMS_PROVIDER: Optional[str] = None
    SMS_API_KEY: Optional[str] = None
    
    # Hospital Info
    HOSPITAL_NAME: str = "CareContinuum Hospital"
    HOSPITAL_ADDRESS: str = "123 Healthcare Ave, Medical City, HC 12345"
    HOSPITAL_PHONE: str = "+1-555-HEALTH"
    
    # Scheduling limits
    MAX_RESCHEDULE_ATTEMPTS: int = 2
    MAX_REMINDER_ATTEMPTS: int = 3
    MAX_CONTACT_ATTEMPTS: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

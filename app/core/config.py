"""
Application Configuration
Converted from Django settings.py
"""
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
from pathlib import Path
import secrets


class Settings(BaseSettings):
    """Application settings"""
    
    # Basic Settings
    PROJECT_NAME: str = "Apex Workspace Management"
    VERSION: str = "2.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    
    # Server Settings
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    FRONTEND_COMPATIBILITY: bool = Field(default=True, env="FRONTEND_COMPATIBILITY")  # Run on port 5001 for frontend compatibility
    ALLOWED_HOSTS: List[str] = Field(default=["*"], env="ALLOWED_HOSTS")
    
    # Database Settings
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./test.db",
        env="DATABASE_URL"
    )
    DATABASE_ECHO: bool = Field(default=False, env="DATABASE_ECHO")
    
    # Redis Settings
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # JWT Settings
    JWT_SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hour
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7     # 7 days
    
    # Email Settings
    EMAIL_BACKEND: str = Field(default="console", env="EMAIL_BACKEND")  # console, smtp
    SMTP_HOST: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USE_TLS: bool = Field(default=True, env="SMTP_USE_TLS")
    SMTP_USERNAME: str = Field(default="", env="SMTP_USERNAME")
    SMTP_PASSWORD: str = Field(default="", env="SMTP_PASSWORD")
    DEFAULT_FROM_EMAIL: str = Field(default="noreply@apex.com", env="DEFAULT_FROM_EMAIL")
    
    # Frontend Settings
    FRONTEND_URL: str = Field(default="http://localhost:3000", env="FRONTEND_URL")
    
    # File Storage Settings
    UPLOAD_DIR: Path = Field(default=Path("uploads"))
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024)  # 10MB
    
    # AWS S3 Settings (Optional)
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    AWS_S3_BUCKET_NAME: Optional[str] = Field(default=None, env="AWS_S3_BUCKET_NAME")
    AWS_S3_REGION: str = Field(default="us-east-1", env="AWS_S3_REGION")
    
    # External API Keys
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    GOOGLE_MAPS_API_KEY: Optional[str] = Field(default=None, env="GOOGLE_MAPS_API_KEY")
    TWILIO_ACCOUNT_SID: Optional[str] = Field(default=None, env="TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: Optional[str] = Field(default=None, env="TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER: Optional[str] = Field(default=None, env="TWILIO_PHONE_NUMBER")
    SENDGRID_API_KEY: Optional[str] = Field(default=None, env="SENDGRID_API_KEY")
    
    # Security Settings
    PASSWORD_RESET_TIMEOUT: int = 7200  # 2 hours in seconds
    MAX_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_DURATION: int = 30  # minutes
    
    # Pagination Settings
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Background Tasks
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2", env="CELERY_RESULT_BACKEND")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @validator("UPLOAD_DIR", pre=True)
    def create_upload_dir(cls, v):
        upload_dir = Path(v)
        upload_dir.mkdir(parents=True, exist_ok=True)
        return upload_dir
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()


# Database URL for Alembic
def get_database_url() -> str:
    """Get database URL for Alembic migrations"""
    return settings.DATABASE_URL.replace("+asyncpg", "")
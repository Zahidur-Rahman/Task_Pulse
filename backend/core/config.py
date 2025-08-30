import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator, Field
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"✅ Loaded .env from: {env_path}")
else:
    print(f"⚠️  .env file not found at: {env_path}")
    # Try to load from current directory
    load_dotenv()


class Settings(BaseSettings):
    # Project Information
    PROJECT_TITLE: str = "Task Pulse - Task Management API"
    PROJECT_VERSION: str = "1.0.0"
    PROJECT_DESCRIPTION: str = "A robust task management API built with FastAPI"
    API_V1_STR: str = "/api/v1"
    
    # Database Configuration
    POSTGRES_USER: str = Field(..., env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(..., env="POSTGRES_PASSWORD")
    POSTGRES_SERVER: str = Field(default="localhost", env="POSTGRES_SERVER")
    POSTGRES_PORT: int = Field(default=5432, env="POSTGRES_PORT")
    POSTGRES_DB: str = Field(..., env="POSTGRES_DB")
    
    # Security Configuration
    SECRET_KEY: str = Field(default="your_super_secret_key_here_make_it_at_least_32_characters_long_2024", env="SUPER_SECRET", min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440, env="ACCESS_TOKEN_EXPIRE_MINUTES")  # 24 hours
    
    # Cookie Configuration
    COOKIE_NAME: str = "access_token"
    COOKIE_DOMAIN: Optional[str] = None  # Allow cookies across all domains for development
    COOKIE_SECURE: bool = Field(default=False, env="COOKIE_SECURE")  # True in production with HTTPS
    COOKIE_SAMESITE: str = Field(default="lax", env="COOKIE_SAMESITE")  # "lax" for development
    
    @property
    def COOKIE_MAX_AGE(self) -> int:
        return 60 * self.ACCESS_TOKEN_EXPIRE_MINUTES
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3001", 
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://192.168.0.106:3000",
            "http://0.0.0.0:3000",
            "*"  # Allow all origins for development
        ],
        env="BACKEND_CORS_ORIGINS"
    )
    
    # Redis Configuration (Optional - for caching and sessions)
    REDIS_URL: Optional[str] = Field(default=None, env="REDIS_URL")
    
    # Environment
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # Admin Setup Tokens
    SETUP_TOKEN: str = Field(default="TASK_PULSE_SETUP_2024", env="SETUP_TOKEN")
    ADMIN_PROMOTION_CODE: str = Field(default="ADMIN_PROMOTION_2024", env="ADMIN_PROMOTION_CODE")
    DIRECT_ADMIN_REG_CODE: str = Field(default="DIRECT_ADMIN_REG_2024", env="DIRECT_ADMIN_REG_CODE")
    
    # Database URL
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Validation
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    @field_validator("POSTGRES_PORT")
    @classmethod
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v
    
    model_config = {
        "extra": "allow",
        "env_file": ".env",
        "case_sensitive": True
    }


# Global settings instance
settings = Settings()


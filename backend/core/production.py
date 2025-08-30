import os
from typing import List
from core.config import settings


class ProductionConfig:
    """Production-specific configuration."""
    
    # Security Settings
    SECURE_HEADERS = {
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_REQUESTS = 100  # requests per minute
    RATE_LIMIT_WINDOW = 60     # seconds
    
    # CORS Settings for Production
    CORS_ORIGINS = [
        "https://yourdomain.com",
        "https://www.yourdomain.com",
        "https://app.yourdomain.com"
    ]
    
    # Database Connection Pool
    DB_POOL_SIZE = 20
    DB_MAX_OVERFLOW = 30
    DB_POOL_RECYCLE = 3600  # 1 hour
    DB_POOL_PRE_PING = True
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE_MAX_SIZE = 100 * 1024 * 1024  # 100MB
    LOG_FILE_BACKUP_COUNT = 10
    
    # Monitoring
    METRICS_ENABLED = True
    HEALTH_CHECK_INTERVAL = 30  # seconds
    
    # Cache Settings
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    CACHE_TTL = 3600  # 1 hour
    
    # Session Settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "strict"
    
    # JWT Settings
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Shorter for production
    JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    # File Upload
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES = [".jpg", ".jpeg", ".png", ".pdf", ".doc", ".docx"]
    
    # Email Settings (if implementing email features)
    SMTP_HOST = os.getenv("SMTP_HOST")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    SMTP_USE_TLS = True
    
    # External Services
    SENTRY_DSN = os.getenv("SENTRY_DSN")
    NEW_RELIC_LICENSE_KEY = os.getenv("NEW_RELIC_LICENSE_KEY")
    
    # Performance
    WORKER_PROCESSES = 4
    WORKER_CLASS = "uvicorn.workers.UvicornWorker"
    MAX_REQUESTS = 1000
    MAX_REQUESTS_JITTER = 100
    
    @classmethod
    def get_cors_origins(cls) -> List[str]:
        """Get CORS origins based on environment."""
        if os.getenv("ENVIRONMENT") == "production":
            return cls.CORS_ORIGINS
        return settings.BACKEND_CORS_ORIGINS
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get database URL with production optimizations."""
        base_url = settings.DATABASE_URL
        
        # Add connection pool parameters for production
        if "?" in base_url:
            base_url += "&"
        else:
            base_url += "?"
        
        base_url += f"pool_size={cls.DB_POOL_SIZE}&"
        base_url += f"max_overflow={cls.DB_MAX_OVERFLOW}&"
        base_url += f"pool_recycle={cls.DB_POOL_RECYCLE}&"
        base_url += "pool_pre_ping=true"
        
        return base_url


class DevelopmentConfig:
    """Development-specific configuration."""
    
    # Security Settings (less strict for development)
    SECURE_HEADERS = {}
    
    # Rate Limiting (disabled for development)
    RATE_LIMIT_ENABLED = False
    
    # CORS Settings for Development
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ]
    
    # Database Connection Pool (smaller for development)
    DB_POOL_SIZE = 5
    DB_MAX_OVERFLOW = 10
    DB_POOL_RECYCLE = 300  # 5 minutes
    DB_POOL_PRE_PING = True
    
    # Logging (more verbose for development)
    LOG_LEVEL = "DEBUG"
    LOG_FILE_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_FILE_BACKUP_COUNT = 3
    
    # Monitoring (disabled for development)
    METRICS_ENABLED = False
    
    # Cache Settings (local for development)
    REDIS_URL = "redis://localhost:6379"
    CACHE_TTL = 300  # 5 minutes
    
    # Session Settings (less strict for development)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "lax"
    
    # JWT Settings (longer for development)
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS = 30
    
    # File Upload (smaller for development)
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_FILE_TYPES = [".jpg", ".jpeg", ".png", ".pdf"]
    
    # Performance (single process for development)
    WORKER_PROCESSES = 1
    WORKER_CLASS = "uvicorn.workers.UvicornWorker"
    MAX_REQUESTS = 100
    MAX_REQUESTS_JITTER = 10


def get_config():
    """Get configuration based on environment."""
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return ProductionConfig()
    else:
        return DevelopmentConfig()


# Global config instance
config = get_config() 
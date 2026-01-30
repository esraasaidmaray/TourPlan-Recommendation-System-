"""
AI Travel Planner - Configuration Management
===========================================
Centralized configuration for production deployment
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    app_name: str = Field(default="AI Travel Planner", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=4, env="WORKERS")
    
    # Database
    database_path: str = Field(default="poi.db", env="DATABASE_PATH")
    
    # Security
    secret_key: str = Field(default="change-me-in-production", env="SECRET_KEY")
    api_key: Optional[str] = Field(default=None, env="API_KEY")
    
    # CORS
    allowed_origins: List[str] = Field(default=["*"], env="ALLOWED_ORIGINS")
    allowed_methods: List[str] = Field(default=["GET", "POST", "PUT", "DELETE", "OPTIONS"], env="ALLOWED_METHODS")
    allowed_headers: List[str] = Field(default=["*"], env="ALLOWED_HEADERS")
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_burst: int = Field(default=100, env="RATE_LIMIT_BURST")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    log_file_path: str = Field(default="app.log", env="LOG_FILE_PATH")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Validation
def validate_settings():
    """Validate critical settings"""
    if settings.secret_key == "change-me-in-production":
        raise ValueError("SECRET_KEY must be changed in production!")
    
    if not os.path.exists(settings.database_path):
        raise FileNotFoundError(f"Database file not found: {settings.database_path}")
    
    return True

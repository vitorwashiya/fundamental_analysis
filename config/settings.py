"""
Configuration settings for the Fundamental Analysis API
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str = Field(default="sqlite:///./fundamental_analysis.db")
    
    # API
    api_v1_str: str = Field(default="/api/v1")
    project_name: str = Field(default="Fundamental Analysis API")
    version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    
    # Security
    secret_key: str = Field(default="your-secret-key-change-this")
    
    # Logging
    log_level: str = Field(default="INFO")
    
    # Data update settings
    fundamentus_cache_hours: int = Field(default=24)
    update_on_startup: bool = Field(default=False)
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

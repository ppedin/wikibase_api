"""
Configuration settings for the application.

This module defines the configuration settings for the application,
including environment variables and defaults.
"""
import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # API configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "XML Schema Validation API"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    
    # Logging configuration
    LOG_LEVEL: str = "INFO"
    
    class Config:
        """Pydantic config for settings."""
        env_file = ".env"
        case_sensitive = True


# Create a singleton instance of the settings
settings = Settings()


def get_settings() -> Settings:
    """Get the singleton instance of settings."""
    return settings
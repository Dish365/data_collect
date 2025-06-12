"""
Configuration settings for the FastAPI analytics engine.
"""

from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path

# Get the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')

# Import Django settings
import django
django.setup()

from django.conf import settings as django_settings

class Settings(BaseSettings):
    """Settings for the FastAPI application."""
    
    PROJECT_NAME: str = "Research Analytics Engine"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Use Django's database settings
    DATABASE_URL: str = str(django_settings.DATABASES['default'])
    
    # Security
    SECRET_KEY: str = django_settings.SECRET_KEY
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS - Use Django's CORS settings
    BACKEND_CORS_ORIGINS: List[str] = django_settings.CORS_ALLOWED_ORIGINS
    
    # Analytics
    MAX_BATCH_SIZE: int = 1000
    ANALYTICS_TIMEOUT: int = 300  # 5 minutes
    
    class Config:
        env_file = ".env"

settings = Settings() 
"""
Configuration settings for the FastAPI analytics engine.
"""

from pydantic_settings import BaseSettings
from typing import List
import os
import sys
from pathlib import Path

# Add the backend directory to Python path to access Django core
# From analytics/core/config.py: .parent -> analytics/core/, .parent -> analytics/, .parent -> backend/
current_file = Path(__file__).resolve()
backend_dir = current_file.parent.parent.parent  # Go up 3 levels: core/ -> analytics/ -> backend/
sys.path.insert(0, str(backend_dir))

# Debug: Print paths to verify
print(f"Current file: {current_file}")
print(f"Backend dir: {backend_dir}")
print(f"Core settings path: {backend_dir / 'core' / 'settings'}")
print(f"Backend dir exists: {backend_dir.exists()}")
print(f"Core settings exists: {(backend_dir / 'core' / 'settings').exists()}")

# Change working directory to backend so Django can find core.settings
original_cwd = os.getcwd()
os.chdir(backend_dir)
print(f"Changed working directory from {original_cwd} to {os.getcwd()}")

# Get the Django settings module - pointing to the correct Django core location
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')

# Import Django settings
import django
django.setup()

from django.conf import settings as django_settings

def get_database_url_from_django():
    """Convert Django database settings to SQLAlchemy URL format."""
    db_config = django_settings.DATABASES['default']
    
    if db_config['ENGINE'] == 'django.db.backends.sqlite3':
        # For SQLite, use the database file path
        db_path = Path(db_config['NAME'])
        # Make sure the path is absolute
        if not db_path.is_absolute():
            db_path = backend_dir / db_path
        return f"sqlite:///{db_path}"
    elif db_config['ENGINE'] == 'django.db.backends.postgresql':
        return f"postgresql://{db_config.get('USER', '')}:{db_config.get('PASSWORD', '')}@{db_config.get('HOST', 'localhost')}:{db_config.get('PORT', 5432)}/{db_config.get('NAME', '')}"
    elif db_config['ENGINE'] == 'django.db.backends.mysql':
        return f"mysql://{db_config.get('USER', '')}:{db_config.get('PASSWORD', '')}@{db_config.get('HOST', 'localhost')}:{db_config.get('PORT', 3306)}/{db_config.get('NAME', '')}"
    else:
        raise ValueError(f"Unsupported database engine: {db_config['ENGINE']}")

class Settings(BaseSettings):
    """Settings for the FastAPI application."""
    
    PROJECT_NAME: str = "Research Analytics Engine"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Use Django's database settings converted to SQLAlchemy format
    DATABASE_URL: str = get_database_url_from_django()
    
    # Security - Use Django's secret key
    SECRET_KEY: str = django_settings.SECRET_KEY
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS - Use Django's CORS settings
    BACKEND_CORS_ORIGINS: List[str] = getattr(django_settings, 'CORS_ALLOWED_ORIGINS', [])
    
    # Analytics
    MAX_BATCH_SIZE: int = 1000
    ANALYTICS_TIMEOUT: int = 300  # 5 minutes
    
    class Config:
        env_file = ".env"

settings = Settings() 
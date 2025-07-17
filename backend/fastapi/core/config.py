"""
Configuration settings for the FastAPI analytics engine.
"""

import os
from typing import List

class Settings:
    PROJECT_NAME: str = "Research Analytics Engine"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    # Django database settings
    DJANGO_SETTINGS_MODULE: str = "django_core.settings.development"
    
    # Analytics settings
    MAX_ANALYSIS_ROWS: int = 10000
    DEFAULT_SAMPLE_SIZE: int = 1000
    
    # File paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DJANGO_PROJECT_DIR: str = os.path.join(BASE_DIR, "..")

settings = Settings() 
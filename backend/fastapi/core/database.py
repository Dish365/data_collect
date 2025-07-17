"""
Database connection module for FastAPI analytics engine.
Connects to Django's database to access collected data.
"""

import os
import sys
import django
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Add Django project to Python path
DJANGO_PROJECT_DIR = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, DJANGO_PROJECT_DIR)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_core.settings.development')

# Initialize Django
django.setup()

# Import Django models after setup
from django.db import connection
from django.conf import settings
from projects.models import Project
from forms.models import Question
from responses.models import Response, Respondent, ResponseType
from authentication.models import User
from analytics_results.models import AnalyticsResult

# Create SQLAlchemy engine using Django's database settings
def get_django_db_url():
    """Get database URL from Django settings"""
    db_settings = settings.DATABASES['default']
    
    if db_settings['ENGINE'] == 'django.db.backends.sqlite3':
        return f"sqlite:///{db_settings['NAME']}"
    elif db_settings['ENGINE'] == 'django.db.backends.postgresql':
        return f"postgresql://{db_settings['USER']}:{db_settings['PASSWORD']}@{db_settings['HOST']}:{db_settings['PORT']}/{db_settings['NAME']}"
    elif db_settings['ENGINE'] == 'django.db.backends.mysql':
        return f"mysql://{db_settings['USER']}:{db_settings['PASSWORD']}@{db_settings['HOST']}:{db_settings['PORT']}/{db_settings['NAME']}"
    else:
        raise ValueError(f"Unsupported database engine: {db_settings['ENGINE']}")

# Create SQLAlchemy engine
engine = create_engine(
    get_django_db_url(),
    poolclass=StaticPool,
    connect_args={"check_same_thread": False} if "sqlite" in get_django_db_url() else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """Initialize database connection"""
    # Test connection using Django's connection instead of SQLAlchemy
    try:
        from django.db import connection
        from asgiref.sync import sync_to_async
        
        # Use sync_to_async to run Django operations in async context
        @sync_to_async
        def test_connection():
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        
        await test_connection()
        print("✅ Database connection established")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise

# Django database connection utilities
def get_django_db_connection():
    """Get Django database connection"""
    return connection

def execute_django_query(query, params=None):
    """Execute a raw SQL query using Django's connection"""
    with connection.cursor() as cursor:
        cursor.execute(query, params or [])
        return cursor.fetchall()

# Data access utilities
async def get_project_data(project_id: str):
    """Get all data for a specific project"""
    from asgiref.sync import sync_to_async
    
    @sync_to_async
    def _get_project_data():
        try:
            # Get project
            project = Project.objects.get(id=project_id)
            
            # Get all responses for this project
            responses = Response.objects.filter(project=project).select_related(
                'question', 'respondent', 'response_type'
            )
            
            # Convert to list of dictionaries for analysis
            data = []
            for response in responses:
                data.append({
                    'response_id': str(response.response_id),
                    'question_text': response.question.question_text,
                    'response_type': response.response_type.name,
                    'response_value': response.response_value,
                    'numeric_value': float(response.numeric_value) if response.numeric_value else None,
                    'datetime_value': response.datetime_value.isoformat() if response.datetime_value else None,
                    'choice_selections': response.choice_selections,
                    'respondent_id': response.respondent.respondent_id,
                    'collected_at': response.collected_at.isoformat(),
                    'collected_by': response.collected_by.username if response.collected_by else None,
                    'location_data': response.location_data,
                    'device_info': response.device_info,
                    'is_validated': response.is_validated,
                    'data_quality_score': response.data_quality_score,
                })
            
            return data
        except Project.DoesNotExist:
            return []
        except Exception as e:
            print(f"Error getting project data: {e}")
            return []
    
    return await _get_project_data()

async def get_project_stats(project_id: str):
    """Get basic statistics for a project"""
    from asgiref.sync import sync_to_async
    
    @sync_to_async
    def _get_project_stats():
        try:
            project = Project.objects.get(id=project_id)
            
            stats = {
                'project_name': project.name,
                'total_questions': project.questions.count(),
                'total_responses': project.responses.count(),
                'unique_respondents': project.responses.values('respondent_id').distinct().count(),
                'analytics_results': project.analytics_results.count(),
                'team_members': project.get_team_members_count(),
                'created_at': project.created_at.isoformat(),
                'last_activity': project.updated_at.isoformat(),
            }
            
            return stats
        except Project.DoesNotExist:
            return None
        except Exception as e:
            print(f"Error getting project stats: {e}")
            return None
    
    return await _get_project_stats() 
# Frontend Integration Guide
## Kivy GUI to Django Backend Connection

This guide provides comprehensive instructions for connecting the Kivy mobile application to the Django backend API.

---

## 🛠️ Backend Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Git (for cloning the repository)

### Step 1: Navigate to Backend Directory
```bash
cd backend
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# If you encounter any issues, try upgrading pip first:
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Database Setup
```bash
# Run database migrations
python manage.py makemigrations
python manage.py migrate

# Create a superuser for admin access
python manage.py createsuperuser
```

### Step 5: Start Development Server
```bash
# Start the Django development server
python manage.py runserver

# The server will start at http://localhost:8000
# Admin interface: http://localhost:8000/admin/
# API documentation: http://localhost:8000/swagger/
```

### Step 6: Verify Installation
1. Open your browser and go to `http://localhost:8000/admin/`
2. Log in with your superuser credentials
3. Check that all apps are properly installed
4. Visit `http://localhost:8000/swagger/` to see the API documentation

### Troubleshooting Common Issues

#### Issue: Port 8000 already in use
```bash
# Kill the process using port 8000
# On Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# On macOS/Linux:
lsof -ti:8000 | xargs kill -9

# Or use a different port:
python manage.py runserver 8001
```

#### Issue: Database connection errors
```bash
# Reset database (WARNING: This will delete all data)
python manage.py flush

# Or recreate the database:
rm db.sqlite3  # Delete existing database
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

#### Issue: Missing dependencies
```bash
# Update pip and try again
pip install --upgrade pip
pip install -r requirements.txt

# If specific packages fail, install them individually:
pip install django
pip install djangorestframework
pip install django-cors-headers
# ... add other packages as needed
```

### Environment Variables (Optional)
Create a `.env` file in the backend directory for custom configurations:
```bash
# .env file
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## �� Table of Contents
1. [Backend API Overview](#backend-api-overview)
2. [Authentication System](#authentication-system)
3. [API Endpoints Reference](#api-endpoints-reference)
4. [Data Models & Serialization](#data-models--serialization)
5. [Offline-First Architecture](#offline-first-architecture)
6. [Sync Service Implementation](#sync-service-implementation)
7. [Error Handling & Network Issues](#error-handling--network-issues)
8. [Testing & Development](#testing--development)
9. [Production Deployment](#production-deployment)

---

## 🚀 Backend API Overview

### Base URL Configuration
```python
# Development
BASE_URL = "http://localhost:8000/api/v1"

# Production (update this for your production server)
BASE_URL = "https://your-domain.com/api/v1"
```

### API Documentation
- **Swagger UI**: `http://localhost:8000/swagger/`
- **ReDoc**: `http://localhost:8000/redoc/`
- **Admin Interface**: `http://localhost:8000/admin/`

### Authentication Method
- **Token-based authentication** using Django REST Framework tokens
- **Header**: `Authorization: Token <your_token>`
- **Content-Type**: `application/json`

---

## 🔐 Authentication System

### Login Flow
```python
# Example login request
import requests

def login(username, password):
    response = requests.post(
        f"{BASE_URL}/auth/login/",
        json={
            "username": username,
            "password": password
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('token')
        return token
    return None
```

### Token Management
```python
# Store token securely
from kivy.storage.jsonstore import JsonStore

class AuthService:
    def __init__(self):
        self.store = JsonStore('auth.json')
        self.token = None
    
    def save_token(self, token, username):
        self.store.put('auth', token=token, username=username)
    
    def get_token(self):
        if self.store.exists('auth'):
            return self.store.get('auth').get('token')
        return None
    
    def logout(self):
        self.token = None
        if self.store.exists('auth'):
            self.store.delete('auth')
```

### API Request with Authentication
```python
def make_authenticated_request(endpoint, method='GET', data=None):
    token = auth_service.get_token()
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }
    
    if method == 'GET':
        response = requests.get(f"{BASE_URL}/{endpoint}", headers=headers)
    elif method == 'POST':
        response = requests.post(f"{BASE_URL}/{endpoint}", json=data, headers=headers)
    elif method == 'PUT':
        response = requests.put(f"{BASE_URL}/{endpoint}", json=data, headers=headers)
    elif method == 'DELETE':
        response = requests.delete(f"{BASE_URL}/{endpoint}", headers=headers)
    
    return response
```

---

## 📡 API Endpoints Reference

### Authentication Endpoints
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/api/auth/register/` | User registration | `{username, email, password, password2, role}` | `{token, user_data}` |
| POST | `/api/auth/login/` | User login | `{username, password}` | `{token, user_data}` |
| POST | `/api/auth/logout/` | User logout | `{}` | `{message}` |
| GET | `/api/auth/profile/` | Get user profile | - | `{user_data}` |
| PUT | `/api/auth/change-password/` | Change password | `{old_password, new_password, new_password2}` | `{message}` |

### Project Management
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/api/v1/projects/` | List projects | - | `[{project_data}]` |
| POST | `/api/v1/projects/` | Create project | `{name, description, settings, metadata}` | `{project_data}` |
| GET | `/api/v1/projects/{id}/` | Get project details | - | `{project_data}` |
| PUT | `/api/v1/projects/{id}/` | Update project | `{name, description, settings, metadata}` | `{project_data}` |
| DELETE | `/api/v1/projects/{id}/` | Delete project | - | `{}` |

### Form/Question Management
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/api/v1/questions/` | List questions | - | `[{question_data}]` |
| POST | `/api/v1/questions/` | Create question | `{project, question_text, question_type, is_required, options, validation_rules, order_index}` | `{question_data}` |
| GET | `/api/v1/questions/{id}/` | Get question details | - | `{question_data}` |
| PUT | `/api/v1/questions/{id}/` | Update question | `{question_text, question_type, is_required, options, validation_rules, order_index}` | `{question_data}` |
| DELETE | `/api/v1/questions/{id}/` | Delete question | - | `{}` |

### Response Collection
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/api/v1/responses/` | List responses | - | `[{response_data}]` |
| POST | `/api/v1/responses/` | Create response | `{project, question, respondent_id, response_value, metadata, location_data}` | `{response_data}` |
| GET | `/api/v1/responses/{id}/` | Get response details | - | `{response_data}` |
| PUT | `/api/v1/responses/{id}/` | Update response | `{response_value, metadata, location_data}` | `{response_data}` |
| DELETE | `/api/v1/responses/{id}/` | Delete response | - | `{}` |

### Analytics Results
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/api/analytics/analytics-results/` | List analytics results | - | `[{analytics_data}]` |
| GET | `/api/analytics/analytics-results/{id}/` | Get analytics details | - | `{analytics_data}` |
| POST | `/api/analytics/analytics-results/{id}/regenerate/` | Regenerate analytics | - | `{message}` |

### Sync Management
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/api/sync/sync-queue/` | List sync queue items | - | `[{sync_data}]` |
| POST | `/api/sync/sync-queue/process_pending/` | Process pending items | - | `{message, total_processed}` |
| POST | `/api/sync/sync-queue/{id}/retry/` | Retry failed sync | - | `{message}` |

---

## 📊 Data Models & Serialization

### Project Model
```python
{
    "id": "uuid",
    "name": "string",
    "description": "string",
    "created_by": "user_uuid",
    "created_by_details": {
        "id": "uuid",
        "email": "string",
        "username": "string",
        "role": "string"
    },
    "created_at": "datetime",
    "updated_at": "datetime",
    "sync_status": "string",
    "cloud_id": "string",
    "settings": "json",
    "metadata": "json",
    "question_count": "integer",
    "response_count": "integer"
}
```

### Question Model
```python
{
    "id": "uuid",
    "project": "project_uuid",
    "project_details": {
        "id": "uuid",
        "name": "string"
    },
    "question_text": "string",
    "question_type": "string",  # numeric, text, choice, scale, date, location
    "is_required": "boolean",
    "options": "json",  # For multiple choice questions
    "validation_rules": "json",
    "order_index": "integer",
    "created_at": "datetime",
    "sync_status": "string"
}
```

### Response Model
```python
{
    "id": "uuid",
    "project": "project_uuid",
    "project_details": {
        "id": "uuid",
        "name": "string"
    },
    "question": "question_uuid",
    "question_details": {
        "id": "uuid",
        "question_text": "string",
        "question_type": "string"
    },
    "respondent_id": "string",
    "response_value": "string",
    "metadata": "json",
    "collected_by": "user_uuid",
    "collected_by_details": {
        "id": "uuid",
        "email": "string",
        "username": "string"
    },
    "collected_at": "datetime",
    "location_data": "json",
    "sync_status": "string"
}
```

### User Model
```python
{
    "id": "uuid",
    "email": "string",
    "username": "string",
    "first_name": "string",
    "last_name": "string",
    "role": "string",  # admin, researcher, field_worker
    "is_active": "boolean",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

---

## 📱 Offline-First Architecture

### Local Database Schema
```sql
-- Projects table
CREATE TABLE projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_by TEXT,
    created_at TEXT,
    updated_at TEXT,
    sync_status TEXT DEFAULT 'pending',
    cloud_id TEXT,
    settings TEXT,
    metadata TEXT
);

-- Questions table
CREATE TABLE questions (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    question_text TEXT NOT NULL,
    question_type TEXT NOT NULL,
    is_required INTEGER DEFAULT 1,
    options TEXT,
    validation_rules TEXT,
    order_index INTEGER DEFAULT 0,
    created_at TEXT,
    sync_status TEXT DEFAULT 'pending',
    FOREIGN KEY (project_id) REFERENCES projects (id)
);

-- Responses table
CREATE TABLE responses (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    question_id TEXT,
    respondent_id TEXT NOT NULL,
    response_value TEXT,
    metadata TEXT,
    collected_by TEXT,
    collected_at TEXT,
    location_data TEXT,
    sync_status TEXT DEFAULT 'pending',
    FOREIGN KEY (project_id) REFERENCES projects (id),
    FOREIGN KEY (question_id) REFERENCES questions (id)
);

-- Sync queue table
CREATE TABLE sync_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    record_id TEXT NOT NULL,
    operation TEXT NOT NULL,
    data TEXT,
    created_at TEXT,
    attempts INTEGER DEFAULT 0,
    last_attempt TEXT,
    status TEXT DEFAULT 'pending'
);
```

### Offline Data Management
```python
class DatabaseService:
    def __init__(self):
        self.conn = sqlite3.connect('research_data.db')
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        cursor = self.conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                created_by TEXT,
                created_at TEXT,
                updated_at TEXT,
                sync_status TEXT DEFAULT 'pending',
                cloud_id TEXT,
                settings TEXT,
                metadata TEXT
            )
        ''')
        
        # Add other table creation statements...
        self.conn.commit()
    
    def save_project_locally(self, project_data):
        """Save project to local database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO projects 
            (id, name, description, created_by, created_at, updated_at, sync_status, cloud_id, settings, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            project_data['id'],
            project_data['name'],
            project_data.get('description'),
            project_data.get('created_by'),
            project_data.get('created_at'),
            project_data.get('updated_at'),
            'pending',
            project_data.get('cloud_id'),
            json.dumps(project_data.get('settings', {})),
            json.dumps(project_data.get('metadata', {}))
        ))
        self.conn.commit()
```

---

## 🔄 Sync Service Implementation

### Automatic Sync
```python
class SyncService:
    def __init__(self):
        self.base_url = BASE_URL
        self.sync_interval = 300  # 5 minutes
        self.is_syncing = False
    
    def start_auto_sync(self, db_service):
        """Start automatic sync with interval"""
        self.db_service = db_service
        Clock.schedule_interval(self.sync, self.sync_interval)
    
    def sync(self, dt=None):
        """Sync local data with backend"""
        if self.is_syncing:
            return
        
        self.is_syncing = True
        try:
            # Get pending items from sync queue
            cursor = self.db_service.conn.cursor()
            cursor.execute('''
                SELECT * FROM sync_queue 
                WHERE status = 'pending' 
                ORDER BY created_at ASC
            ''')
            pending_items = cursor.fetchall()
            
            for item in pending_items:
                self._process_sync_item(item)
                
        except Exception as e:
            print(f"Sync error: {str(e)}")
        finally:
            self.is_syncing = False
    
    def _process_sync_item(self, item):
        """Process a single sync queue item"""
        try:
            data = json.loads(item['data'])
            endpoint = f"{self.base_url}/{item['table_name']}/"
            
            headers = {
                'Authorization': f'Token {auth_service.get_token()}',
                'Content-Type': 'application/json'
            }
            
            if item['operation'] == 'create':
                response = requests.post(endpoint, json=data, headers=headers)
            elif item['operation'] == 'update':
                response = requests.put(f"{endpoint}{item['record_id']}/", json=data, headers=headers)
            elif item['operation'] == 'delete':
                response = requests.delete(f"{endpoint}{item['record_id']}/", headers=headers)
            
            if response.status_code in (200, 201, 204):
                # Mark as completed
                self._update_sync_status(item['id'], 'completed')
            else:
                # Increment attempt count
                self._increment_attempts(item['id'])
                
        except Exception as e:
            print(f"Error processing sync item: {str(e)}")
            self._increment_attempts(item['id'])
    
    def queue_sync(self, table_name, record_id, operation, data):
        """Queue an item for sync"""
        cursor = self.db_service.conn.cursor()
        cursor.execute('''
            INSERT INTO sync_queue (table_name, record_id, operation, data, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (table_name, record_id, operation, json.dumps(data), datetime.now().isoformat()))
        self.db_service.conn.commit()
```

### Manual Sync Triggers
```python
def sync_on_network_available(self):
    """Trigger sync when network becomes available"""
    if self._check_network_connectivity():
        self.sync()

def sync_on_app_resume(self):
    """Trigger sync when app resumes"""
    self.sync()

def force_sync(self):
    """Force immediate sync"""
    self.sync()
```

---

## ⚠️ Error Handling & Network Issues

### Network Error Handling
```python
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

def make_api_request(endpoint, method='GET', data=None, timeout=30):
    """Make API request with proper error handling"""
    try:
        headers = {
            'Authorization': f'Token {auth_service.get_token()}',
            'Content-Type': 'application/json'
        }
        
        if method == 'GET':
            response = requests.get(f"{BASE_URL}/{endpoint}", headers=headers, timeout=timeout)
        elif method == 'POST':
            response = requests.post(f"{BASE_URL}/{endpoint}", json=data, headers=headers, timeout=timeout)
        elif method == 'PUT':
            response = requests.put(f"{BASE_URL}/{endpoint}", json=data, headers=headers, timeout=timeout)
        elif method == 'DELETE':
            response = requests.delete(f"{BASE_URL}/{endpoint}", headers=headers, timeout=timeout)
        
        response.raise_for_status()
        return response.json()
        
    except ConnectionError:
        # Network connection error - work offline
        return {"error": "network_unavailable", "message": "Working in offline mode"}
    except Timeout:
        # Request timeout
        return {"error": "timeout", "message": "Request timed out"}
    except RequestException as e:
        # Other request errors
        return {"error": "request_failed", "message": str(e)}
    except Exception as e:
        # Unexpected errors
        return {"error": "unknown", "message": str(e)}
```

### Offline Mode Detection
```python
def is_network_available(self):
    """Check if network is available"""
    try:
        response = requests.get(f"{BASE_URL}/health/", timeout=5)
        return response.status_code == 200
    except:
        return False

def handle_offline_mode(self):
    """Handle offline mode operations"""
    # Load data from local database
    projects = self.db_service.get_all_projects()
    questions = self.db_service.get_all_questions()
    responses = self.db_service.get_all_responses()
    
    # Queue operations for later sync
    return {
        'projects': projects,
        'questions': questions,
        'responses': responses,
        'sync_pending': True
    }
```

### Retry Logic
```python
def retry_api_request(self, endpoint, method='GET', data=None, max_retries=3):
    """Retry API request with exponential backoff"""
    for attempt in range(max_retries):
        try:
            result = self.make_api_request(endpoint, method, data)
            if 'error' not in result:
                return result
            
            # Wait before retry (exponential backoff)
            wait_time = 2 ** attempt
            time.sleep(wait_time)
            
        except Exception as e:
            if attempt == max_retries - 1:
                return {"error": "max_retries_exceeded", "message": str(e)}
    
    return {"error": "max_retries_exceeded", "message": "Maximum retries exceeded"}
```

---

## 🧪 Testing & Development

### Development Server Setup
```bash
# Start Django backend server
cd backend
python manage.py runserver

# Test API endpoints
curl -X GET http://localhost:8000/api/v1/projects/ \
  -H "Authorization: Token your_token_here"
```

### API Testing with Swagger
1. Open `http://localhost:8000/swagger/`
2. Click "Authorize" and enter your token
3. Test endpoints directly from the browser

### Mock Data for Testing
```python
# Create test data in Django admin or via management commands
python manage.py shell

from authentication.models import User
from projects.models import Project
from forms.models import Question

# Create test user
user = User.objects.create_user(
    username='testuser',
    email='test@example.com',
    password='testpass123',
    role='researcher'
)

# Create test project
project = Project.objects.create(
    name='Test Research Project',
    description='A test project for development',
    created_by=user
)

# Create test question
question = Question.objects.create(
    project=project,
    question_text='What is your age?',
    question_type='numeric',
    is_required=True,
    order_index=1
)
```

### Unit Testing
```python
import unittest
from services.auth_service import AuthService
from services.sync_service import SyncService

class TestAuthService(unittest.TestCase):
    def setUp(self):
        self.auth_service = AuthService()
    
    def test_login_success(self):
        result = self.auth_service.authenticate('testuser', 'testpass123')
        self.assertTrue(result)
    
    def test_login_failure(self):
        result = self.auth_service.authenticate('wronguser', 'wrongpass')
        self.assertFalse(result)

class TestSyncService(unittest.TestCase):
    def setUp(self):
        self.sync_service = SyncService()
    
    def test_queue_sync(self):
        self.sync_service.queue_sync('projects', 'test-id', 'create', {'name': 'Test'})
        # Verify item was queued
```

---

## 🚀 Production Deployment

### Environment Configuration
```python
# config.py
import os

class Config:
    # Development
    if os.getenv('ENVIRONMENT') == 'development':
        BASE_URL = "http://localhost:8000/api/v1"
        DEBUG = True
    
    # Production
    else:
        BASE_URL = "https://your-production-domain.com/api/v1"
        DEBUG = False
    
    # Sync settings
    SYNC_INTERVAL = int(os.getenv('SYNC_INTERVAL', 300))  # 5 minutes
    MAX_RETRY_ATTEMPTS = int(os.getenv('MAX_RETRY_ATTEMPTS', 3))
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))
```

### Security Considerations
```python
# Secure token storage
from kivy.storage.jsonstore import JsonStore
import hashlib

class SecureAuthService:
    def __init__(self):
        self.store = JsonStore('secure_auth.json')
    
    def save_token_secure(self, token, username):
        # Hash the token before storing
        hashed_token = hashlib.sha256(token.encode()).hexdigest()
        self.store.put('auth', token_hash=hashed_token, username=username)
    
    def verify_token(self, token):
        if self.store.exists('auth'):
            stored_hash = self.store.get('auth').get('token_hash')
            current_hash = hashlib.sha256(token.encode()).hexdigest()
            return stored_hash == current_hash
        return False
```

### Performance Optimization
```python
# Request caching
import time
from functools import lru_cache

class CachedAPIService:
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
    
    @lru_cache(maxsize=100)
    def get_projects(self):
        """Cache projects for 5 minutes"""
        return self.make_api_request('projects/')
    
    def invalidate_cache(self, key=None):
        """Invalidate cache when data changes"""
        if key:
            self.cache.pop(key, None)
        else:
            self.cache.clear()
```

### Monitoring & Logging
```python
import logging
from datetime import datetime

class APILogger:
    def __init__(self):
        logging.basicConfig(
            filename='api_requests.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def log_request(self, endpoint, method, status_code, response_time):
        self.logger.info(
            f"API Request: {method} {endpoint} - Status: {status_code} - Time: {response_time}ms"
        )
    
    def log_error(self, endpoint, method, error):
        self.logger.error(
            f"API Error: {method} {endpoint} - Error: {str(error)}"
        )
```

---

## 📞 Support & Troubleshooting

### Common Issues

1. **Authentication Token Expired**
   ```python
   # Handle token refresh or re-login
   if response.status_code == 401:
       auth_service.logout()
       # Redirect to login screen
   ```

2. **Network Connectivity Issues**
   ```python
   # Check network before making requests
   if not self.is_network_available():
       return self.handle_offline_mode()
   ```

3. **Sync Conflicts**
   ```python
   # Handle data conflicts during sync
   if response.status_code == 409:
       # Resolve conflict by merging data or user choice
       self.resolve_sync_conflict(local_data, server_data)
   ```

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Add debug headers to requests
headers = {
    'Authorization': f'Token {token}',
    'Content-Type': 'application/json',
    'X-Debug': 'true'
}
```

### Contact Information
- **Backend Engineer**: [Your Contact Info]
- **API Documentation**: `http://localhost:8000/swagger/`
- **Admin Interface**: `http://localhost:8000/admin/`

---

## 📝 Checklist for Frontend Implementation

- [ ] Set up authentication service with token management
- [ ] Implement offline-first database schema
- [ ] Create sync service with automatic and manual triggers
- [ ] Add error handling for network issues
- [ ] Implement retry logic with exponential backoff
- [ ] Set up proper logging and monitoring
- [ ] Test all API endpoints
- [ ] Configure production environment variables
- [ ] Implement security best practices
- [ ] Add unit tests for critical functionality

---

*This guide should be updated as the backend evolves. Always check the latest API documentation at `/swagger/` for the most current endpoint specifications.* 
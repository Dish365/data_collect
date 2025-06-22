# Frontend-Backend Integration Points
## Where to Implement API Integration in the Kivy Frontend

This document outlines all the specific locations where frontend integration with the Django backend API should be implemented or enhanced.

---

## 📍 Current Integration Points

### 1. **Authentication Service** (`gui/services/auth_service.py`)

**Current Implementation:**
```python
# Line 6: Base URL configuration
self.base_url = 'http://localhost:8000/api/v1'

# Lines 12-13: Login API call
response = requests.post(
    f'{self.base_url}/auth/login/',
    json={'username': username, 'password': password}
)
```

**Integration Points to Add:**
- [ ] **User Registration**: `/api/auth/register/`
- [ ] **User Profile**: `/api/auth/profile/`
- [ ] **Change Password**: `/api/auth/change-password/`
- [ ] **Logout**: `/api/auth/logout/`
- [ ] **Token Refresh**: Handle expired tokens
- [ ] **Offline Authentication**: Better local storage handling

### 2. **Sync Service** (`gui/services/sync_service.py`)

**Current Implementation:**
```python
# Line 7: Base URL configuration
self.base_url = 'http://localhost:8000/api/v1'

# Lines 51, 53, 55: Basic CRUD operations
response = requests.post(endpoint, json=data)
response = requests.put(f"{endpoint}{item['record_id']}/", json=data)
response = requests.delete(f"{endpoint}{item['record_id']}/")
```

**Integration Points to Add:**
- [ ] **Authentication Headers**: Add token to all requests
- [ ] **Error Handling**: Better error response handling
- [ ] **Retry Logic**: Exponential backoff for failed requests
- [ ] **Conflict Resolution**: Handle data conflicts during sync
- [ ] **Batch Operations**: Sync multiple items at once
- [ ] **Progress Tracking**: Show sync progress to user

### 3. **Data Collection Screen** (`gui/screens/data_collection.py`)

**Current Implementation:**
```python
# Lines 135-184: Queue responses for sync
app.sync_service.queue_sync(
    'responses',
    response_id,
    'create',
    {
        'project_id': self.current_project,
        'question_id': question.question_id,
        'respondent_id': respondent_id,
        'response_value': question.get_response(),
        'collected_by': 'user'
    }
)
```

**Integration Points to Add:**
- [ ] **Real-time Sync**: Immediate sync after response submission
- [ ] **Response Validation**: Validate responses before sending
- [ ] **Location Data**: Include GPS coordinates
- [ ] **Metadata**: Add device info, timestamp, etc.
- [ ] **Offline Queue**: Better offline handling
- [ ] **Response Status**: Show sync status to user

### 4. **Form Builder Screen** (`gui/screens/form_builder.py`)

**Current Implementation:**
```python
# Lines 286-349: Queue questions for sync
app.sync_service.queue_sync(
    'questions',
    question_id,
    'create',
    {
        'project_id': self.current_project,
        'question_text': question_text,
        'question_type': question_type,
        'options': options_json,
        'order_index': len(self.current_questions)
    }
)
```

**Integration Points to Add:**
- [ ] **Question Validation**: Validate question format
- [ ] **Real-time Preview**: Show question preview
- [ ] **Question Templates**: Pre-built question templates
- [ ] **Question Import**: Import questions from other projects
- [ ] **Question Export**: Export questions to other formats
- [ ] **Question Versioning**: Track question changes

---

## 🆕 Missing Integration Points

### 5. **Projects Screen** (`gui/screens/projects.py`)

**Integration Points to Add:**
- [ ] **Project Creation**: POST `/api/v1/projects/`
- [ ] **Project Listing**: GET `/api/v1/projects/`
- [ ] **Project Details**: GET `/api/v1/projects/{id}/`
- [ ] **Project Update**: PUT `/api/v1/projects/{id}/`
- [ ] **Project Delete**: DELETE `/api/v1/projects/{id}/`
- [ ] **Project Search**: Filter and search projects
- [ ] **Project Sharing**: Share projects with other users
- [ ] **Project Templates**: Use project templates

### 6. **Analytics Screen** (`gui/screens/analytics.py`)

**Integration Points to Add:**
- [ ] **Analytics Results**: GET `/api/analytics/analytics-results/`
- [ ] **Project Analytics**: GET `/api/v1/projects/{id}/analytics/`
- [ ] **Real-time Analytics**: Live data updates
- [ ] **Analytics Export**: Export analytics data
- [ ] **Custom Analytics**: User-defined analytics
- [ ] **Analytics Scheduling**: Scheduled analytics generation
- [ ] **Analytics Sharing**: Share analytics with team

### 7. **Dashboard Screen** (`gui/screens/dashboard.py`)

**Integration Points to Add:**
- [ ] **User Statistics**: GET user activity data
- [ ] **Project Overview**: GET project summaries
- [ ] **Recent Activity**: GET recent actions
- [ ] **Sync Status**: Show sync queue status
- [ ] **Notifications**: GET user notifications
- [ ] **Quick Actions**: Common task shortcuts
- [ ] **Data Summary**: Overview of collected data

### 8. **Sync Screen** (`gui/screens/sync.py`)

**Integration Points to Add:**
- [ ] **Manual Sync**: POST `/api/sync/sync-queue/process_pending/`
- [ ] **Sync Status**: GET `/api/sync/sync-queue/`
- [ ] **Retry Failed**: POST `/api/sync/sync-queue/{id}/retry/`
- [ ] **Sync History**: View sync logs
- [ ] **Conflict Resolution**: Handle sync conflicts
- [ ] **Sync Settings**: Configure sync behavior
- [ ] **Data Export**: Export data for backup

---

## 🔧 Service Layer Enhancements

### 9. **API Service** (`gui/services/api_service.py`) - **NEW FILE**

**Create a centralized API service:**
```python
class APIService:
    def __init__(self, base_url, auth_service):
        self.base_url = base_url
        self.auth_service = auth_service
    
    def make_request(self, endpoint, method='GET', data=None):
        # Centralized request handling with authentication
        pass
    
    def get_projects(self):
        # GET /api/v1/projects/
        pass
    
    def create_project(self, project_data):
        # POST /api/v1/projects/
        pass
    
    def get_questions(self, project_id=None):
        # GET /api/v1/questions/ or /api/v1/projects/{id}/questions/
        pass
    
    def create_question(self, question_data):
        # POST /api/v1/questions/
        pass
    
    def get_responses(self, project_id=None):
        # GET /api/v1/responses/ or /api/v1/projects/{id}/responses/
        pass
    
    def create_response(self, response_data):
        # POST /api/v1/responses/
        pass
    
    def get_analytics(self, project_id=None):
        # GET /api/analytics/analytics-results/
        pass
```

### 10. **Error Handling Service** (`gui/services/error_handler.py`) - **NEW FILE**

**Create centralized error handling:**
```python
class ErrorHandler:
    def handle_network_error(self, error):
        # Handle network connectivity issues
        pass
    
    def handle_auth_error(self, error):
        # Handle authentication errors
        pass
    
    def handle_validation_error(self, error):
        # Handle data validation errors
        pass
    
    def handle_sync_conflict(self, local_data, server_data):
        # Handle data conflicts
        pass
```

### 11. **Cache Service** (`gui/services/cache_service.py`) - **NEW FILE**

**Create caching for better performance:**
```python
class CacheService:
    def cache_projects(self, projects):
        # Cache project data
        pass
    
    def get_cached_projects(self):
        # Get cached projects
        pass
    
    def invalidate_cache(self, key):
        # Invalidate specific cache
        pass
```

---

## 📱 Screen-Specific Integration Tasks

### 12. **Login Screen** (`gui/screens/login.py`)

**Tasks:**
- [ ] Integrate with `/api/auth/login/`
- [ ] Handle login errors
- [ ] Store authentication token
- [ ] Redirect to dashboard on success
- [ ] Show offline mode message

### 13. **Signup Screen** (`gui/screens/signup.py`)

**Tasks:**
- [ ] Integrate with `/api/auth/register/`
- [ ] Validate registration data
- [ ] Handle registration errors
- [ ] Auto-login after successful registration
- [ ] Email verification (if required)

### 14. **Profile Screen** (`gui/screens/profile.py`) - **NEW SCREEN**

**Tasks:**
- [ ] Display user profile from `/api/auth/profile/`
- [ ] Allow profile editing
- [ ] Change password functionality
- [ ] Account settings
- [ ] Logout functionality

---

## 🔄 Data Flow Integration

### 15. **Data Synchronization Flow**

**Current Flow:**
1. User creates/updates data locally
2. Data is stored in SQLite database
3. Change is queued for sync
4. Background sync sends data to backend

**Enhanced Flow:**
1. User creates/updates data locally
2. Data is validated
3. Data is stored in SQLite database
4. Change is queued for sync
5. Background sync sends data to backend
6. Sync status is updated
7. User is notified of sync status
8. Conflicts are resolved if any

### 16. **Authentication Flow**

**Current Flow:**
1. User enters credentials
2. Login request is sent to backend
3. Token is stored locally
4. User is redirected to dashboard

**Enhanced Flow:**
1. User enters credentials
2. Login request is sent to backend
3. Token is stored securely
4. User profile is fetched
5. User is redirected to dashboard
6. Token refresh is scheduled
7. Offline mode is handled

---

## 🧪 Testing Integration Points

### 17. **Unit Tests** (`gui/tests/`)

**Test Files to Create:**
- [ ] `test_api_service.py`
- [ ] `test_auth_service.py`
- [ ] `test_sync_service.py`
- [ ] `test_error_handler.py`
- [ ] `test_cache_service.py`

### 18. **Integration Tests** (`gui/tests/`)

**Test Files to Create:**
- [ ] `test_backend_integration.py`
- [ ] `test_offline_mode.py`
- [ ] `test_sync_conflicts.py`
- [ ] `test_authentication_flow.py`

---

## 📋 Implementation Checklist

### Phase 1: Core API Integration
- [ ] Create centralized `APIService` class
- [ ] Enhance `AuthService` with all auth endpoints
- [ ] Improve `SyncService` with better error handling
- [ ] Add authentication headers to all requests
- [ ] Implement retry logic for failed requests

### Phase 2: Screen Integration
- [ ] Integrate Projects screen with backend
- [ ] Integrate Analytics screen with backend
- [ ] Enhance Data Collection screen
- [ ] Enhance Form Builder screen
- [ ] Create Profile screen

### Phase 3: Advanced Features
- [ ] Implement real-time sync
- [ ] Add conflict resolution
- [ ] Create caching system
- [ ] Add offline mode indicators
- [ ] Implement data export/import

### Phase 4: Testing & Optimization
- [ ] Write comprehensive tests
- [ ] Performance optimization
- [ ] Error handling improvements
- [ ] User experience enhancements
- [ ] Documentation updates

---

## 🚨 Important Notes

1. **Base URL Configuration**: Update `base_url` in all services for production
2. **Authentication**: Always include authentication headers in API requests
3. **Error Handling**: Implement proper error handling for all API calls
4. **Offline Mode**: Ensure app works offline with proper sync when online
5. **Data Validation**: Validate data before sending to backend
6. **Security**: Store sensitive data securely
7. **Performance**: Implement caching for better performance
8. **Testing**: Test all integration points thoroughly

---

*This document should be updated as new integration points are identified or requirements change.* 
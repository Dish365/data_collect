# Frontend Troubleshooting Guide
## Fixing 404 Errors and API Integration Issues

This guide addresses common issues when integrating the Kivy frontend with the Django backend API.

---

## 🚨 Current Issue: 404 Errors

### Problem
```
Not Found: /auth/login/
Not Found: /auth/register/
```

### Root Cause
The frontend is trying to access authentication endpoints at the wrong URL path.

### Solution
**Fixed in `gui/services/auth_service.py`:**

**Before (Incorrect):**
```python
self.base_url = 'http://localhost:8000/api/v1'  # Wrong!
# This results in: http://localhost:8000/api/v1/auth/login/
```

**After (Correct):**
```python
self.base_url = 'http://localhost:8000/api'  # Fixed!
# This results in: http://localhost:8000/api/auth/login/
```

---

## 📍 Backend URL Structure

### Authentication Endpoints
- **Login**: `POST /api/auth/login/`
- **Register**: `POST /api/auth/register/`
- **Logout**: `POST /api/auth/logout/`
- **Profile**: `GET /api/auth/profile/`
- **Change Password**: `PUT /api/auth/change-password/`

### API v1 Endpoints
- **Projects**: `/api/v1/projects/`
- **Questions**: `/api/v1/questions/`
- **Responses**: `/api/v1/responses/`
- **Sync Queue**: `/api/v1/sync-queue/`
- **Analytics**: `/api/v1/analytics-results/`

### Individual App Endpoints
- **Analytics**: `/api/analytics/`
- **Forms**: `/api/forms/`
- **Projects**: `/api/projects/`
- **Responses**: `/api/responses/`
- **Sync**: `/api/sync/`

---

## 🔧 Configuration Fixes

### 1. **AuthService Configuration** ✅ FIXED

**File**: `gui/services/auth_service.py`

```python
class AuthService:
    def __init__(self):
        self.store = JsonStore('auth.json')
        self.base_url = 'http://localhost:8000/api'  # ✅ Correct
        self.token = None
```

### 2. **SyncService Configuration** ✅ CORRECT

**File**: `gui/services/sync_service.py`

```python
class SyncService:
    def __init__(self):
        self.base_url = 'http://localhost:8000/api/v1'  # ✅ Correct for main API
        self.sync_interval = 300
        self.is_syncing = False
```

### 3. **Add Authentication Headers**

**File**: `gui/services/sync_service.py`

```python
def _process_sync_item(self, item):
    """Process a single sync queue item"""
    try:
        data = json.loads(item['data'])
        endpoint = f"{self.base_url}/{item['table_name']}/"
        
        # Add authentication headers
        headers = {
            'Authorization': f'Token {self.auth_service.get_token()}',
            'Content-Type': 'application/json'
        }
        
        if item['operation'] == 'create':
            response = requests.post(endpoint, json=data, headers=headers)
        elif item['operation'] == 'update':
            response = requests.put(f"{endpoint}{item['record_id']}/", json=data, headers=headers)
        elif item['operation'] == 'delete':
            response = requests.delete(f"{endpoint}{item['record_id']}/", headers=headers)
        
        # ... rest of the method
```

---

## 🧪 Testing the Fix

### 1. **Test Authentication Endpoints**

```bash
# Test login endpoint
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'

# Test register endpoint
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "newuser", "email": "new@example.com", "password": "pass123", "password2": "pass123", "role": "field_worker"}'
```

### 2. **Test API v1 Endpoints**

```bash
# Test projects endpoint (requires authentication)
curl -X GET http://localhost:8000/api/v1/projects/ \
  -H "Authorization: Token your_token_here"

# Test questions endpoint
curl -X GET http://localhost:8000/api/v1/questions/ \
  -H "Authorization: Token your_token_here"
```

### 3. **Check Backend Server**

```bash
# Make sure backend is running
cd backend
python manage.py runserver

# Check available URLs
python manage.py show_urls
```

---

## 🔍 Debugging Steps

### 1. **Check Backend URLs**

```bash
# In Django shell
python manage.py shell

>>> from django.urls import get_resolver
>>> resolver = get_resolver()
>>> for url in resolver.url_patterns:
...     print(url.pattern)
```

### 2. **Check Frontend Requests**

Add debug logging to `AuthService`:

```python
def authenticate(self, username, password):
    """Authenticate user with backend"""
    try:
        url = f'{self.base_url}/auth/login/'
        print(f"Making request to: {url}")  # Debug log
        
        response = requests.post(
            url,
            json={'username': username, 'password': password}
        )
        
        print(f"Response status: {response.status_code}")  # Debug log
        print(f"Response content: {response.text}")  # Debug log
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get('token')
            self.store.put('auth', token=self.token, username=username)
            return True
        return False
    except requests.RequestException as e:
        print(f"Request error: {str(e)}")  # Debug log
        return False
```

### 3. **Check Network Connectivity**

```python
def test_connectivity(self):
    """Test if backend is reachable"""
    try:
        response = requests.get('http://localhost:8000/api/auth/login/', timeout=5)
        print(f"Backend reachable: {response.status_code}")
        return True
    except requests.RequestException as e:
        print(f"Backend not reachable: {str(e)}")
        return False
```

---

## 🚨 Common Issues & Solutions

### Issue 1: CORS Errors
**Error**: `Access to XMLHttpRequest at 'http://localhost:8000/api/auth/login/' from origin 'null' has been blocked by CORS policy`

**Solution**: Add CORS headers to Django settings:

```python
# backend/core/settings/base.py
INSTALLED_APPS = [
    # ...
    'corsheaders',
    # ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Add this first
    'django.middleware.common.CommonMiddleware',
    # ...
]

# Development settings
CORS_ALLOW_ALL_ORIGINS = True  # Only for development
CORS_ALLOW_CREDENTIALS = True
```

### Issue 2: Authentication Token Missing
**Error**: `401 Unauthorized`

**Solution**: Ensure token is included in headers:

```python
headers = {
    'Authorization': f'Token {auth_service.get_token()}',
    'Content-Type': 'application/json'
}
```

### Issue 3: Database Connection Errors
**Error**: `Database connection failed`

**Solution**: Check Django database settings and run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Issue 4: Port Already in Use
**Error**: `Address already in use`

**Solution**: Kill existing process or use different port:

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
python manage.py runserver 8001
```

---

## 📋 Verification Checklist

- [ ] Backend server is running on `http://localhost:8000`
- [ ] Authentication endpoints are accessible at `/api/auth/`
- [ ] API v1 endpoints are accessible at `/api/v1/`
- [ ] Frontend `AuthService` uses correct base URL
- [ ] Frontend `SyncService` uses correct base URL
- [ ] Authentication headers are included in requests
- [ ] CORS is properly configured
- [ ] Database migrations are applied
- [ ] Test user exists in database

---

## 🔗 Useful Links

- **Backend Admin**: `http://localhost:8000/admin/`
- **API Documentation**: `http://localhost:8000/swagger/`
- **ReDoc**: `http://localhost:8000/redoc/`
- **Health Check**: `http://localhost:8000/api/health/` (if implemented)

---

## 📞 Getting Help

If you're still experiencing issues:

1. **Check the logs**: Look at Django server logs for detailed error messages
2. **Test endpoints manually**: Use curl or Postman to test API endpoints
3. **Verify configuration**: Double-check all URL configurations
4. **Check network**: Ensure frontend can reach backend server
5. **Review documentation**: Check the main integration guide

---

*This troubleshooting guide should be updated as new issues are identified.* 
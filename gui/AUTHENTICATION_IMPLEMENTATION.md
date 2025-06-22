# Authentication Implementation with Spinner

This document describes the complete authentication implementation for the Research Data Collector app, including spinner functionality, error handling, and offline mode support.

## 🚀 Features Implemented

### ✅ Authentication Flow
- **Async Authentication**: Non-blocking authentication with callback support
- **Spinner UI**: Visual feedback during authentication process
- **Error Handling**: Comprehensive error handling for network issues
- **Offline Mode**: Graceful handling when network is unavailable
- **Token Management**: Secure token storage and retrieval
- **Auto-login**: Remembers user session across app restarts

### ✅ UI Components
- **Login Screen**: Updated with spinner and disabled state during auth
- **Top Bar**: Shows user information and logout functionality
- **Error Messages**: User-friendly error messages for different scenarios

## 📱 User Experience

### Login Process
1. User enters username and password
2. Login button is disabled and spinner appears
3. Authentication request is sent to backend
4. Success: User is redirected to dashboard
5. Failure: Appropriate error message is shown
6. Spinner disappears and form is re-enabled

### Error Scenarios Handled
- **Invalid Credentials**: "Invalid username or password"
- **Network Unavailable**: "No network connection. Please check your internet connection."
- **Timeout**: "Request timed out. Please try again."
- **Server Error**: "Server error: [status_code]"
- **Connection Error**: "Connection failed. Please check your internet connection."

## 🔧 Technical Implementation

### AuthService Class (`services/auth_service.py`)

#### Key Methods:
```python
def authenticate(self, username, password, callback=None)
```
- Performs async authentication
- Checks network connectivity first
- Handles all error scenarios
- Calls callback with result

```python
def _check_network_connectivity(self)
```
- Tests server connectivity
- Returns True if server is reachable

```python
def make_authenticated_request(self, endpoint, method='GET', data=None, timeout=30)
```
- Makes authenticated API requests
- Handles token management
- Provides consistent error handling

### LoginScreen Class (`screens/login.py`)

#### Key Properties:
```python
is_authenticating = BooleanProperty(False)
```
- Controls spinner visibility
- Disables form inputs during auth

#### Key Methods:
```python
def login(self)
```
- Validates input
- Starts authentication process
- Shows spinner

```python
def _on_auth_complete(self, result)
```
- Handles authentication result
- Shows appropriate success/error messages
- Navigates to dashboard on success

### TopBar Widget (`widgets/top_bar.py`)

#### Key Methods:
```python
def update_user_info(self)
```
- Displays user information from auth service
- Shows name, username, or "User" as fallback

```python
def logout(self)
```
- Logs out user
- Clears stored credentials
- Navigates to login screen

## 🎨 UI Updates

### Login Screen (`kv/login.kv`)
- Added spinner with "Authenticating..." text
- Disabled form inputs during authentication
- Improved visual feedback

### Top Bar (`kv/topbar.kv`)
- Added logout button
- Dynamic user information display
- Consistent styling

## 🔐 Security Features

### Token Storage
- Tokens stored securely using Kivy's JsonStore
- Automatic token retrieval on app restart
- Secure logout with server notification

### Network Security
- HTTPS support (update BASE_URL for production)
- Timeout protection (30 seconds default)
- Connection error handling

## 🌐 Backend Integration

### API Endpoints Used
- `POST /api/v1/auth/login/` - User authentication
- `POST /api/v1/auth/logout/` - User logout
- `GET /api/v1/` - Network connectivity check

### Request Format
```json
{
    "username": "user@example.com",
    "password": "userpassword"
}
```

### Response Format
```json
{
    "token": "your_auth_token_here",
    "user_data": {
        "id": "user_uuid",
        "username": "username",
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "researcher"
    }
}
```

## 🚀 Usage Examples

### Basic Authentication
```python
# In your screen class
def login(self):
    app = MDApp.get_running_app()
    app.auth_service.authenticate(username, password, self._on_auth_complete)

def _on_auth_complete(self, result):
    if result.get('success'):
        # Navigate to dashboard
        self.manager.current = "dashboard"
    else:
        # Show error message
        toast(result.get('message'))
```

### Making Authenticated Requests
```python
# Get user projects
result = auth_service.make_authenticated_request('projects/')
if 'error' not in result:
    projects = result
else:
    # Handle error
    print(f"Error: {result['message']}")
```

### Checking Authentication Status
```python
if auth_service.is_authenticated():
    # User is logged in
    user_data = auth_service.get_user_data()
    token = auth_service.get_token()
else:
    # User needs to login
    pass
```

## 🔧 Configuration

### Backend URL
Update the `BASE_URL` in `services/auth_service.py`:
```python
# Development
self.base_url = 'http://127.0.0.1:8000/api/v1'

# Production
self.base_url = 'https://your-domain.com/api/v1'
```

### Timeout Settings
```python
# Authentication timeout (seconds)
timeout=30

# Network check timeout (seconds)
timeout=5
```

## 🧪 Testing

The implementation includes comprehensive error handling and can be tested with:
- Valid credentials
- Invalid credentials
- Network unavailable
- Server down
- Slow network (timeout)

## 📋 Future Enhancements

### Potential Improvements
1. **Biometric Authentication**: Add fingerprint/face ID support
2. **Two-Factor Authentication**: Support for 2FA
3. **Password Reset**: Implement forgot password functionality
4. **Session Management**: Automatic token refresh
5. **Offline Authentication**: Local authentication for offline mode

### Security Enhancements
1. **Token Encryption**: Encrypt stored tokens
2. **Certificate Pinning**: Prevent MITM attacks
3. **Rate Limiting**: Prevent brute force attacks
4. **Audit Logging**: Track authentication events

## 🐛 Troubleshooting

### Common Issues

#### "Network Unavailable" Error
- Check if backend server is running
- Verify BASE_URL is correct
- Check internet connection

#### "Invalid Credentials" Error
- Verify username/password are correct
- Check if user account is active
- Ensure backend authentication is working

#### Spinner Not Showing
- Check if `is_authenticating` property is properly bound
- Verify KV file includes spinner widget
- Ensure callback is being called

#### Token Not Persisting
- Check JsonStore permissions
- Verify token is being saved correctly
- Check if logout is being called unexpectedly

## 📞 Support

For issues or questions about the authentication implementation:
1. Check the error messages in the console
2. Verify backend API endpoints are working
3. Test network connectivity
4. Review the authentication flow logs 
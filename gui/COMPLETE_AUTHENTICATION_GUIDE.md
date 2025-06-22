# Complete Authentication System Guide

This guide covers the complete authentication implementation for the Research Data Collector app, including login, signup, and forgot password functionality with spinner UI and comprehensive error handling.

## 🚀 Features Overview

### ✅ Complete Authentication Flow
- **Login**: Username/password authentication with spinner
- **Signup**: User registration with comprehensive validation
- **Forgot Password**: Password reset functionality
- **Auto-login**: Session persistence across app restarts
- **Logout**: Secure logout with server notification

### ✅ UI/UX Features
- **Spinner Feedback**: Visual loading indicators during all auth operations
- **Form Validation**: Client-side validation with helpful error messages
- **Error Handling**: Comprehensive error handling for all scenarios
- **Responsive Design**: Disabled states during processing
- **User Information**: Dynamic user display in top bar

## 📱 User Experience Flow

### 🔐 Login Process
1. User enters username and password
2. Login button disabled, spinner appears with "Authenticating..."
3. Authentication request sent to backend
4. **Success**: Redirect to dashboard with success message
5. **Failure**: Show specific error message, re-enable form

### 📝 Signup Process
1. User fills registration form (username, names, email, password)
2. Client-side validation checks all fields
3. Signup button disabled, spinner appears with "Creating account..."
4. Registration request sent to backend
5. **Success**: Redirect to dashboard with welcome message
6. **Failure**: Show field-specific or general error messages

### 🔑 Forgot Password Process
1. User clicks "Forgot Password?" link
2. Popup opens requesting username or email
3. Submit button disabled, spinner appears with "Processing..."
4. Password reset request sent to backend
5. **Success**: Show confirmation message and close popup
6. **Failure**: Show specific error message in popup

## 🔧 Technical Implementation

### AuthService Class (`services/auth_service.py`)

#### Core Methods:
```python
def authenticate(self, username, password, callback=None)
def register(self, username, email, password, password2, first_name="", last_name="", role="researcher", callback=None)
def forgot_password(self, username_or_email, callback=None)
def logout(self)
def is_authenticated(self)
def get_token(self)
def get_user_data(self)
def make_authenticated_request(self, endpoint, method='GET', data=None, timeout=30)
```

#### Key Features:
- **Async Operations**: All auth operations are non-blocking
- **Network Detection**: Checks connectivity before making requests
- **Error Categorization**: Different handling for different error types
- **Token Management**: Secure storage and retrieval
- **Offline Support**: Graceful handling when network unavailable

### LoginScreen Class (`screens/login.py`)

#### Properties:
```python
is_authenticating = BooleanProperty(False)
```

#### Key Methods:
```python
def login(self)
def _on_auth_complete(self, result)
def on_signup(self)
def on_forgot_password(self)
def on_enter(self)
```

### SignUpScreen Class (`screens/signup.py`)

#### Properties:
```python
is_registering = BooleanProperty(False)
```

#### Key Methods:
```python
def signup(self)
def _validate_form(self, username, first_name, last_name, email, password, confirm_password)
def _on_registration_complete(self, result)
def on_login(self)
def on_enter(self)
```

### ForgotPasswordPopup Class (`widgets/forgot_password_popup.py`)

#### Properties:
```python
is_processing = BooleanProperty(False)
```

#### Key Methods:
```python
def on_submit(self)
def _on_forgot_password_complete(self, result)
```

## 🎨 UI Components

### Login Screen (`kv/login.kv`)
- Username and password fields
- Spinner with "Authenticating..." text
- Disabled form during authentication
- "Forgot Password?" link
- "Sign Up" link

### Signup Screen (`kv/signup.kv`)
- Username, first name, last name, email fields
- Password and confirm password fields
- Spinner with "Creating account..." text
- Disabled form during registration
- Back to login link

### Forgot Password Popup (`kv/forgot_password_popup.kv`)
- Username/email input field
- Spinner with "Processing..." text
- Disabled submit button during processing
- Error message display

### Top Bar (`kv/topbar.kv`)
- User information display
- Logout button
- Dynamic user name from auth service

## 🔐 Security Features

### Input Validation
- **Username**: 3-30 characters, alphanumeric + underscore
- **Email**: Valid email format validation
- **Password**: Minimum 8 characters, letters + numbers
- **Password Confirmation**: Must match password

### Network Security
- **HTTPS Support**: Update BASE_URL for production
- **Timeout Protection**: 30-second timeout for all requests
- **Connection Error Handling**: Graceful offline mode

### Token Security
- **Secure Storage**: Using Kivy's JsonStore
- **Automatic Cleanup**: Tokens cleared on logout
- **Server Notification**: Logout request sent to server

## 🌐 API Integration

### Authentication Endpoints
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/api/v1/auth/login/` | User login | `{username, password}` | `{token, user_data}` |
| POST | `/api/v1/auth/register/` | User registration | `{username, email, password, password2, first_name?, last_name?, role}` | `{token, user_data}` |
| POST | `/api/v1/auth/forgot-password/` | Password reset | `{username_or_email}` | `{message}` |
| POST | `/api/v1/auth/logout/` | User logout | `{}` | `{message}` |

### Request Examples

#### Login Request:
```json
{
    "username": "john_doe",
    "password": "securepass123"
}
```

#### Registration Request:
```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepass123",
    "password2": "securepass123",
    "first_name": "John",
    "last_name": "Doe",
    "role": "researcher"
}
```

#### Forgot Password Request:
```json
{
    "username_or_email": "john_doe"
}
```

### Response Examples

#### Successful Login/Registration:
```json
{
    "token": "your_auth_token_here",
    "user_data": {
        "id": "user_uuid",
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "researcher",
        "is_active": true
    }
}
```

#### Error Response:
```json
{
    "error": "validation_error",
    "message": "Username already exists",
    "field_errors": {
        "username": ["A user with that username already exists."]
    }
}
```

## 🚀 Usage Examples

### Basic Authentication Flow
```python
# Login
app.auth_service.authenticate(username, password, self._on_auth_complete)

# Registration
app.auth_service.register(username, email, password, password2, 
                         first_name, last_name, "researcher", 
                         self._on_registration_complete)

# Forgot Password
app.auth_service.forgot_password(username_or_email, self._on_forgot_password_complete)

# Logout
app.auth_service.logout()
```

### Making Authenticated Requests
```python
# Get user projects
result = auth_service.make_authenticated_request('projects/')
if 'error' not in result:
    projects = result
else:
    print(f"Error: {result['message']}")
```

### Checking Authentication Status
```python
if auth_service.is_authenticated():
    user_data = auth_service.get_user_data()
    token = auth_service.get_token()
    print(f"Logged in as: {user_data.get('username')}")
```

## 🔧 Configuration

### Backend URL Configuration
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

### Validation Rules
```python
# Username validation
username_pattern = r'^[a-zA-Z0-9_]{3,30}$'

# Email validation
email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# Password requirements
min_password_length = 8
require_letters_and_numbers = True
```

## 🧪 Testing Scenarios

### Login Testing
- ✅ Valid credentials
- ❌ Invalid credentials
- ❌ Network unavailable
- ❌ Server down
- ❌ Slow network (timeout)

### Registration Testing
- ✅ Valid registration data
- ❌ Username already exists
- ❌ Email already exists
- ❌ Weak password
- ❌ Invalid email format
- ❌ Network unavailable

### Forgot Password Testing
- ✅ Valid username/email
- ❌ User not found
- ❌ Network unavailable
- ❌ Server error

## 🐛 Error Handling

### Error Types and Messages

#### Login Errors:
- `invalid_credentials`: "Invalid username or password"
- `network_unavailable`: "No network connection. Please check your internet connection."
- `timeout`: "Request timed out. Please try again."
- `server_error`: "Server error: [status_code]"

#### Registration Errors:
- `validation_error`: Field-specific error messages
- `user_exists`: "User with this username or email already exists"
- `network_unavailable`: "No network connection. Please check your internet connection."
- `timeout`: "Request timed out. Please try again."

#### Forgot Password Errors:
- `user_not_found`: "No user found with this username or email."
- `network_unavailable`: "No network connection. Please check your internet connection."
- `timeout`: "Request timed out. Please try again."

## 📋 Future Enhancements

### Potential Improvements
1. **Biometric Authentication**: Fingerprint/face ID support
2. **Two-Factor Authentication**: 2FA support
3. **Social Login**: Google, Facebook integration
4. **Session Management**: Automatic token refresh
5. **Offline Authentication**: Local auth for offline mode
6. **Password Strength Indicator**: Visual password strength meter
7. **Email Verification**: Email verification flow

### Security Enhancements
1. **Token Encryption**: Encrypt stored tokens
2. **Certificate Pinning**: Prevent MITM attacks
3. **Rate Limiting**: Prevent brute force attacks
4. **Audit Logging**: Track authentication events
5. **Device Management**: Track and manage devices

## 🐛 Troubleshooting

### Common Issues

#### "Network Unavailable" Error
- Check if backend server is running
- Verify BASE_URL is correct
- Check internet connection
- Test with `auth_service._check_network_connectivity()`

#### "Invalid Credentials" Error
- Verify username/password are correct
- Check if user account is active
- Ensure backend authentication is working
- Check server logs for authentication errors

#### Registration Validation Errors
- Check username format (3-30 chars, alphanumeric + underscore)
- Verify email format is valid
- Ensure password meets requirements (8+ chars, letters + numbers)
- Check if username/email already exists

#### Spinner Not Showing
- Check if `is_authenticating`/`is_registering` properties are properly bound
- Verify KV file includes spinner widgets
- Ensure callback functions are being called
- Check for UI update issues

#### Token Not Persisting
- Check JsonStore permissions
- Verify token is being saved correctly
- Check if logout is being called unexpectedly
- Test with `auth_service.is_authenticated()`

## 📞 Support

For issues or questions about the authentication system:

1. **Check Console Logs**: Look for error messages and debug information
2. **Verify Backend**: Ensure Django backend is running and accessible
3. **Test Network**: Check network connectivity and API endpoints
4. **Review Flow**: Follow the authentication flow step by step
5. **Check Configuration**: Verify BASE_URL and timeout settings

### Debug Commands
```python
# Test network connectivity
print(auth_service._check_network_connectivity())

# Check authentication status
print(auth_service.is_authenticated())

# Get stored token
print(auth_service.get_token())

# Get user data
print(auth_service.get_user_data())
```

The complete authentication system provides a robust, user-friendly, and secure authentication experience for the Research Data Collector app. 
import requests
import json
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from requests.exceptions import RequestException, Timeout, ConnectionError

class AuthService:
    def __init__(self):
        self.store = JsonStore('auth.json')
        self.base_url = 'http://localhost:8000'  # Change this to your backend URL
        self.token = None
        self.user_data = None
    
    def authenticate(self, username, password, callback=None):
        """Authenticate user with backend asynchronously"""
        def _authenticate():
            try:
                # Check network connectivity first
                if not self._check_network_connectivity():
                    if callback:
                        callback({
                            'success': False,
                            'error': 'network_unavailable',
                            'message': 'No network connection. Please check your internet connection.'
                        })
                    return

                response = requests.post(
                    f'{self.base_url}/auth/login/',
                    json={'username': username, 'password': password},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.token = data.get('token')
                    self.user_data = data.get('user_data', {})
                    
                    # Save to local storage
                    self.store.put('auth', 
                                 token=self.token, 
                                 username=username,
                                 user_data=json.dumps(self.user_data))
                    
                    if callback:
                        callback({
                            'success': True,
                            'token': self.token,
                            'user_data': self.user_data
                        })
                elif response.status_code == 401:
                    if callback:
                        callback({
                            'success': False,
                            'error': 'invalid_credentials',
                            'message': 'Invalid username or password'
                        })
                else:
                    if callback:
                        callback({
                            'success': False,
                            'error': 'server_error',
                            'message': f'Server error: {response.status_code}'
                        })
                        
            except Timeout:
                if callback:
                    callback({
                        'success': False,
                        'error': 'timeout',
                        'message': 'Request timed out. Please try again.'
                    })
            except ConnectionError:
                if callback:
                    callback({
                        'success': False,
                        'error': 'connection_error',
                        'message': 'Connection failed. Please check your internet connection.'
                    })
            except RequestException as e:
                if callback:
                    callback({
                        'success': False,
                        'error': 'request_failed',
                        'message': f'Request failed: {str(e)}'
                    })
            except Exception as e:
                if callback:
                    callback({
                        'success': False,
                        'error': 'unknown',
                        'message': f'An unexpected error occurred: {str(e)}'
                    })
        
        # Run authentication in a separate thread to avoid blocking UI
        Clock.schedule_once(lambda dt: _authenticate(), 0)
    
    def _check_network_connectivity(self):
        """Check if network is available"""
        try:
            # Try to connect to the base URL first
            response = requests.get(f"{self.base_url}/", timeout=5)
            return response.status_code in [200, 404, 405]  # Any response means server is reachable
        except:
            try:
                # Fallback: try to connect to the auth endpoint
                response = requests.get(f"{self.base_url}/auth/", timeout=5)
                return response.status_code in [200, 404, 405]
            except:
                return False
    
    def register(self, username, email, password, password2, role='field_worker'):
        """Register new user with backend"""
        try:
            response = requests.post(
                f'{self.base_url}/auth/register/',
                json={
                    'username': username,
                    'email': email,
                    'password': password,
                    'password2': password2,
                    'role': role
                }
            )
            
            if response.status_code == 201:
                data = response.json()
                self.token = data.get('token')
                self.store.put('auth', token=self.token, username=username)
                return True
            return False
        except requests.RequestException:
            return False
    
    def logout(self):
        """Logout user and clear stored credentials"""
        try:
            # Try to logout from server
            if self.token:
                requests.post(
                    f'{self.base_url}/auth/logout/',
                    headers={'Authorization': f'Token {self.token}'},
                    timeout=10
                )
        except:
            pass  # Ignore logout errors
        
        self.token = None
        self.user_data = None
        if self.store.exists('auth'):
            self.store.delete('auth')
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        if self.token:
            return True
        
        if self.store.exists('auth'):
            auth_data = self.store.get('auth')
            self.token = auth_data.get('token')
            user_data_str = auth_data.get('user_data')
            if user_data_str:
                try:
                    self.user_data = json.loads(user_data_str)
                except:
                    self.user_data = {}
            return self.token is not None
        return False
    
    def get_token(self):
        """Get current authentication token"""
        if not self.token and self.store.exists('auth'):
            self.token = self.store.get('auth').get('token')
        return self.token
    
    def get_user_data(self):
        """Get current user data"""
        if not self.user_data and self.store.exists('auth'):
            user_data_str = self.store.get('auth').get('user_data')
            if user_data_str:
                try:
                    self.user_data = json.loads(user_data_str)
                except:
                    self.user_data = {}
        return self.user_data
    
    def make_authenticated_request(self, endpoint, method='GET', data=None, timeout=30):
        """Make authenticated API request with proper error handling"""
        try:
            token = self.get_token()
            if not token:
                return {"error": "not_authenticated", "message": "User not authenticated"}
            
            headers = {
                'Authorization': f'Token {token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.base_url}/{endpoint}"
            
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=timeout)
            
            response.raise_for_status()
            return response.json()
            
        except ConnectionError:
            return {"error": "network_unavailable", "message": "Working in offline mode"}
        except Timeout:
            return {"error": "timeout", "message": "Request timed out"}
        except RequestException as e:
            return {"error": "request_failed", "message": str(e)}
        except Exception as e:
            return {"error": "unknown", "message": str(e)}
    
    def register(self, username, email, password, password2, first_name="", last_name="", role="researcher", callback=None):
        """Register new user with backend asynchronously"""
        def _register():
            try:
                # Check network connectivity first
                if not self._check_network_connectivity():
                    if callback:
                        callback({
                            'success': False,
                            'error': 'network_unavailable',
                            'message': 'No network connection. Please check your internet connection.'
                        })
                    return

                # Prepare registration data
                registration_data = {
                    'username': username,
                    'email': email,
                    'password': password,
                    'password2': password2,
                    'role': role
                }
                
                # Add optional fields if provided
                if first_name:
                    registration_data['first_name'] = first_name
                if last_name:
                    registration_data['last_name'] = last_name

                response = requests.post(
                    f'{self.base_url}/auth/register/',
                    json=registration_data,
                    timeout=30
                )
                
                if response.status_code == 201:  # Created
                    data = response.json()
                    self.token = data.get('token')
                    self.user_data = data.get('user_data', {})
                    
                    # Save to local storage
                    self.store.put('auth', 
                                 token=self.token, 
                                 username=username,
                                 user_data=json.dumps(self.user_data))
                    
                    if callback:
                        callback({
                            'success': True,
                            'token': self.token,
                            'user_data': self.user_data,
                            'message': 'Registration successful!'
                        })
                elif response.status_code == 400:
                    # Validation errors
                    error_data = response.json()
                    error_messages = []
                    
                    # Extract error messages from response
                    for field, errors in error_data.items():
                        if isinstance(errors, list):
                            error_messages.extend(errors)
                        else:
                            error_messages.append(str(errors))
                    
                    error_message = '; '.join(error_messages) if error_messages else 'Registration failed'
                    
                    if callback:
                        callback({
                            'success': False,
                            'error': 'validation_error',
                            'message': error_message,
                            'field_errors': error_data
                        })
                elif response.status_code == 409:
                    # Conflict - user already exists
                    if callback:
                        callback({
                            'success': False,
                            'error': 'user_exists',
                            'message': 'User with this username or email already exists'
                        })
                else:
                    if callback:
                        callback({
                            'success': False,
                            'error': 'server_error',
                            'message': f'Server error: {response.status_code}'
                        })
                        
            except Timeout:
                if callback:
                    callback({
                        'success': False,
                        'error': 'timeout',
                        'message': 'Request timed out. Please try again.'
                    })
            except ConnectionError:
                if callback:
                    callback({
                        'success': False,
                        'error': 'connection_error',
                        'message': 'Connection failed. Please check your internet connection.'
                    })
            except RequestException as e:
                if callback:
                    callback({
                        'success': False,
                        'error': 'request_failed',
                        'message': f'Request failed: {str(e)}'
                    })
            except Exception as e:
                if callback:
                    callback({
                        'success': False,
                        'error': 'unknown',
                        'message': f'An unexpected error occurred: {str(e)}'
                    })
        
        # Run registration in a separate thread to avoid blocking UI
        Clock.schedule_once(lambda dt: _register(), 0)
    
    def forgot_password(self, username_or_email, callback=None):
        """Request password reset"""
        def _forgot_password():
            try:
                # Check network connectivity first
                if not self._check_network_connectivity():
                    if callback:
                        callback({
                            'success': False,
                            'error': 'network_unavailable',
                            'message': 'No network connection. Please check your internet connection.'
                        })
                    return

                response = requests.post(
                    f'{self.base_url}/auth/forgot-password/',
                    json={'username_or_email': username_or_email},
                    timeout=30
                )
                
                if response.status_code == 200:
                    if callback:
                        callback({
                            'success': True,
                            'message': 'Password reset instructions have been sent to your email.'
                        })
                elif response.status_code == 404:
                    if callback:
                        callback({
                            'success': False,
                            'error': 'user_not_found',
                            'message': 'No user found with this username or email.'
                        })
                elif response.status_code == 400:
                    error_data = response.json()
                    error_message = error_data.get('message', 'Invalid request')
                    if callback:
                        callback({
                            'success': False,
                            'error': 'validation_error',
                            'message': error_message
                        })
                else:
                    if callback:
                        callback({
                            'success': False,
                            'error': 'server_error',
                            'message': f'Server error: {response.status_code}'
                        })
                        
            except Timeout:
                if callback:
                    callback({
                        'success': False,
                        'error': 'timeout',
                        'message': 'Request timed out. Please try again.'
                    })
            except ConnectionError:
                if callback:
                    callback({
                        'success': False,
                        'error': 'connection_error',
                        'message': 'Connection failed. Please check your internet connection.'
                    })
            except RequestException as e:
                if callback:
                    callback({
                        'success': False,
                        'error': 'request_failed',
                        'message': f'Request failed: {str(e)}'
                    })
            except Exception as e:
                if callback:
                    callback({
                        'success': False,
                        'error': 'unknown',
                        'message': f'An unexpected error occurred: {str(e)}'
                    })
        
        # Run forgot password request in a separate thread
        Clock.schedule_once(lambda dt: _forgot_password(), 0) 
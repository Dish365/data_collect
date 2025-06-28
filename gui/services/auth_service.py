import requests
import json
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from requests.exceptions import RequestException, Timeout, ConnectionError
from services.database import DatabaseService

class AuthService:
    def __init__(self):
        self.store = JsonStore('auth.json')
        self.base_url = 'http://127.0.0.1:8000'  # Standardized backend URL
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
    
    def register(self, username, email, password, password2, first_name="", last_name="", institution="", role="researcher", callback=None):
        """Register new user with backend asynchronously"""
        def _register():
            try:
                if not self._check_network_connectivity():
                    if callback:
                        callback({'success': False, 'error': 'network_unavailable', 'message': 'No network connection.'})
                    return

                registration_data = {
                    'username': username, 'email': email,
                    'password': password, 'password2': password2, 'role': role
                }
                if first_name: registration_data['first_name'] = first_name
                if last_name: registration_data['last_name'] = last_name
                if institution: registration_data['institution'] = institution

                response = requests.post(
                    f'{self.base_url}/auth/register/',
                    json=registration_data,
                    timeout=30
                )

                if response.status_code == 201:
                    data = response.json()
                    self.token = data.get('token')
                    self.user_data = data.get('user', {})
                    self.store.put('auth', token=self.token, username=username, user_data=json.dumps(self.user_data))
                    if callback:
                        callback({'success': True, 'data': data})
                else:
                    error_data = response.json()
                    if callback:
                        callback({'success': False, 'error': 'registration_failed', 'message': error_data, 'status_code': response.status_code})

            except (Timeout, ConnectionError) as e:
                if callback:
                    callback({'success': False, 'error': 'network_error', 'message': str(e)})
            except Exception as e:
                if callback:
                    callback({'success': False, 'error': 'unknown', 'message': str(e)})

        Clock.schedule_once(lambda dt: _register(), 0)
    
    def logout(self):
        """Logout user, clear stored credentials, and clear the sync queue."""
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
        
        # Get user ID before clearing token
        user_id = None
        if self.user_data:
            user_id = self.user_data.get('id')
        
        self.token = None
        self.user_data = None
        if self.store.exists('auth'):
            self.store.delete('auth')

        # Clear user-specific data from database
        if user_id:
            db_service = DatabaseService()
            db_service.clear_user_data(user_id)
        else:
            # Fallback: clear the sync queue if we can't identify the user
            db_service = DatabaseService()
            db_service.clear_sync_queue()
    
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
            
            # Handle empty responses for methods like DELETE
            if response.status_code == 204:
                return {}

            return response.json()
            
        except ConnectionError:
            return {"error": "network_unavailable", "message": "Working in offline mode"}
        except Timeout:
            return {"error": "timeout", "message": "Request timed out"}
        except requests.exceptions.HTTPError as e:
            # Try to parse the JSON error response from the server
            try:
                error_body = e.response.json()
            except json.JSONDecodeError:
                error_body = e.response.text
            return {"error": "http_error", "message": str(e), "status_code": e.response.status_code, "details": error_body}
        except RequestException as e:
            return {"error": "request_failed", "message": str(e)}
        except Exception as e:
            return {"error": "unknown", "message": str(e)}
    
    def forgot_password(self, username_or_email, callback=None):
        """Handles forgot password request asynchronously"""
        def _forgot_password():
            try:
                if not self._check_network_connectivity():
                    if callback:
                        callback({'success': False, 'error': 'network_unavailable', 'message': 'No network connection.'})
                    return

                response = requests.post(
                    f'{self.base_url}/auth/forgot-password/',
                    json={'username_or_email': username_or_email},
                    timeout=30
                )
                
                if response.status_code == 200:
                    if callback:
                        callback({'success': True, 'message': response.json().get('message')})
                else:
                    if callback:
                        callback({'success': False, 'error': 'request_failed', 'message': response.json().get('message', 'An error occurred.')})

            except (Timeout, ConnectionError) as e:
                if callback:
                    callback({'success': False, 'error': 'network_error', 'message': str(e)})
            except Exception as e:
                if callback:
                    callback({'success': False, 'error': 'unknown', 'message': str(e)})

        Clock.schedule_once(lambda dt: _forgot_password(), 0)

    def change_password(self, old_password, new_password, callback=None):
        """Handles password change request asynchronously"""
        def _change_password():
            try:
                token = self.get_token()
                if not token:
                    if callback:
                        callback({'success': False, 'error': 'not_authenticated', 'message': 'User not authenticated.'})
                    return

                response = self.make_authenticated_request(
                    'auth/change-password/',
                    method='POST',
                    data={'old_password': old_password, 'new_password': new_password}
                )

                if 'error' not in response:
                    if callback:
                        callback({'success': True, 'message': response.get('message', 'Password changed successfully.')})
                else:
                    if callback:
                        callback({'success': False, 'error': 'change_failed', 'message': response.get('message', 'Failed to change password.')})
            
            except Exception as e:
                 if callback:
                    callback({'success': False, 'error': 'unknown', 'message': str(e)})
        
        Clock.schedule_once(lambda dt: _change_password(), 0)

    def update_profile(self, profile_data, callback=None):
        """Handles user profile update request asynchronously"""
        def _update_profile():
            try:
                token = self.get_token()
                if not token:
                    if callback:
                        callback({'success': False, 'error': 'not_authenticated', 'message': 'User not authenticated.'})
                    return

                response = self.make_authenticated_request(
                    'auth/profile/',
                    method='PUT',
                    data=profile_data
                )

                if 'error' not in response:
                    # Update local user data
                    self.user_data = response
                    self.store.put('auth', token=self.get_token(), user_data=json.dumps(self.user_data))
                    if callback:
                        callback({'success': True, 'user_data': response})
                else:
                    if callback:
                        callback({'success': False, 'error': 'update_failed', 'message': response.get('message', 'Failed to update profile.')})
            
            except Exception as e:
                 if callback:
                    callback({'success': False, 'error': 'unknown', 'message': str(e)})

        Clock.schedule_once(lambda dt: _update_profile(), 0) 
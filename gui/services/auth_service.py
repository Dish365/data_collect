import requests
from kivy.storage.jsonstore import JsonStore

class AuthService:
    def __init__(self):
        self.store = JsonStore('auth.json')
        self.base_url = 'http://localhost:8000/api'  # Fixed: auth endpoints are at /api/auth/
        self.token = None
    
    def authenticate(self, username, password):
        """Authenticate user with backend"""
        try:
            response = requests.post(
                f'{self.base_url}/auth/login/',
                json={'username': username, 'password': password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                self.store.put('auth', token=self.token, username=username)
                return True
            return False
        except requests.RequestException:
            # Handle offline mode - check local storage
            if self.store.exists('auth'):
                auth_data = self.store.get('auth')
                if auth_data.get('username') == username:
                    self.token = auth_data.get('token')
                    return True
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
        self.token = None
        if self.store.exists('auth'):
            self.store.delete('auth')
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        return self.token is not None or self.store.exists('auth')
    
    def get_token(self):
        """Get current authentication token"""
        if not self.token and self.store.exists('auth'):
            self.token = self.store.get('auth').get('token')
        return self.token 
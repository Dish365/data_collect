#!/usr/bin/env python
"""
Test script for password reset functionality
"""
import os
import sys
import django
from django.conf import settings

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

import requests
import json
from django.contrib.auth import get_user_model
from authentication.models import PasswordResetToken

User = get_user_model()

def test_password_reset():
    """Test the complete password reset flow"""
    base_url = 'http://127.0.0.1:8000'
    
    print("=== Testing Password Reset Functionality ===\n")
    
    # 1. Create a test user
    print("1. Creating test user...")
    test_user_data = {
        'username': 'testresetuser',
        'email': 'test.reset@example.com',
        'password': 'testpass123',
        'password2': 'testpass123',
        'first_name': 'Test',
        'last_name': 'Reset',
        'institution': 'Test University'
    }
    
    try:
        # Try to delete existing test user
        User.objects.filter(username='testresetuser').delete()
        User.objects.filter(email='test.reset@example.com').delete()
    except:
        pass
    
    # Register the test user
    response = requests.post(f'{base_url}/auth/register/', json=test_user_data)
    if response.status_code == 201:
        print("✅ Test user created successfully")
        user_data = response.json()
        print(f"   User ID: {user_data['user']['id']}")
    else:
        print(f"❌ Failed to create test user: {response.status_code}")
        print(f"   Response: {response.text}")
        return
    
    # 2. Test forgot password request
    print("\n2. Testing forgot password request...")
    forgot_request = {
        'username_or_email': 'test.reset@example.com'
    }
    
    response = requests.post(f'{base_url}/auth/forgot-password/', json=forgot_request)
    if response.status_code == 200:
        print("✅ Forgot password request successful")
        message = response.json()['message']
        print(f"   Message: {message}")
        
        # Extract token from development message
        if 'Password reset token:' in message:
            token = message.split('Password reset token: ')[1].split(' ')[0]
            print(f"   Token: {token}")
        else:
            print("❌ No token found in response")
            return
    else:
        print(f"❌ Forgot password request failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return
    
    # 3. Test password reset with token
    print("\n3. Testing password reset with token...")
    reset_request = {
        'token': token,
        'new_password': 'newpass123',
        'new_password2': 'newpass123'
    }
    
    response = requests.post(f'{base_url}/auth/reset-password/', json=reset_request)
    if response.status_code == 200:
        print("✅ Password reset successful")
        message = response.json()['message']
        print(f"   Message: {message}")
    else:
        print(f"❌ Password reset failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return
    
    # 4. Test login with new password
    print("\n4. Testing login with new password...")
    login_request = {
        'username': 'testresetuser',
        'password': 'newpass123'
    }
    
    response = requests.post(f'{base_url}/auth/login/', json=login_request)
    if response.status_code == 200:
        print("✅ Login with new password successful")
        login_data = response.json()
        print(f"   Token: {login_data['token'][:20]}...")
    else:
        print(f"❌ Login with new password failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return
    
    # Cleanup
    print("\n5. Cleaning up...")
    try:
        User.objects.filter(username='testresetuser').delete()
        print("✅ Test user cleaned up")
    except:
        print("⚠️  Could not clean up test user")
    
    print("\n=== Password Reset Test Complete ===")

if __name__ == '__main__':
    test_password_reset() 
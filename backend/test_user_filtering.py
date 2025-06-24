#!/usr/bin/env python
"""
Test script to verify user filtering is working correctly.
Run this after creating some test data.
"""

import os
import django

# Setup Django first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

# Now import Django modules after setup
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from projects.models import Project
from forms.models import Question
from responses.models import Response

User = get_user_model()

def test_user_filtering():
    """Test that users only see their own data"""
    print("Testing user filtering...")
    
    # Create test users
    user1 = User.objects.create_user(
        username='testuser1',
        email='test1@example.com',
        password='testpass123'
    )
    
    user2 = User.objects.create_user(
        username='testuser2', 
        email='test2@example.com',
        password='testpass123'
    )
    
    # Create projects for each user
    project1 = Project.objects.create(
        name='User 1 Project',
        description='Project created by user 1',
        created_by=user1
    )
    
    project2 = Project.objects.create(
        name='User 2 Project',
        description='Project created by user 2', 
        created_by=user2
    )
    
    # Create API clients
    client1 = APIClient()
    client2 = APIClient()
    
    # Get tokens
    token1 = Token.objects.create(user=user1)
    token2 = Token.objects.create(user=user2)
    
    # Authenticate clients
    client1.credentials(HTTP_AUTHORIZATION=f'Token {token1.key}')
    client2.credentials(HTTP_AUTHORIZATION=f'Token {token2.key}')
    
    # Test project filtering
    print("\nTesting project filtering...")
    
    # User 1 should only see their own project
    response1 = client1.get('/api/v1/projects/')
    print(f"User 1 projects: {response1.status_code}")
    if response1.status_code == 200:
        projects1 = response1.json()
        print(f"User 1 sees {len(projects1['results'])} projects")
        for project in projects1['results']:
            print(f"  - {project['name']}")
    
    # User 2 should only see their own project
    response2 = client2.get('/api/v1/projects/')
    print(f"User 2 projects: {response2.status_code}")
    if response2.status_code == 200:
        projects2 = response2.json()
        print(f"User 2 sees {len(projects2['results'])} projects")
        for project in projects2['results']:
            print(f"  - {project['name']}")
    
    # Clean up
    user1.delete()
    user2.delete()
    
    print("\nUser filtering test completed!")

if __name__ == '__main__':
    test_user_filtering() 
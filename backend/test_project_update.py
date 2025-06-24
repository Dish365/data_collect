#!/usr/bin/env python
"""
Test script to verify project update functionality is working correctly.
"""

import os
import django

# Setup Django first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

# Now import Django modules after setup
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from projects.models import Project

User = get_user_model()

def test_project_update():
    """Test that project update functionality works correctly"""
    print("Testing project update functionality...")
    
    # Create test user
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    
    # Create a test project
    project = Project.objects.create(
        name='Original Project Name',
        description='Original description',
        created_by=user
    )
    
    print(f"Created project: {project.name}")
    
    # Create API client
    client = APIClient()
    
    # Get token
    token = Token.objects.create(user=user)
    
    # Authenticate client
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    
    # Test project update
    print("\nTesting project update...")
    
    update_data = {
        'name': 'Updated Project Name',
        'description': 'Updated description'
    }
    
    response = client.patch(f'/api/v1/projects/{project.id}/', update_data, format='json')
    print(f"Update response status: {response.status_code}")
    
    if response.status_code == 200:
        updated_project = response.json()
        print(f"Updated project name: {updated_project['name']}")
        print(f"Updated project description: {updated_project['description']}")
        print(f"Sync status: {updated_project['sync_status']}")
        print("✅ Project update successful!")
    else:
        print(f"❌ Update failed: {response.content}")
    
    # Test duplicate name validation
    print("\nTesting duplicate name validation...")
    
    # Create another project
    project2 = Project.objects.create(
        name='Another Project',
        description='Another description',
        created_by=user
    )
    
    # Try to update project2 with the same name as project1
    duplicate_data = {
        'name': 'Updated Project Name'  # Same name as updated project1
    }
    
    response = client.patch(f'/api/v1/projects/{project2.id}/', duplicate_data, format='json')
    print(f"Duplicate name test response status: {response.status_code}")
    
    if response.status_code == 400:
        print("✅ Duplicate name validation working!")
    else:
        print(f"❌ Duplicate name validation failed: {response.content}")
    
    # Clean up
    user.delete()
    
    print("\nProject update test completed!")

if __name__ == '__main__':
    test_project_update() 
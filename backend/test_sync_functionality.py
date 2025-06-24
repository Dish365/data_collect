#!/usr/bin/env python
"""
Test script to verify sync functionality is working correctly.
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
from sync.models import SyncQueue
from projects.models import Project

User = get_user_model()

def test_sync_functionality():
    """Test that sync functionality works correctly"""
    print("Testing sync functionality...")
    
    # Create test user
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    
    # Create a test project
    project = Project.objects.create(
        name='Test Project',
        description='Test project for sync',
        created_by=user
    )
    
    print(f"Created project: {project.name}")
    
    # Create API client
    client = APIClient()
    
    # Get token
    token = Token.objects.create(user=user)
    
    # Authenticate client
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    
    # Test creating a sync queue item
    print("\nTesting sync queue item creation...")
    
    sync_data = {
        'table_name': 'projects',
        'record_id': str(project.id),
        'operation': 'update',
        'data': {'name': 'Updated Project Name'},
        'priority': 1
    }
    
    response = client.post('/api/sync/sync-queue/', sync_data, format='json')
    print(f"Create sync item response status: {response.status_code}")
    
    if response.status_code == 201:
        sync_item = response.json()
        print(f"Created sync item ID: {sync_item['id']}")
        print(f"Status: {sync_item['status']}")
        print("✅ Sync item creation successful!")
    else:
        print(f"❌ Sync item creation failed: {response.content}")
        return
    
    # Test getting pending sync items
    print("\nTesting get pending sync items...")
    
    response = client.get('/api/sync/sync-queue/?status=pending')
    print(f"Get pending items response status: {response.status_code}")
    
    if response.status_code == 200:
        items = response.json()
        print(f"Found {len(items['results'])} pending items")
        print("✅ Get pending items successful!")
    else:
        print(f"❌ Get pending items failed: {response.content}")
    
    # Test process pending action
    print("\nTesting process pending action...")
    
    response = client.post('/api/sync/sync-queue/process_pending/')
    print(f"Process pending response status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Processed {result['total_processed']} items")
        print("✅ Process pending successful!")
    else:
        print(f"❌ Process pending failed: {response.content}")
    
    # Test pending count action
    print("\nTesting pending count action...")
    
    response = client.get('/api/sync/sync-queue/pending_count/')
    print(f"Pending count response status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Pending count: {result['pending_count']}")
        print("✅ Pending count successful!")
    else:
        print(f"❌ Pending count failed: {response.content}")
    
    # Clean up
    user.delete()
    
    print("\nSync functionality test completed!")

if __name__ == '__main__':
    test_sync_functionality() 
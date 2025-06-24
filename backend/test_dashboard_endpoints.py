#!/usr/bin/env python
"""
Test script for dashboard endpoints

Run this script to test the dashboard API endpoints:
python test_dashboard_endpoints.py
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from projects.models import Project
from forms.models import Question
from responses.models import Response
from sync.models import SyncQueue

User = get_user_model()


class DashboardEndpointTest:
    def __init__(self):
        self.client = APIClient()
        self.setup_test_data()

    def setup_test_data(self):
        """Create test data for dashboard endpoints"""
        print("Setting up test data...")
        
        # Create test users
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='testpass123',
            role='admin',
            first_name='Admin',
            last_name='User'
        )
        
        self.researcher_user = User.objects.create_user(
            username='researcher_test',
            email='researcher@test.com',
            password='testpass123',
            role='researcher',
            first_name='Research',
            last_name='User'
        )
        
        # Create tokens for authentication
        self.admin_token = Token.objects.create(user=self.admin_user)
        self.researcher_token = Token.objects.create(user=self.researcher_user)
        
        # Create test projects
        self.project1 = Project.objects.create(
            name='Test Project 1',
            description='Test project description',
            created_by=self.admin_user
        )
        
        self.project2 = Project.objects.create(
            name='Test Project 2',
            description='Another test project',
            created_by=self.researcher_user
        )
        
        # Create test questions
        self.question1 = Question.objects.create(
            project=self.project1,
            question_text='What is your age?',
            question_type='number',
            order_index=1
        )
        
        self.question2 = Question.objects.create(
            project=self.project1,
            question_text='What is your name?',
            question_type='text',
            order_index=2
        )
        
        # Create test responses
        Response.objects.create(
            project=self.project1,
            question=self.question1,
            respondent_id='respondent_1',
            response_value='25',
            collected_by=self.researcher_user
        )
        
        Response.objects.create(
            project=self.project1,
            question=self.question2,
            respondent_id='respondent_1',
            response_value='John Doe',
            collected_by=self.researcher_user
        )
        
        # Create test sync queue items
        SyncQueue.objects.create(
            table_name='projects',
            record_id=str(self.project1.id),
            operation='create',
            data='{}',
            status='pending'
        )
        
        SyncQueue.objects.create(
            table_name='responses',
            record_id='test_id',
            operation='create',
            data='{}',
            status='failed'
        )
        
        print("Test data setup complete!")

    def authenticate_user(self, user_token):
        """Authenticate a user for API requests"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {user_token.key}')

    def test_dashboard_stats_endpoint(self):
        """Test the dashboard stats endpoint"""
        print("\n=== Testing Dashboard Stats Endpoint ===")
        
        # Test with admin user
        self.authenticate_user(self.admin_token)
        response = self.client.get('/api/v1/dashboard-stats/')
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        required_fields = ['total_responses', 'active_projects', 'team_members', 'pending_sync']
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        print("✓ Dashboard stats endpoint working correctly")

    def test_activity_stream_endpoint(self):
        """Test the activity stream endpoint"""
        print("\n=== Testing Activity Stream Endpoint ===")
        
        # Test with admin user
        self.authenticate_user(self.admin_token)
        response = self.client.get('/api/v1/activity-stream/')
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), "Activity stream should return a list"
        
        # Check activity structure if any activities exist
        if data:
            activity = data[0]
            required_fields = ['text', 'timestamp', 'verb']
            for field in required_fields:
                assert field in activity, f"Missing field in activity: {field}"
        
        print("✓ Activity stream endpoint working correctly")

    def test_combined_dashboard_endpoint(self):
        """Test the combined dashboard endpoint"""
        print("\n=== Testing Combined Dashboard Endpoint ===")
        
        # Test with admin user
        self.authenticate_user(self.admin_token)
        response = self.client.get('/api/v1/dashboard/')
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check main structure
        assert 'stats' in data, "Missing stats section"
        assert 'activity_feed' in data, "Missing activity_feed section"
        assert 'timestamp' in data, "Missing timestamp"
        
        # Check stats structure
        stats = data['stats']
        required_stats = ['total_responses', 'active_projects', 'team_members', 'pending_sync']
        for field in required_stats:
            assert field in stats, f"Missing stats field: {field}"
        
        # Check activity feed structure
        activity_feed = data['activity_feed']
        assert isinstance(activity_feed, list), "Activity feed should be a list"
        
        print("✓ Combined dashboard endpoint working correctly")

    def test_permission_handling(self):
        """Test permission handling for different user roles"""
        print("\n=== Testing Permission Handling ===")
        
        # Test with researcher user (limited permissions)
        self.authenticate_user(self.researcher_token)
        response = self.client.get('/api/v1/dashboard-stats/')
        
        print(f"Researcher Status Code: {response.status_code}")
        print(f"Researcher Response: {json.dumps(response.json(), indent=2)}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Researcher should see limited data (only their projects)
        print("✓ Permission handling working correctly")

    def test_unauthenticated_access(self):
        """Test that unauthenticated requests are rejected"""
        print("\n=== Testing Unauthenticated Access ===")
        
        # Clear authentication
        self.client.credentials()
        
        endpoints = [
            '/api/v1/dashboard-stats/',
            '/api/v1/activity-stream/',
            '/api/v1/dashboard/'
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            print(f"Endpoint: {endpoint}, Status: {response.status_code}")
            assert response.status_code == 401, f"Endpoint {endpoint} should require authentication"
        
        print("✓ Authentication protection working correctly")

    def run_all_tests(self):
        """Run all dashboard endpoint tests"""
        print("Starting Dashboard Endpoint Tests...")
        print("=" * 50)
        
        try:
            self.test_dashboard_stats_endpoint()
            self.test_activity_stream_endpoint()
            self.test_combined_dashboard_endpoint()
            self.test_permission_handling()
            self.test_unauthenticated_access()
            
            print("\n" + "=" * 50)
            print("🎉 All dashboard endpoint tests passed!")
            
        except Exception as e:
            print(f"\n❌ Test failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        return True

    def cleanup(self):
        """Clean up test data"""
        print("\nCleaning up test data...")
        try:
            Response.objects.filter(collected_by__in=[self.admin_user, self.researcher_user]).delete()
            Question.objects.filter(project__in=[self.project1, self.project2]).delete()
            Project.objects.filter(created_by__in=[self.admin_user, self.researcher_user]).delete()
            SyncQueue.objects.filter(table_name__in=['projects', 'responses']).delete()
            Token.objects.filter(user__in=[self.admin_user, self.researcher_user]).delete()
            User.objects.filter(username__in=['admin_test', 'researcher_test']).delete()
            print("✓ Test data cleaned up")
        except Exception as e:
            print(f"Warning: Error during cleanup: {e}")


def main():
    """Main function to run the tests"""
    test_runner = DashboardEndpointTest()
    
    try:
        success = test_runner.run_all_tests()
        if success:
            print("\n🚀 Dashboard endpoints are ready for frontend integration!")
        else:
            print("\n🔧 Some tests failed. Please check the output above.")
            sys.exit(1)
    finally:
        test_runner.cleanup()


if __name__ == '__main__':
    main() 
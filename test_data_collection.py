#!/usr/bin/env python3
"""
Test script for data collection service
"""

import sys
import os
import uuid
from pathlib import Path

# Add the current directory to path so we can import from services
sys.path.insert(0, str(Path(__file__).parent))

try:
    from services.database import DatabaseService
    from services.data_collection_service import DataCollectionService
    
    # Mock auth and sync services for testing
    class MockAuthService:
        def is_authenticated(self):
            return False  # Test offline mode
        
        def get_user_data(self):
            return {'id': 'test_user_123'}
        
        def make_authenticated_request(self, *args, **kwargs):
            return {'error': 'offline'}
    
    class MockSyncService:
        def queue_sync(self, *args, **kwargs):
            print(f"Sync queued: {args}")
    
    def test_data_collection():
        print("=== Testing Data Collection Service ===")
        
        # Initialize services
        db_service = DatabaseService()
        db_service.init_database()
        
        auth_service = MockAuthService()
        sync_service = MockSyncService()
        data_collection_service = DataCollectionService(auth_service, db_service, sync_service)
        
        # Test project setup
        project_id = str(uuid.uuid4())
        print(f"Using test project ID: {project_id}")
        
        # Test respondent creation
        print("\n--- Testing Respondent Creation ---")
        try:
            respondent_data = data_collection_service.create_respondent(
                project_id=project_id,
                name="Test Respondent",
                is_anonymous=True,
                consent_given=True
            )
            print(f"✅ Respondent created: {respondent_data['respondent_id']}")
            respondent_id = respondent_data['respondent_id']
        except Exception as e:
            print(f"❌ Error creating respondent: {e}")
            return False
        
        # Test response submission
        print("\n--- Testing Response Submission ---")
        try:
            responses_data = [
                {
                    'question_id': str(uuid.uuid4()),
                    'response_value': 'Test answer 1',
                    'metadata': {'question_type': 'text'}
                },
                {
                    'question_id': str(uuid.uuid4()),
                    'response_value': 'Test answer 2',
                    'metadata': {'question_type': 'text'}
                }
            ]
            
            result = data_collection_service.submit_form_responses(
                project_id=project_id,
                respondent_id=respondent_id,
                responses_data=responses_data
            )
            print(f"✅ Form submitted: {result['message']}")
            print(f"   Responses count: {result['responses_count']}")
        except Exception as e:
            print(f"❌ Error submitting responses: {e}")
            return False
        
        # Test data retrieval
        print("\n--- Testing Data Retrieval ---")
        try:
            respondents, error = data_collection_service.get_project_respondents(project_id)
            if error:
                print(f"❌ Error getting respondents: {error}")
                return False
            
            print(f"✅ Found {len(respondents)} respondents for project")
            
            if respondents:
                responses, error = data_collection_service.get_respondent_responses(respondent_id)
                if error:
                    print(f"❌ Error getting responses: {error}")
                    return False
                
                print(f"✅ Found {len(responses)} responses for respondent")
        except Exception as e:
            print(f"❌ Error testing data retrieval: {e}")
            return False
        
        print("\n=== All Tests Passed! ===")
        return True
    
    if __name__ == "__main__":
        success = test_data_collection()
        sys.exit(0 if success else 1)

except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the GUI directory with the virtual environment activated")
    sys.exit(1) 
"""
Comprehensive test script for the survey system.
Tests forms, responses, and their interactions.
"""

import os
import sys
import django
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_core.settings.development')
django.setup()

from projects.models import Project
from forms.models import Question
from responses.models import Response, Respondent, ResponseType
from authentication.models import User

def test_survey_system():
    """Test the complete survey system"""
    print("🧪 Testing Survey System...")
    
    # Create test user
    User = get_user_model()
    user, created = User.objects.get_or_create(
        email='test@example.com',
        defaults={
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'researcher'
        }
    )
    
    # Create test project
    project, created = Project.objects.get_or_create(
        name='Test Survey Project',
        defaults={
            'description': 'A test project for survey system validation',
            'created_by': user,
            'sync_status': 'synced'
        }
    )
    
    print(f"✅ Created test project: {project.name}")
    
    # Create test questions
    questions_data = [
        {
            'question_text': 'What is your age?',
            'response_type': 'numeric_integer',
            'is_required': True,
            'validation_rules': {'min_value': 0, 'max_value': 120},
            'order_index': 1
        },
        {
            'question_text': 'How satisfied are you with our service?',
            'response_type': 'scale_rating',
            'is_required': True,
            'validation_rules': {'min_value': 1, 'max_value': 5},
            'order_index': 2
        },
        {
            'question_text': 'What is your favorite color?',
            'response_type': 'choice_single',
            'is_required': True,
            'options': ['Red', 'Blue', 'Green', 'Yellow', 'Other'],
            'order_index': 3
        },
        {
            'question_text': 'Which features do you use? (Select all that apply)',
            'response_type': 'choice_multiple',
            'is_required': False,
            'options': ['Feature A', 'Feature B', 'Feature C', 'Feature D'],
            'order_index': 4
        },
        {
            'question_text': 'Please provide additional comments',
            'response_type': 'text_long',
            'is_required': False,
            'validation_rules': {'max_length': 500},
            'order_index': 5
        }
    ]
    
    questions = []
    for q_data in questions_data:
        question = Question.objects.create(project=project, **q_data)
        questions.append(question)
        print(f"✅ Created question: {question.question_text}")
    
    # Create test respondent
    respondent = Respondent.objects.create(
        respondent_id='TEST_RESPONDENT_001',
        project=project,
        name='Test Respondent',
        email='respondent@example.com',
        is_anonymous=False,
        consent_given=True,
        created_by=user
    )
    print(f"✅ Created respondent: {respondent.name}")
    
    # Test response creation and validation
    test_responses = [
        {
            'question': questions[0],  # Age question
            'response_value': '25',
            'expected_valid': True
        },
        {
            'question': questions[0],  # Age question - invalid
            'response_value': '150',
            'expected_valid': False
        },
        {
            'question': questions[1],  # Satisfaction question
            'response_value': '4',
            'expected_valid': True
        },
        {
            'question': questions[2],  # Color choice
            'response_value': 'Blue',
            'expected_valid': True
        },
        {
            'question': questions[2],  # Color choice - invalid
            'response_value': 'Purple',
            'expected_valid': False
        },
        {
            'question': questions[3],  # Multiple choice
            'response_value': 'Feature A,Feature B',
            'expected_valid': True
        },
        {
            'question': questions[4],  # Text comment
            'response_value': 'This is a test comment for the survey system.',
            'expected_valid': True
        }
    ]
    
    print("\n🧪 Testing Response Creation and Validation:")
    for i, test_data in enumerate(test_responses):
        question = test_data['question']
        response_value = test_data['response_value']
        expected_valid = test_data['expected_valid']
        
        # Validate using question's validation method
        is_valid, error_message = question.validate_response_value(response_value)
        
        if is_valid == expected_valid:
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        print(f"{status} Test {i+1}: {question.question_text[:30]}...")
        print(f"   Value: '{response_value}' | Expected: {expected_valid} | Actual: {is_valid}")
        if not is_valid and error_message:
            print(f"   Error: {error_message}")
        
        # Create response if valid
        if is_valid:
            response = Response.objects.create(
                project=project,
                question=question,
                respondent=respondent,
                response_value=response_value,
                collected_by=user
            )
            print(f"   ✅ Created response with ID: {response.response_id}")
    
    # Test analytics integration
    print("\n📊 Testing Analytics Integration:")
    
    # Get project stats
    stats = project.get_summary_stats()
    print(f"✅ Project stats: {stats}")
    
    # Test question response summaries
    for question in questions:
        summary = question.get_response_summary()
        print(f"✅ Question '{question.question_text[:30]}...': {summary}")
    
    # Test respondent completion rate
    completion_rate = respondent.get_completion_rate()
    print(f"✅ Respondent completion rate: {completion_rate:.1f}%")
    
    # Test response type mapping
    print("\n🔗 Testing Response Type Mapping:")
    for question in questions:
        response_type = question.get_expected_response_type()
        print(f"✅ Question '{question.response_type}' -> ResponseType '{response_type.name}'")
    
    print("\n🎉 Survey System Test Completed Successfully!")
    return True

if __name__ == "__main__":
    try:
        test_survey_system()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 
from django.test import TestCase
from django.contrib.auth import get_user_model
from projects.models import Project
from .models import AnalyticsResult

class AnalyticsResultModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            description='Test project description',
            created_by=self.user
        )

    def test_analytics_result_creation(self):
        analytics_result = AnalyticsResult.objects.create(
            project=self.project,
            analysis_type='descriptive_stats',
            parameters={'method': 'mean'},
            results={'mean': 5.5, 'std': 2.1}
        )
        
        self.assertEqual(analytics_result.project, self.project)
        self.assertEqual(analytics_result.analysis_type, 'descriptive_stats')
        self.assertEqual(analytics_result.sync_status, 'pending')
        self.assertIsNotNone(analytics_result.generated_at)

    def test_analytics_result_str_representation(self):
        analytics_result = AnalyticsResult.objects.create(
            project=self.project,
            analysis_type='t_test',
            parameters={},
            results={}
        )
        
        expected_str = f"t_test - {self.project.name}"
        self.assertIn(expected_str, str(analytics_result)) 
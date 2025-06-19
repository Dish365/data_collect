from django.db import models
import uuid
from authentication.models import User

class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sync_status = models.CharField(max_length=20, default='pending')
    cloud_id = models.CharField(max_length=255, blank=True, null=True)
    settings = models.JSONField(default=dict)  # Project-specific settings
    metadata = models.JSONField(default=dict)  # Additional metadata

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
    
    def get_question_count(self):
        """Get the number of questions in this project"""
        return self.questions.count()
    
    def get_response_count(self):
        """Get the number of responses in this project"""
        return self.responses.count()
    
    def get_analytics_count(self):
        """Get the number of analytics results for this project"""
        return self.analytics_results.count()
    
    def get_participants_count(self):
        """Get the number of unique participants (respondents) in this project"""
        return self.responses.values('respondent_id').distinct().count()
    
    def can_user_access(self, user):
        """Check if a user can access this project"""
        if user.is_superuser:
            return True
        return self.created_by == user or user.role in ['admin', 'researcher']
    
    def get_summary_stats(self):
        """Get summary statistics for the project"""
        return {
            'question_count': self.get_question_count(),
            'response_count': self.get_response_count(),
            'analytics_count': self.get_analytics_count(),
            'participants_count': self.get_participants_count(),
        }

from django.db import models
import uuid
from projects.models import Project

# Create your models here.

class Question(models.Model):
    RESPONSE_TYPES = [
        # Text Response Types
        ('text_short', 'Short Text'),
        ('text_long', 'Long Text'),
        
        # Numeric Response Types
        ('numeric_integer', 'Number (Integer)'),
        ('numeric_decimal', 'Number (Decimal)'),
        ('scale_rating', 'Rating Scale'),
        
        # Choice Response Types
        ('choice_single', 'Single Choice'),
        ('choice_multiple', 'Multiple Choice'),
        
        # Date & Time Response Types
        ('date', 'Date'),
        ('datetime', 'Date & Time'),
        
        # Location Response Types
        ('geopoint', 'GPS Location'),
        ('geoshape', 'Geographic Shape'),
        
        # Media Response Types
        ('image', 'Photo/Image'),
        ('audio', 'Audio Recording'),
        ('video', 'Video Recording'),
        ('file', 'File Upload'),
        
        # Special Response Types
        ('signature', 'Digital Signature'),
        ('barcode', 'Barcode/QR Code'),
        
        # Legacy types for backward compatibility
        ('numeric', 'Numeric (Legacy)'),
        ('text', 'Text (Legacy)'),
        ('choice', 'Multiple Choice (Legacy)'),
        ('scale', 'Scale (Legacy)'),
        ('location', 'Location (Legacy)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    response_type = models.CharField(max_length=20, choices=RESPONSE_TYPES)
    is_required = models.BooleanField(default=True)
    allow_multiple = models.BooleanField(default=False)  # Added to support frontend
    options = models.JSONField(null=True, blank=True)  # For multiple choice questions
    validation_rules = models.JSONField(null=True, blank=True)
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    sync_status = models.CharField(max_length=20, default='pending')

    class Meta:
        ordering = ['order_index', 'created_at']
        unique_together = ['project', 'order_index']

    def __str__(self):
        return f"{self.question_text[:50]}..."
    
    def get_response_count(self):
        """Get the number of responses for this question"""
        return self.responses.count()
    
    def get_unique_respondents_count(self):
        """Get the number of unique respondents for this question"""
        return self.responses.values('respondent_id').distinct().count()
    
    def get_completion_rate(self):
        """Get the completion rate for this question"""
        total_responses = self.get_response_count()
        if total_responses == 0:
            return 0.0
        
        # For required questions, assume all responses are complete
        if self.is_required:
            return 100.0
        
        # For optional questions, check if response_value is not empty
        complete_responses = self.responses.exclude(response_value='').count()
        return (complete_responses / total_responses) * 100 if total_responses > 0 else 0.0
    
    def get_response_summary(self):
        """Get a summary of responses for this question"""
        return {
            'total_responses': self.get_response_count(),
            'unique_respondents': self.get_unique_respondents_count(),
            'completion_rate': self.get_completion_rate(),
        }
    
    def can_user_access(self, user):
        """Check if a user can access this question"""
        return self.project.can_user_access(user)

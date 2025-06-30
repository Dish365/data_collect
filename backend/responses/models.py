from django.db import models
import uuid
from projects.models import Project
from forms.models import Question
from authentication.models import User

class Respondent(models.Model):
    """Model to track individuals who are answering questions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    respondent_id = models.CharField(max_length=255, unique=True, db_index=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='respondents')
    
    # Optional demographic/metadata fields
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    demographics = models.JSONField(default=dict, blank=True)  # age, gender, etc.
    
    # Location information
    location_data = models.JSONField(null=True, blank=True)  # GPS coordinates, address
    
    # Data collection metadata
    created_at = models.DateTimeField(auto_now_add=True)
    last_response_at = models.DateTimeField(null=True, blank=True)
    is_anonymous = models.BooleanField(default=True)
    consent_given = models.BooleanField(default=False)
    
    # Sync and tracking
    sync_status = models.CharField(max_length=20, default='pending')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_respondents')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project']),
            models.Index(fields=['respondent_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        display_name = self.name or f"Respondent {self.respondent_id}"
        return f"{display_name} ({self.project.name})"
    
    def get_response_count(self):
        """Get total number of responses by this respondent"""
        return self.responses.count()
    
    def get_completion_rate(self):
        """Get completion rate for this respondent across all project questions"""
        total_questions = self.project.questions.count()
        answered_questions = self.responses.filter(
            response_value__isnull=False
        ).exclude(response_value='').count()
        
        return (answered_questions / total_questions * 100) if total_questions > 0 else 0
    
    def update_last_response(self):
        """Update the last_response_at timestamp"""
        from django.utils import timezone
        self.last_response_at = timezone.now()
        self.save(update_fields=['last_response_at'])

class Response(models.Model):
    """Restructured Response model with proper responseID and better relationships"""
    # Primary identifiers
    response_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationships
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='responses')
    respondent = models.ForeignKey(Respondent, on_delete=models.CASCADE, related_name='responses')
    
    # Response data
    response_value = models.TextField()
    response_metadata = models.JSONField(default=dict)  # validation, formatting, etc.
    
    # Collection metadata
    collected_at = models.DateTimeField(auto_now_add=True)
    collected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='collected_responses')
    
    # Location and device info
    location_data = models.JSONField(null=True, blank=True)  # GPS coordinates, location name
    device_info = models.JSONField(null=True, blank=True)   # device type, OS, app version
    
    # Data quality and validation
    is_validated = models.BooleanField(default=False)
    validation_errors = models.JSONField(null=True, blank=True)
    data_quality_score = models.FloatField(null=True, blank=True)  # 0-100 quality score
    
    # Sync status
    sync_status = models.CharField(max_length=20, default='pending')
    synced_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-collected_at']
        indexes = [
            models.Index(fields=['project', 'question']),
            models.Index(fields=['respondent']),
            models.Index(fields=['collected_by']),
            models.Index(fields=['collected_at']),
            models.Index(fields=['sync_status']),
        ]
        # Ensure one response per question per respondent
        unique_together = ['question', 'respondent']

    def __str__(self):
        return f"Response {self.response_id} to {self.question.question_text[:30]} by {self.respondent.respondent_id}"
    
    def save(self, *args, **kwargs):
        """Override save to update respondent's last_response_at"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.respondent.update_last_response()
    
    def get_location_summary(self):
        """Get a summary of location data if available"""
        if not self.location_data:
            return None
        
        location = self.location_data
        return {
            'latitude': location.get('latitude'),
            'longitude': location.get('longitude'),
            'location_name': location.get('location_name'),
            'accuracy': location.get('accuracy'),
        }
    
    def get_device_summary(self):
        """Get device information summary"""
        if not self.device_info:
            return None
            
        device = self.device_info
        return {
            'platform': device.get('platform'),
            'device_model': device.get('device_model'),
            'os_version': device.get('os_version'),
            'app_version': device.get('app_version'),
        }
    
    def is_complete(self):
        """Check if the response is complete and valid"""
        return bool(self.response_value and self.response_value.strip())
    
    def can_user_access(self, user):
        """Check if a user can access this response"""
        return self.project.can_user_access(user)
    
    def validate_response(self):
        """Validate response against question's validation rules"""
        validation_errors = []
        
        # Check if required question has a response
        if self.question.is_required and not self.is_complete():
            validation_errors.append("Response is required for this question")
        
        # Check response type specific validation
        if self.question.response_type == 'numeric':
            try:
                float(self.response_value)
            except (ValueError, TypeError):
                validation_errors.append("Response must be a valid number")
        
        elif self.question.response_type == 'choice':
            if self.question.options:
                valid_options = [str(opt) for opt in self.question.options]
                if self.response_value not in valid_options:
                    validation_errors.append(f"Response must be one of: {', '.join(valid_options)}")
        
        # Store validation results
        self.validation_errors = validation_errors if validation_errors else None
        self.is_validated = len(validation_errors) == 0
        
        return self.is_validated
    
    def calculate_quality_score(self):
        """Calculate data quality score (0-100)"""
        score = 100.0
        
        # Deduct points for validation errors
        if self.validation_errors:
            score -= len(self.validation_errors) * 20
        
        # Deduct points for incomplete responses
        if not self.is_complete():
            score -= 30
        
        # Deduct points for missing location data (if location question)
        if self.question.response_type == 'location' and not self.location_data:
            score -= 10
        
        # Add points for having metadata
        if self.response_metadata:
            score += 5
        
        # Ensure score is between 0 and 100
        self.data_quality_score = max(0, min(100, score))
        return self.data_quality_score

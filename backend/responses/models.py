from django.db import models
import uuid
from projects.models import Project
from forms.models import Question
from authentication.models import User

class Response(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='responses')
    respondent_id = models.CharField(max_length=255)
    response_value = models.TextField()
    metadata = models.JSONField(default=dict)  # timestamps, location, device info
    collected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='collected_responses')
    collected_at = models.DateTimeField(auto_now_add=True)
    location_data = models.JSONField(null=True, blank=True)  # GPS coordinates, location name
    sync_status = models.CharField(max_length=20, default='pending')

    class Meta:
        ordering = ['-collected_at']
        indexes = [
            models.Index(fields=['project', 'question']),
            models.Index(fields=['respondent_id']),
            models.Index(fields=['collected_by']),
            models.Index(fields=['collected_at']),
        ]

    def __str__(self):
        return f"Response to {self.question.question_text[:30]} by {self.respondent_id}"
    
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
    
    def get_device_info(self):
        """Get device information from metadata"""
        return self.metadata.get('device_info', {})
    
    def get_collection_time(self):
        """Get the actual collection time from metadata if available"""
        return self.metadata.get('collection_time', self.collected_at)
    
    def is_complete(self):
        """Check if the response is complete"""
        return bool(self.response_value and self.response_value.strip())
    
    def can_user_access(self, user):
        """Check if a user can access this response"""
        return self.project.can_user_access(user)
    
    def get_response_summary(self):
        """Get a summary of the response"""
        return {
            'is_complete': self.is_complete(),
            'has_location': bool(self.location_data),
            'has_device_info': bool(self.get_device_info()),
            'response_length': len(self.response_value) if self.response_value else 0,
        }

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid
import secrets
from datetime import timedelta

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=[
        ('admin', 'Administrator'),
        ('researcher', 'Researcher'),
        ('field_worker', 'Field Worker'),
    ], default='researcher')
    institution = models.CharField(max_length=255, blank=True, help_text="Organization or institution the user belongs to")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.email
    
    def get_projects_count(self):
        """Get the number of projects created by this user"""
        return self.created_projects.count()
    
    def get_responses_collected_count(self):
        """Get the number of responses collected by this user"""
        return self.collected_responses.count()
    
    def get_sync_operations_count(self):
        """Get the number of sync operations initiated by this user"""
        return self.sync_operations.count()
    
    def can_access_project(self, project):
        """Check if this user can access a specific project"""
        if self.is_superuser:
            return True
        if project.created_by == self:
            return True
        if self.role in ['admin', 'researcher']:
            return True
        return False
    
    def can_manage_users(self):
        """Check if this user can manage other users"""
        return self.is_superuser or self.role == 'admin'
    
    def can_create_projects(self):
        """Check if this user can create projects"""
        return self.is_superuser or self.role in ['admin', 'researcher']
    
    def can_collect_data(self):
        """Check if this user can collect data"""
        return self.is_superuser or self.role in ['admin', 'researcher', 'field_worker']
    
    def get_user_summary(self):
        """Get a summary of user activity"""
        return {
            'projects_created': self.get_projects_count(),
            'responses_collected': self.get_responses_collected_count(),
            'sync_operations': self.get_sync_operations_count(),
            'can_manage_users': self.can_manage_users(),
            'can_create_projects': self.can_create_projects(),
            'can_collect_data': self.can_collect_data(),
        }


class PasswordResetToken(models.Model):
    """Model for secure password reset tokens"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)  # 24 hour expiry
        super().save(*args, **kwargs)
    
    def is_valid(self):
        """Check if token is valid (not used and not expired)"""
        return not self.used and timezone.now() < self.expires_at
    
    def mark_used(self):
        """Mark token as used"""
        self.used = True
        self.save()
    
    def __str__(self):
        return f"Reset token for {self.user.email} - {'Valid' if self.is_valid() else 'Invalid'}"

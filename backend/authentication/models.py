from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=[
        ('admin', 'Administrator'),
        ('researcher', 'Researcher'),
        ('field_worker', 'Field Worker'),
    ], default='researcher')
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

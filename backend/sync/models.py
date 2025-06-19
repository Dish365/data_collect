from django.db import models
from django.utils import timezone
from authentication.models import User

class SyncQueue(models.Model):
    OPERATION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('syncing', 'Syncing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    table_name = models.CharField(max_length=255)
    record_id = models.CharField(max_length=255)
    operation = models.CharField(max_length=10, choices=OPERATION_CHOICES)
    data = models.JSONField(null=True, blank=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='sync_operations'
    )
    created_at = models.DateTimeField(default=timezone.now)
    attempts = models.IntegerField(default=0)
    last_attempt = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    priority = models.IntegerField(default=0)  # Higher number = higher priority

    class Meta:
        db_table = 'sync_queue'
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['table_name', 'record_id']),
            models.Index(fields=['priority', 'status']),
            models.Index(fields=['created_by', 'status']),
        ]

    def __str__(self):
        return f"{self.operation} - {self.table_name}:{self.record_id} ({self.status})"
    
    def increment_attempts(self):
        """Increment the number of attempts and update last_attempt"""
        self.attempts += 1
        self.last_attempt = timezone.now()
        self.save(update_fields=['attempts', 'last_attempt'])
    
    def mark_as_failed(self, error_message=""):
        """Mark the sync operation as failed"""
        self.status = 'failed'
        self.error_message = error_message
        self.increment_attempts()
        self.save(update_fields=['status', 'error_message', 'attempts', 'last_attempt'])
    
    def mark_as_completed(self):
        """Mark the sync operation as completed"""
        self.status = 'completed'
        self.save(update_fields=['status'])

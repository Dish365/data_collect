from django.db import models
import uuid
from projects.models import Project

class AnalyticsResult(models.Model):
    ANALYSIS_TYPES = [
        ('descriptive_stats', 'Descriptive Statistics'),
        ('distribution_analysis', 'Distribution Analysis'),
        ('frequency_analysis', 'Frequency Analysis'),
        ('chi_square', 'Chi-Square Test'),
        ('t_test', 'T-Test'),
        ('anova', 'ANOVA'),
        ('correlation', 'Correlation Analysis'),
        ('sentiment_analysis', 'Sentiment Analysis'),
        ('theme_extraction', 'Theme Extraction'),
        ('word_cloud', 'Word Cloud'),
        ('custom', 'Custom Analysis'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='analytics_results')
    analysis_type = models.CharField(max_length=50, choices=ANALYSIS_TYPES)
    parameters = models.JSONField(default=dict)  # Analysis parameters and configuration
    results = models.JSONField(default=dict)  # Analysis results and outputs
    generated_at = models.DateTimeField(auto_now_add=True)
    sync_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        db_table = 'analytics_results'
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['project', 'analysis_type']),
            models.Index(fields=['sync_status', 'generated_at']),
        ]

    def __str__(self):
        return f"{self.analysis_type} - {self.project.name} ({self.generated_at.strftime('%Y-%m-%d %H:%M')})" 
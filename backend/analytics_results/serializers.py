from rest_framework import serializers
from .models import AnalyticsResult

class AnalyticsResultSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = AnalyticsResult
        fields = [
            'id', 'project', 'project_name', 'analysis_type', 
            'parameters', 'results', 'generated_at', 'sync_status'
        ]
        read_only_fields = ['id', 'generated_at'] 
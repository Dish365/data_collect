from rest_framework import serializers
from .models import Project
from authentication.serializers import UserSerializer

class ProjectSerializer(serializers.ModelSerializer):
    created_by_details = UserSerializer(source='created_by', read_only=True)
    question_count = serializers.SerializerMethodField()
    response_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'created_by', 'created_by_details',
            'created_at', 'updated_at', 'sync_status', 'cloud_id',
            'settings', 'metadata', 'question_count', 'response_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'question_count', 'response_count', 'created_by']
        
    def validate_name(self, value):
        """Validate project name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Project name is required.")
        
        # Check for duplicate names within the same user's projects
        user = self.context['request'].user
        project_id = self.instance.id if self.instance else None
        
        # Exclude current project from duplicate check (for updates)
        existing_projects = Project.objects.filter(created_by=user, name__iexact=value.strip())
        if project_id:
            existing_projects = existing_projects.exclude(id=project_id)
        
        if existing_projects.exists():
            raise serializers.ValidationError("A project with this name already exists.")
        
        return value.strip()
    
    def validate_description(self, value):
        """Validate project description"""
        if value and len(value) > 1000:
            raise serializers.ValidationError("Description cannot exceed 1000 characters.")
        return value
        
    def get_question_count(self, obj):
        """Get the number of questions in this project"""
        return obj.questions.count()
    
    def get_response_count(self, obj):
        """Get the number of responses in this project"""
        return obj.responses.count() 
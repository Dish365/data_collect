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
        read_only_fields = ['id', 'created_at', 'updated_at', 'question_count', 'response_count']
        
    def get_question_count(self, obj):
        """Get the number of questions in this project"""
        return obj.questions.count()
    
    def get_response_count(self, obj):
        """Get the number of responses in this project"""
        return obj.responses.count() 
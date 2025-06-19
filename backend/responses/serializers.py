from rest_framework import serializers
from .models import Response
from projects.serializers import ProjectSerializer
from forms.serializers import QuestionSerializer
from authentication.serializers import UserSerializer

class ResponseSerializer(serializers.ModelSerializer):
    project_details = ProjectSerializer(source='project', read_only=True)
    question_details = QuestionSerializer(source='question', read_only=True)
    collected_by_details = UserSerializer(source='collected_by', read_only=True)
    
    class Meta:
        model = Response
        fields = [
            'id', 'project', 'project_details', 'question', 'question_details', 
            'respondent_id', 'response_value', 'metadata', 'collected_by', 
            'collected_by_details', 'collected_at', 'location_data', 'sync_status'
        ]
        read_only_fields = ['id', 'collected_at']
        
    def validate(self, attrs):
        """Validate that question belongs to the specified project"""
        project = attrs.get('project')
        question = attrs.get('question')
        
        if project and question and question.project != project:
            raise serializers.ValidationError(
                "Question must belong to the specified project."
            )
        
        return attrs 
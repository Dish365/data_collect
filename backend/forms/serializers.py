from rest_framework import serializers
from .models import Question
from projects.serializers import ProjectSerializer

class QuestionSerializer(serializers.ModelSerializer):
    project_details = ProjectSerializer(source='project', read_only=True)
    
    class Meta:
        model = Question
        fields = [
            'id', 'project', 'project_details', 'question_text', 'question_type', 
            'is_required', 'options', 'validation_rules', 'order_index', 
            'created_at', 'sync_status'
        ]
        read_only_fields = ['id', 'created_at']
        
    def validate_order_index(self, value):
        """Ensure order_index is unique within the project"""
        project = self.initial_data.get('project')
        if project and value is not None:
            existing_question = Question.objects.filter(
                project=project, 
                order_index=value
            ).exclude(id=self.instance.id if self.instance else None)
            
            if existing_question.exists():
                raise serializers.ValidationError(
                    f"Question with order_index {value} already exists in this project."
                )
        return value 
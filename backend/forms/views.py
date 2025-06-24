from django.shortcuts import render
from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from core.utils.viewsets import BaseModelViewSet
from core.utils.filters import QuestionFilter
from .models import Question
from .serializers import QuestionSerializer

# Create your views here.

class QuestionViewSet(BaseModelViewSet):
    serializer_class = QuestionSerializer
    filterset_class = QuestionFilter
    search_fields = ['question_text', 'project__name']
    ordering_fields = ['question_text', 'order_index', 'created_at']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter questions by projects that belong to the authenticated user.
        Superusers can see all questions, regular users only see questions from their projects.
        """
        user = self.request.user
        if user.is_superuser:
            queryset = Question.objects.all()
        else:
            queryset = Question.objects.filter(project__created_by=user)
        
        # Additional filtering by project_id if provided
        project_id = self.request.query_params.get('project_id', None)
        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset

    def perform_create(self, serializer):
        """Handle question creation with proper validation"""
        # Get the project from the serializer data
        project_id = serializer.validated_data.get('project').id
        user = self.request.user
        
        # Check if user has access to this project
        from projects.models import Project
        try:
            project = Project.objects.get(id=project_id)
            if not project.can_user_access(user):
                raise permissions.PermissionDenied("You don't have permission to add questions to this project.")
        except Project.DoesNotExist:
            raise serializers.ValidationError("Project not found.")
        
        # Set sync status to pending since data has changed
        serializer.save(sync_status='pending')

    def perform_update(self, serializer):
        """Handle question updates with proper validation"""
        question = serializer.instance
        user = self.request.user
        
        # Check if user can update this question
        if not question.can_user_access(user):
            raise permissions.PermissionDenied("You don't have permission to update this question.")
        
        # Set sync status to pending since data has changed
        serializer.save(sync_status='pending')

    def perform_destroy(self, instance):
        """Handle question deletion with proper validation"""
        user = self.request.user
        
        # Check if user can delete this question
        if not instance.can_user_access(user):
            raise permissions.PermissionDenied("You don't have permission to delete this question.")
        
        instance.delete()

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Bulk create multiple questions for a project"""
        user = request.user
        questions_data = request.data
        
        # Validate that we received a list
        if not isinstance(questions_data, list):
            return Response(
                {"error": "Expected a list of questions"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate all questions belong to the same project
        project_ids = set()
        for q_data in questions_data:
            project_id = q_data.get('project')
            if project_id:
                project_ids.add(project_id)
        
        if len(project_ids) != 1:
            return Response(
                {"error": "All questions must belong to the same project"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        project_id = list(project_ids)[0]
        
        # Check if user has access to this project
        from projects.models import Project
        try:
            project = Project.objects.get(id=project_id)
            if not project.can_user_access(user):
                raise permissions.PermissionDenied("You don't have permission to add questions to this project.")
        except Project.DoesNotExist:
            return Response(
                {"error": "Project not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Clear existing questions for this project
        Question.objects.filter(project=project).delete()
        
        # Create new questions
        created_questions = []
        for i, q_data in enumerate(questions_data):
            serializer = self.get_serializer(data=q_data)
            if serializer.is_valid():
                question = serializer.save(sync_status='pending')
                created_questions.append(serializer.data)
            else:
                # If any question fails validation, rollback and return error
                return Response(
                    {"error": f"Validation failed for question {i+1}: {serializer.errors}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(created_questions, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def responses(self, request, pk=None):
        """Get responses for a specific question"""
        question = self.get_object()
        responses = question.responses.all()
        from responses.serializers import ResponseSerializer
        serializer = ResponseSerializer(responses, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get question summary statistics"""
        question = self.get_object()
        return Response(question.get_response_summary())

from django.shortcuts import render
from rest_framework import viewsets, permissions
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

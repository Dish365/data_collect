from django.shortcuts import render
from rest_framework import viewsets
from core.utils.viewsets import BaseModelViewSet
from core.utils.filters import QuestionFilter
from .models import Question
from .serializers import QuestionSerializer

# Create your views here.

class QuestionViewSet(BaseModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    filterset_class = QuestionFilter
    search_fields = ['question_text', 'project__name']
    ordering_fields = ['question_text', 'order_index', 'created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get('project_id', None)
        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)
        return queryset

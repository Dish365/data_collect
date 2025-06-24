from rest_framework import permissions
from core.utils.viewsets import BaseModelViewSet
from core.utils.filters import ResponseFilter
from .models import Response
from .serializers import ResponseSerializer

# Create your views here.

class ResponseViewSet(BaseModelViewSet):
    serializer_class = ResponseSerializer
    filterset_class = ResponseFilter
    search_fields = ['response_value', 'respondent_id', 'question__question_text']
    ordering_fields = ['collected_at', 'respondent_id']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter responses by projects that belong to the authenticated user.
        Superusers can see all responses, regular users only see responses from their projects.
        """
        user = self.request.user
        if user.is_superuser:
            queryset = Response.objects.all()
        else:
            queryset = Response.objects.filter(project__created_by=user)
        
        # Additional filtering by query parameters
        project_id = self.request.query_params.get('project_id', None)
        question_id = self.request.query_params.get('question_id', None)
        respondent_id = self.request.query_params.get('respondent_id', None)

        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)
        if question_id is not None:
            queryset = queryset.filter(question_id=question_id)
        if respondent_id is not None:
            queryset = queryset.filter(respondent_id=respondent_id)

        return queryset

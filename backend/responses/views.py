from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response as DRFResponse
from django.db.models import Count, Avg, Max
from django_core.utils.viewsets import BaseModelViewSet
from django_core.utils.filters import ResponseFilter
from .models import Response, Respondent
from .serializers import ResponseSerializer, RespondentSerializer

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


class RespondentViewSet(BaseModelViewSet):
    serializer_class = RespondentSerializer
    search_fields = ['respondent_id', 'name', 'email']
    ordering_fields = ['created_at', 'last_response_at']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter respondents by projects that belong to the authenticated user.
        Superusers can see all respondents, regular users only see respondents from their projects.
        """
        user = self.request.user
        if user.is_superuser:
            queryset = Respondent.objects.select_related('project', 'created_by').prefetch_related('responses')
        else:
            queryset = Respondent.objects.filter(project__created_by=user).select_related('project', 'created_by').prefetch_related('responses')
        
        # Additional filtering by query parameters
        project_id = self.request.query_params.get('project_id', None)
        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)

        return queryset

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary statistics for respondents"""
        try:
            queryset = self.get_queryset()
            
            total_respondents = queryset.count()
            total_responses = Response.objects.filter(
                respondent__in=queryset
            ).count()
            
            avg_responses_per_respondent = 0
            if total_respondents > 0:
                avg_responses_per_respondent = round(total_responses / total_respondents, 1)
            
            return DRFResponse({
                'total_respondents': total_respondents,
                'total_responses': total_responses,
                'avg_responses_per_respondent': avg_responses_per_respondent
            })
        except Exception as e:
            return DRFResponse({
                'error': f'Failed to get summary: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def responses(self, request, pk=None):
        """Get all responses for a specific respondent with detailed information"""
        try:
            respondent = self.get_object()
            responses = Response.objects.filter(
                respondent=respondent
            ).select_related('question', 'collected_by', 'project').order_by('collected_at')
            
            serializer = ResponseSerializer(responses, many=True)
            return DRFResponse({
                'respondent': RespondentSerializer(respondent).data,
                'responses': serializer.data
            })
        except Exception as e:
            return DRFResponse({
                'error': f'Failed to get responses: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def with_response_counts(self, request):
        """Get respondents with their response counts - optimized for list view"""
        try:
            queryset = self.get_queryset().annotate(
                response_count=Count('responses'),
                last_response_date=Max('responses__collected_at')
            ).order_by('-created_at')
            
            # Pagination
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return DRFResponse(serializer.data)
        except Exception as e:
            return DRFResponse({
                'error': f'Failed to get respondents with counts: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import AnalyticsResult
from .serializers import AnalyticsResultSerializer

class AnalyticsResultViewSet(viewsets.ModelViewSet):
    queryset = AnalyticsResult.objects.all()
    serializer_class = AnalyticsResultSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['project', 'analysis_type', 'sync_status']

    def get_queryset(self):
        queryset = AnalyticsResult.objects.select_related('project')
        return queryset.order_by('-generated_at')

    @action(detail=False, methods=['get'])
    def by_project(self, request):
        """Get analytics results for a specific project"""
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response(
                {'error': 'project_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = self.get_queryset().filter(project_id=project_id)
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def analysis_types(self, request):
        """Get available analysis types"""
        types = [choice[0] for choice in AnalyticsResult.ANALYSIS_TYPES]
        return Response({'analysis_types': types})

    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """Regenerate an analytics result"""
        analytics_result = self.get_object()
        
        # TODO: Implement regeneration logic here
        # This would typically involve calling the analytics engine
        
        return Response({
            'message': 'Analytics result regeneration initiated',
            'id': analytics_result.id
        }) 
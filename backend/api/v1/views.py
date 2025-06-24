"""
Views for API v1.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from forms.models import Question
from forms.serializers import QuestionSerializer
from projects.models import Project
from responses.models import Response as ResponseModel
from sync.models import SyncQueue
from authentication.models import User

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics"""
    user = request.user
    
    # Get user's projects (projects created by user or accessible to user role)
    if user.is_superuser or user.role in ['admin', 'researcher']:
        user_projects = Project.objects.all()
    else:
        user_projects = Project.objects.filter(created_by=user)
    
    # Total responses across user's projects
    total_responses = ResponseModel.objects.filter(
        project__in=user_projects
    ).count()
    
    # Team members (users who have collected responses in these projects)
    team_member_ids = set()
    team_member_ids.update(
        ResponseModel.objects.filter(
            project__in=user_projects,
            collected_by__isnull=False
        ).values_list('collected_by_id', flat=True)
    )
    # Add project creators
    team_member_ids.update(user_projects.values_list('created_by_id', flat=True))
    team_members = len(team_member_ids)
    
    return Response({
        'total_responses': total_responses,
        'team_members': team_members,
        'active_projects': user_projects.count(),
        'pending_sync': SyncQueue.objects.filter(status='pending').count()
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def activity_stream(request):
    """Get recent activity stream"""
    user = request.user
    
    # Get user's projects (projects created by user or accessible to user role)
    if user.is_superuser or user.role in ['admin', 'researcher']:
        user_projects = Project.objects.all()
    else:
        user_projects = Project.objects.filter(created_by=user)
    
    # Get recent activities (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    activities = []
    
    # Recent responses
    recent_responses = ResponseModel.objects.filter(
        project__in=user_projects,
        collected_at__gte=thirty_days_ago
    ).order_by('-collected_at')[:10]
    
    for response in recent_responses:
        activities.append({
            'text': f'New response submitted for {response.project.name}',
            'timestamp': response.collected_at.isoformat(),
            'verb': 'submitted'
        })
    
    # Recent projects
    recent_projects = user_projects.filter(
        created_at__gte=thirty_days_ago
    ).order_by('-created_at')[:5]
    
    for project in recent_projects:
        activities.append({
            'text': f'Project "{project.name}" was created',
            'timestamp': project.created_at.isoformat(),
            'verb': 'created'
        })
    
    # Sort by timestamp (most recent first)
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return Response(activities[:20])  # Return top 20 activities

# Example ViewSet
# class ExampleViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated]
#     queryset = Example.objects.all()
#     serializer_class = ExampleSerializer 

class QuestionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionSerializer

    def get_queryset(self):
        project_id = self.kwargs.get('project_pk')
        return Question.objects.filter(project_id=project_id)

    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_pk')
        project = Project.objects.get(id=project_id)
        serializer.save(project=project)

    @action(detail=False, methods=['get'])
    def reorder(self, request, project_pk=None):
        """Reorder questions within a project"""
        questions = self.get_queryset()
        order_data = request.data.get('order', [])
        
        if not order_data:
            return Response(
                {'error': 'Order data is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update order_index for each question
        for index, question_id in enumerate(order_data):
            Question.objects.filter(id=question_id).update(order_index=index)

        return Response({'status': 'Questions reordered successfully'}) 
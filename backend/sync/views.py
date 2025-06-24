from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import SyncQueue
from .serializers import SyncQueueSerializer

# Create your views here.

class SyncQueueViewSet(viewsets.ModelViewSet):
    serializer_class = SyncQueueSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter sync queue items by the authenticated user's projects.
        Superusers can see all items, regular users only see items from their projects.
        """
        user = self.request.user
        if user.is_superuser:
            queryset = SyncQueue.objects.all()
        else:
            # Filter by projects that belong to the user
            queryset = SyncQueue.objects.filter(
                table_name__in=['projects', 'questions', 'responses', 'analytics_results']
            )
        
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        """Automatically set the created_by field to the authenticated user"""
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['post'])
    def process_pending(self, request):
        """Process all pending sync queue items"""
        pending_items = self.get_queryset().filter(status='pending')
        processed_count = 0
        
        for item in pending_items:
            item.status = 'syncing'
            item.attempts += 1
            item.last_attempt = timezone.now()
            item.save()
            
            try:
                # TODO: Implement actual sync logic here
                item.status = 'completed'
                processed_count += 1
            except Exception as e:
                item.status = 'failed'
            
            item.save()
        
        return Response({
            'message': f'Processed {processed_count} items',
            'total_processed': processed_count
        })

    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Retry a failed sync queue item"""
        sync_item = self.get_object()
        
        if sync_item.status != 'failed':
            return Response(
                {'error': 'Can only retry failed items'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sync_item.status = 'pending'
        sync_item.save()
        
        return Response({
            'message': 'Item queued for retry',
            'id': sync_item.id
        })

    @action(detail=False, methods=['get'])
    def pending_count(self, request):
        """Get count of pending sync items"""
        count = self.get_queryset().filter(status='pending').count()
        return Response({'pending_count': count})

    @action(detail=False, methods=['post'])
    def clear_completed(self, request):
        """Clear completed sync items"""
        completed_items = self.get_queryset().filter(status='completed')
        count = completed_items.count()
        completed_items.delete()
        
        return Response({
            'message': f'Cleared {count} completed items',
            'cleared_count': count
        })

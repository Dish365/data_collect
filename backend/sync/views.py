from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import SyncQueue
from .serializers import SyncQueueSerializer

# Create your views here.

class SyncQueueViewSet(viewsets.ModelViewSet):
    queryset = SyncQueue.objects.all()
    serializer_class = SyncQueueSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = SyncQueue.objects.all()
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by('-created_at')

    @action(detail=False, methods=['post'])
    def process_pending(self, request):
        """Process all pending sync queue items"""
        pending_items = SyncQueue.objects.filter(status='pending')
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

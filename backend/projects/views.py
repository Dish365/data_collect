from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.utils.viewsets import BaseModelViewSet
from core.utils.filters import ProjectFilter
from .models import Project
from .serializers import ProjectSerializer

# Create your views here.

class ProjectViewSet(BaseModelViewSet):
    serializer_class = ProjectSerializer
    filterset_class = ProjectFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter projects by the authenticated user.
        Superusers can see all projects, regular users only see their own.
        """
        user = self.request.user
        if user.is_superuser:
            return Project.objects.all()
        return Project.objects.filter(created_by=user)

    def perform_create(self, serializer):
        """Automatically set the created_by field to the authenticated user"""
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        """Ensure only the project creator can update the project"""
        project = serializer.instance
        user = self.request.user
        
        # Check if user can update this project
        if not project.can_user_access(user):
            raise permissions.PermissionDenied("You don't have permission to update this project.")
        
        # Update sync status to pending since data has changed
        serializer.save(sync_status='pending')

    def perform_destroy(self, instance):
        """Ensure only the project creator can delete the project"""
        user = self.request.user
        
        # Check if user can delete this project
        if not instance.can_user_access(user):
            raise permissions.PermissionDenied("You don't have permission to delete this project.")
        
        instance.delete()

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get project summary statistics"""
        project = self.get_object()
        return Response(project.get_summary_stats())

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get detailed project statistics"""
        project = self.get_object()
        stats = {
            'question_count': project.get_question_count(),
            'response_count': project.get_response_count(),
            'analytics_count': project.get_analytics_count(),
            'participants_count': project.get_participants_count(),
            'created_at': project.created_at,
            'updated_at': project.updated_at,
            'sync_status': project.sync_status,
        }
        return Response(stats)

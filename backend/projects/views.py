from django.shortcuts import render
from django.db import models
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from core.utils.viewsets import BaseModelViewSet
from core.utils.filters import ProjectFilter
from .models import Project, ProjectMember
from .serializers import (
    ProjectSerializer, 
    ProjectMemberSerializer, 
    ProjectMemberInviteSerializer, 
    ProjectMemberUpdateSerializer
)

User = get_user_model()

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
        Users can see projects they created or are members of.
        Superusers can see all projects.
        """
        user = self.request.user
        if user.is_superuser:
            return Project.objects.all()
        
        # Get projects where user is creator or member
        return Project.objects.filter(
            models.Q(created_by=user) | models.Q(members__user=user)
        ).distinct()

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
        
        # Only project creator can delete
        if instance.created_by != user and not user.is_superuser:
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
            'team_members_count': project.get_team_members_count(),
            'created_at': project.created_at,
            'updated_at': project.updated_at,
            'sync_status': project.sync_status,
        }
        return Response(stats)

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get all team members for a project"""
        project = self.get_object()
        
        # Check if user can view team members
        if not project.can_user_access(request.user):
            return Response(
                {'error': 'You do not have permission to view team members'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        team_members = project.get_team_members()
        return Response({
            'team_members': team_members,
            'total_count': len(team_members)
        })

    @action(detail=True, methods=['post'])
    def invite_member(self, request, pk=None):
        """Invite a user to join the project team"""
        project = self.get_object()
        
        # Check if user can manage team members (creator or admin)
        if project.created_by != request.user and not request.user.is_superuser:
            return Response(
                {'error': 'Only project creators can invite team members'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ProjectMemberInviteSerializer(
            data=request.data, 
            context={'project': project}
        )
        
        if serializer.is_valid():
            validated_data = serializer.validated_data
            user_to_invite = validated_data['user_email']  # This is a User object
            role = validated_data['role']
            permissions = validated_data['permissions']
            
            success, result = project.add_team_member(
                user=user_to_invite,
                role=role,
                permissions=permissions,
                actor=request.user
            )
            
            if success:
                # Set the invited_by field
                result.invited_by = request.user
                result.save()
                
                member_serializer = ProjectMemberSerializer(result)
                return Response({
                    'message': 'Team member invited successfully',
                    'member': member_serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'error': result}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'])
    def update_member(self, request, pk=None):
        """Update a team member's role and permissions"""
        project = self.get_object()
        
        # Check if user can manage team members
        if project.created_by != request.user and not request.user.is_superuser:
            return Response(
                {'error': 'Only project creators can update team members'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_to_update = User.objects.get(id=user_id)
            member = project.members.get(user=user_to_update)
            
            serializer = ProjectMemberUpdateSerializer(
                member, 
                data=request.data, 
                partial=True
            )
            
            if serializer.is_valid():
                # Get the old values before saving
                old_role = member.role
                old_permissions = member.get_permissions_list()
                
                serializer.save()
                
                # Create activity record for the update
                project.create_activity(
                    activity_type='member_updated',
                    actor=request.user,
                    target_user=user_to_update,
                    metadata={
                        'old_role': old_role,
                        'new_role': member.role,
                        'old_permissions': old_permissions,
                        'new_permissions': member.get_permissions_list()
                    }
                )
                
                return Response({
                    'message': 'Team member updated successfully',
                    'member': ProjectMemberSerializer(member).data
                })
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except ProjectMember.DoesNotExist:
            return Response(
                {'error': 'User is not a team member'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['delete'])
    def remove_member(self, request, pk=None):
        """Remove a team member from the project"""
        project = self.get_object()
        
        # Check if user can manage team members
        if project.created_by != request.user and not request.user.is_superuser:
            return Response(
                {'error': 'Only project creators can remove team members'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Try to get user_id from query params first, then from request data
        user_id = request.query_params.get('user_id') or request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required as query parameter or in request body'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_to_remove = User.objects.get(id=user_id)
            success, message = project.remove_team_member(user_to_remove, actor=request.user)
            
            if success:
                return Response({'message': message})
            else:
                return Response(
                    {'error': message}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def my_memberships(self, request):
        """Get all projects where the current user is a member"""
        user = request.user
        memberships = ProjectMember.objects.filter(user=user).select_related('project')
        
        projects_data = []
        for membership in memberships:
            project = membership.project
            projects_data.append({
                'project': ProjectSerializer(project, context={'request': request}).data,
                'membership': ProjectMemberSerializer(membership).data
            })
        
        return Response({
            'memberships': projects_data,
            'total_count': len(projects_data)
        })

    @action(detail=False, methods=['get'])
    def available_users(self, request):
        """Get list of users that can be invited to projects"""
        # Only allow project creators and admins to see available users
        if not request.user.can_create_projects():
            return Response(
                {'error': 'You do not have permission to view available users'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get all users except the current user
        users = User.objects.exclude(id=request.user.id).values(
            'id', 'username', 'email', 'role', 'institution'
        )
        
        return Response({
            'users': list(users),
            'total_count': users.count()
        })

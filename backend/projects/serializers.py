from rest_framework import serializers
from .models import Project, ProjectMember
from authentication.serializers import UserSerializer

class ProjectMemberSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    invited_by_details = UserSerializer(source='invited_by', read_only=True)
    permissions_list = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectMember
        fields = [
            'id', 'user', 'user_details', 'role', 'permissions', 'permissions_list',
            'joined_at', 'invited_by', 'invited_by_details'
        ]
        read_only_fields = ['id', 'joined_at', 'invited_by']
    
    def get_permissions_list(self, obj):
        """Get permissions as a list"""
        return obj.get_permissions_list()
    
    def validate_user(self, value):
        """Validate that user can be added to project"""
        project = self.context.get('project')
        if project and project.created_by == value:
            raise serializers.ValidationError("Project creator is automatically a team member.")
        
        if project and project.members.filter(user=value).exists():
            raise serializers.ValidationError("User is already a team member of this project.")
        
        return value
    
    def validate_permissions(self, value):
        """Validate permissions format"""
        if not value:
            return 'view_project,view_responses'
        
        # If it's a list, convert to string
        if isinstance(value, list):
            return ','.join(value)
        
        # Validate that permissions are valid
        valid_permissions = [choice[0] for choice in ProjectMember.PERMISSION_CHOICES]
        permissions_list = value.split(',') if isinstance(value, str) else value
        
        for perm in permissions_list:
            if perm.strip() not in valid_permissions:
                raise serializers.ValidationError(f"Invalid permission: {perm}")
        
        return value


class ProjectSerializer(serializers.ModelSerializer):
    created_by_details = UserSerializer(source='created_by', read_only=True)
    question_count = serializers.SerializerMethodField()
    response_count = serializers.SerializerMethodField()
    team_members_count = serializers.SerializerMethodField()
    team_members = serializers.SerializerMethodField()
    user_permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'created_by', 'created_by_details',
            'created_at', 'updated_at', 'sync_status', 'cloud_id',
            'settings', 'metadata', 'question_count', 'response_count', 
            'team_members_count', 'team_members', 'user_permissions'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'question_count', 'response_count', 
                           'team_members_count', 'team_members', 'user_permissions', 'created_by']
        
    def validate_name(self, value):
        """Validate project name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Project name is required.")
        
        # Check for duplicate names within the same user's projects
        user = self.context['request'].user
        project_id = self.instance.id if self.instance else None
        
        # Exclude current project from duplicate check (for updates)
        existing_projects = Project.objects.filter(created_by=user, name__iexact=value.strip())
        if project_id:
            existing_projects = existing_projects.exclude(id=project_id)
        
        if existing_projects.exists():
            raise serializers.ValidationError("A project with this name already exists.")
        
        return value.strip()
    
    def validate_description(self, value):
        """Validate project description"""
        if value and len(value) > 1000:
            raise serializers.ValidationError("Description cannot exceed 1000 characters.")
        return value
        
    def get_question_count(self, obj):
        """Get the number of questions in this project"""
        return obj.questions.count()
    
    def get_response_count(self, obj):
        """Get the number of responses in this project"""
        return obj.responses.count()
    
    def get_team_members_count(self, obj):
        """Get the number of team members in this project"""
        return obj.get_team_members_count()
    
    def get_team_members(self, obj):
        """Get team members for this project"""
        request = self.context.get('request')
        if not request:
            return []
        
        # Only return team members if user has permission to view them
        user = request.user
        if not obj.can_user_access(user):
            return []
        
        # The get_team_members() method now returns serializable data directly
        return obj.get_team_members()
    
    def get_user_permissions(self, obj):
        """Get current user's permissions for this project"""
        request = self.context.get('request')
        if not request:
            return []
        
        return obj.get_user_permissions(request.user)


class ProjectMemberInviteSerializer(serializers.Serializer):
    """Serializer for inviting users to projects"""
    user_email = serializers.EmailField()
    role = serializers.ChoiceField(choices=ProjectMember.ROLE_CHOICES, default='member')
    permissions = serializers.ListField(
        child=serializers.ChoiceField(choices=[choice[0] for choice in ProjectMember.PERMISSION_CHOICES]),
        required=False
    )
    
    def validate_user_email(self, value):
        """Validate that user exists"""
        from authentication.models import User
        try:
            user = User.objects.get(email=value)
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address.")
    
    def validate(self, attrs):
        """Validate the invite data"""
        project = self.context.get('project')
        user = attrs['user_email']  # This is now a User object from validate_user_email
        
        if project.created_by == user:
            raise serializers.ValidationError("Cannot invite project creator as a team member.")
        
        if project.members.filter(user=user).exists():
            raise serializers.ValidationError("User is already a team member of this project.")
        
        # Set default permissions based on role if not provided
        if 'permissions' not in attrs or not attrs['permissions']:
            attrs['permissions'] = ProjectMember.get_default_permissions_for_role(attrs['role'])
        
        return attrs


class ProjectMemberUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating project member role and permissions"""
    permissions_list = serializers.ListField(
        child=serializers.ChoiceField(choices=[choice[0] for choice in ProjectMember.PERMISSION_CHOICES]),
        source='permissions',
        required=False
    )
    
    class Meta:
        model = ProjectMember
        fields = ['role', 'permissions_list']
    
    def validate_role(self, value):
        """Validate role change"""
        # Add any business logic for role changes here
        return value
    
    def update(self, instance, validated_data):
        """Update project member"""
        if 'permissions' in validated_data:
            # Convert list back to comma-separated string
            permissions = validated_data.pop('permissions')
            validated_data['permissions'] = ','.join(permissions) if isinstance(permissions, list) else permissions
        
        return super().update(instance, validated_data) 
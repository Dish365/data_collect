from rest_framework import serializers
from .models import SyncQueue
from authentication.serializers import UserSerializer

class SyncQueueSerializer(serializers.ModelSerializer):
    created_by_details = UserSerializer(source='created_by', read_only=True)
    
    class Meta:
        model = SyncQueue
        fields = [
            'id', 'table_name', 'record_id', 'operation', 
            'data', 'created_by', 'created_by_details', 'created_at', 
            'attempts', 'last_attempt', 'status', 'error_message', 'priority'
        ]
        read_only_fields = ['id', 'created_at', 'attempts', 'last_attempt']
        
    def validate_priority(self, value):
        """Ensure priority is within reasonable bounds"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Priority must be between 0 and 100.")
        return value 
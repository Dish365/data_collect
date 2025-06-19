from django.contrib import admin
from .models import Response

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'question', 'respondent_id', 'collected_by', 'collected_at', 'sync_status', 'get_response_preview']
    search_fields = ['respondent_id', 'response_value', 'question__question_text', 'project__name', 'collected_by__email']
    list_filter = ['sync_status', 'collected_at', 'collected_by', 'project', 'question__question_type']
    readonly_fields = ['id', 'collected_at']
    ordering = ['-collected_at']
    list_select_related = ['project', 'question', 'collected_by']
    date_hierarchy = 'collected_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'project', 'question', 'respondent_id')
        }),
        ('Response Data', {
            'fields': ('response_value', 'metadata'),
        }),
        ('Collection Information', {
            'fields': ('collected_by', 'collected_at', 'location_data'),
            'classes': ('collapse',),
        }),
        ('Sync Information', {
            'fields': ('sync_status',),
            'classes': ('collapse',),
        }),
    )
    
    def get_response_preview(self, obj):
        """Display a preview of the response value"""
        if obj.response_value:
            preview = str(obj.response_value)[:50]
            if len(str(obj.response_value)) > 50:
                preview += "..."
            return preview
        return "No response"
    get_response_preview.short_description = 'Response Preview'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('project', 'question', 'collected_by')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "project":
            kwargs["queryset"] = db_field.related_model.objects.all().order_by('name')
        elif db_field.name == "question":
            kwargs["queryset"] = db_field.related_model.objects.all().order_by('question_text')
        elif db_field.name == "collected_by":
            kwargs["queryset"] = db_field.related_model.objects.all().order_by('email')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

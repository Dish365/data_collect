from django.contrib import admin
from .models import AnalyticsResult

@admin.register(AnalyticsResult)
class AnalyticsResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'analysis_type', 'generated_at', 'sync_status', 'get_result_summary']
    list_filter = ['analysis_type', 'sync_status', 'generated_at', 'project']
    search_fields = ['project__name', 'analysis_type', 'id']
    readonly_fields = ['id', 'generated_at']
    ordering = ['-generated_at']
    date_hierarchy = 'generated_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'project', 'analysis_type', 'generated_at')
        }),
        ('Analysis Configuration', {
            'fields': ('parameters',),
            'classes': ('collapse',),
        }),
        ('Analysis Results', {
            'fields': ('results',),
            'classes': ('collapse',),
        }),
        ('Sync Information', {
            'fields': ('sync_status',),
            'classes': ('collapse',),
        }),
    )
    
    def get_result_summary(self, obj):
        """Display a summary of the analysis results"""
        if obj.results and isinstance(obj.results, dict):
            # Show first few keys as summary
            keys = list(obj.results.keys())[:3]
            return f"Results: {', '.join(keys)}"
        return "No results"
    get_result_summary.short_description = 'Result Summary'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('project')
    
    def has_add_permission(self, request):
        # Analytics results are typically generated programmatically
        return False 
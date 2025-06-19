from django.contrib import admin
from .models import Question

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'question_text', 'question_type', 'order_index', 'is_required', 'created_at', 'sync_status']
    search_fields = ['question_text', 'project__name', 'id']
    list_filter = ['question_type', 'sync_status', 'is_required', 'created_at', 'project']
    readonly_fields = ['id', 'created_at']
    ordering = ['project', 'order_index']
    list_select_related = ['project']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'project', 'question_text', 'question_type')
        }),
        ('Question Configuration', {
            'fields': ('order_index', 'is_required', 'options', 'validation_rules')
        }),
        ('Metadata', {
            'fields': ('created_at', 'sync_status'),
            'classes': ('collapse',),
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('project')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "project":
            kwargs["queryset"] = db_field.related_model.objects.all().order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

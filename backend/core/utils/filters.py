import django_filters
from django.db.models import Q
from datetime import datetime
from projects.models import Project
from forms.models import Question
from responses.models import Response

class BaseFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    updated_after = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='lte')

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )

class ProjectFilter(BaseFilter):
    class Meta:
        model = Project
        fields = {
            'name': ['exact', 'icontains'],
            'created_by': ['exact'],
            'sync_status': ['exact'],
        }

class QuestionFilter(BaseFilter):
    class Meta:
        model = Question
        fields = {
            'question_text': ['exact', 'icontains'],
            'question_type': ['exact'],
            'project': ['exact'],
            'sync_status': ['exact'],
        }

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(question_text__icontains=value) |
            Q(project__name__icontains=value)
        )

class ResponseFilter(BaseFilter):
    class Meta:
        model = Response
        fields = {
            'project': ['exact'],
            'question': ['exact'],
            'respondent_id': ['exact'],
            'collected_by': ['exact'],
            'sync_status': ['exact'],
        }

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(response_value__icontains=value) |
            Q(respondent_id__icontains=value) |
            Q(question__question_text__icontains=value)
        ) 
from django.shortcuts import render
from rest_framework import viewsets
from core.utils.viewsets import BaseModelViewSet
from core.utils.filters import ProjectFilter
from .models import Project
from .serializers import ProjectSerializer

# Create your views here.

class ProjectViewSet(BaseModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filterset_class = ProjectFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']

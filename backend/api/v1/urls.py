"""
URL configuration for API v1.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
# Register your viewsets here
# router.register(r'example', views.ExampleViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 
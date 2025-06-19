from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnalyticsResultViewSet

router = DefaultRouter()
router.register(r'analytics-results', AnalyticsResultViewSet, basename='analytics-results')

urlpatterns = [
    path('', include(router.urls)),
] 
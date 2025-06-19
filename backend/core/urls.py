"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Import admin configuration
from . import admin as admin_config

# API Version
API_VERSION = getattr(settings, 'API_VERSION', 'v1')

# Swagger schema view
schema_view = get_schema_view(
    openapi.Info(
        title="Research Data Collection API",
        default_version='v1',
        description="API for research data collection tool",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@researchtool.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin URLs
    path("admin/", admin.site.urls),
    
    # API Documentation
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Authentication URLs
    path('api/auth/', include('authentication.urls')),
    
    # API v1 URLs
    path(f'api/{API_VERSION}/', include('api.v1.urls')),
    
    # Individual app URLs
    path('api/analytics/', include('analytics_results.urls')),
    path('api/forms/', include('forms.urls')),
    path('api/projects/', include('projects.urls')),
    path('api/responses/', include('responses.urls')),
    path('api/sync/', include('sync.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

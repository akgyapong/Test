from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Core API endpoints (must come BEFORE auth/ to avoid conflicts)
    path('api/v1/', include('api.urls')),
    
    # Products and Categories API
    path('api/v1/', include('products.urls')),
    
    # Social Authentication APIs (more specific path to avoid conflict)
    path('api/v1/social-auth/', include('authentication.urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Social Authentication (allauth)
    path('accounts/', include('allauth.urls')),
] 



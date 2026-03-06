"""
URL configuration for connectly_project project.

This file maps URLs to views for the project, including:
- Django admin interface
- REST framework authentication
- Social authentication via Google (allauth)
- API endpoints for posts, comments, and authentication

For more information on Django URL routing, see:
https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.urls import path
from connectly_project.authentication.views import GoogleLoginView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # -------------------- ADMIN -------------------- #
    # Default Django admin interface
    path("admin/", admin.site.urls),

    # -------------------- REST FRAMEWORK AUTH -------------------- #
    # Provides browsable API login/logout buttons
    path("api-auth/", include("rest_framework.urls")), 
    
    # -------------------- SOCIAL AUTH -------------------- #
    # Handles Google OAuth redirects and login flow via allauth
    path('accounts/', include('allauth.urls')), 
    
    # Optional direct endpoint for Google login (custom API view)
    path('api/auth/google/login/', GoogleLoginView.as_view(), name='google-login'),

    # JWT token refresh endpoint
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # -------------------- API ENDPOINTS -------------------- #
    # Includes all the posts, comments, likes, and feed endpoints
    path("api/", include("connectly_project.posts.urls")),  
]
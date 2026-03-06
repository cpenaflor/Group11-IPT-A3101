# This file defines URL patterns for the authentication app.
# It maps HTTP endpoints to corresponding view classes that handle
# authentication-related actions, such as logging in with Google OAuth.

from connectly_project.authentication.views import GoogleLoginView
from django.urls import path

# List of URL patterns for the authentication app
urlpatterns = [
    # Endpoint for Google OAuth login
    # Maps POST requests to the GoogleLoginView class
    path('auth/google/login/', GoogleLoginView.as_view(), name='google-login'),
]



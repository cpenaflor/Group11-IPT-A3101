# This file defines view classes for authentication-related endpoints.
# Currently, it provides a Google OAuth login endpoint, which allows
# users to authenticate using their Google account and receive JWT tokens.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from rest_framework.permissions import AllowAny
from decouple import config

# Dynamically retrieve the custom user model defined in settings.AUTH_USER_MODEL
User = get_user_model()

class GoogleLoginView(APIView):
    # View class to handle Google OAuth login.
    # Accepts a POST request with an 'id_token' from Google,
    # verifies it, and returns JWT access and refresh tokens for the user.
    # Allow any user (authenticated or not) to access this endpoint
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle POST requests for Google login.
        Expects an 'id_token' in the request data.
        """
        # Retrieve the token from the request payload
        token = request.data.get("id_token")
        if not token:
            # Return error if no token is provided
            return Response({"error": "id_token required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve Google OAuth client ID from environment variables
            CLIENT_ID = config("GOOGLE_OAUTH_CLIENT_ID")

            # Verify the provided ID token with Google's OAuth2 service
            idinfo = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                CLIENT_ID
            )

            # Extract user's email from the verified token
            email = idinfo.get("email")
            # Generate a username based on the email prefix
            username = email.split("@")[0]

            # Retrieve existing user or create a new one if not found
            # Email is used as the unique identifier
            user, created = User.objects.get_or_create(
                email=email,
                defaults={"username": username}
            )

            # Generate JWT refresh and access tokens for the user
            refresh = RefreshToken.for_user(user)

            # Return the tokens in the response
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            })

        except ValueError:
            # Token verification failed; return an unauthorized error
            return Response({"error": "Invalid Google token"}, status=status.HTTP_401_UNAUTHORIZED)
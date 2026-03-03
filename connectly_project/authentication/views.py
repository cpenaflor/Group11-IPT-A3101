from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from rest_framework.permissions import AllowAny
from decouple import config

class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("id_token")
        if not token:
            return Response({"error": "id_token required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            CLIENT_ID = config("GOOGLE_OAUTH_CLIENT_ID")

            idinfo = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                CLIENT_ID
            )

            email = idinfo.get("email")
            username = email.split("@")[0]

            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": email}
            )

            refresh = RefreshToken.for_user(user)

            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            })

        except ValueError:
            return Response({"error": "Invalid Google token"}, status=status.HTTP_401_UNAUTHORIZED)
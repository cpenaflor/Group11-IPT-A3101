from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import User, Post, Comment
from .serializers import UserSerializer, PostSerializer, CommentSerializer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from .permissions import IsPostAuthor
from rest_framework.authentication import TokenAuthentication


# We use @csrf_exempt so Postman can make POST requests without a token
@method_decorator(csrf_exempt, name='dispatch')
class UserListCreate(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Manually extract the data from the request
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        if not username or not password:
            return Response({"error": "Username and password required"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Leverage Django's Built-in Password Hashing
        # Use the variables (username, password) instead of "new_user"
        user = User.objects.create_user(username=username, password=password, email=email)
        print(user.password)  # This outputs the hashed version to terminal
        
        # 2. Verify Passwords During Login
        user = authenticate(username=username, password=password)
        if user is not None:
            print("Authentication successful!")
        else:
            print("Invalid credentials.")
        
        # Return the serialized user data
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@method_decorator(csrf_exempt, name='dispatch')
class PostListCreate(APIView):
    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class CommentListCreate(APIView):
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PostDetailView(APIView):
    # This view requires being logged in AND being the author of the post
    permission_classes = [IsAuthenticated, IsPostAuthor]

    def get(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            
            # This line manually triggers the logic in permissions.py
            self.check_object_permissions(request, post)
            
            return Response({"content": post.content})
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND) 

class ProtectedView(APIView):
    # This requires a valid token to access
    authentication_classes = [TokenAuthentication]
    
    # This ensures the user is logged in
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Authenticated!"})
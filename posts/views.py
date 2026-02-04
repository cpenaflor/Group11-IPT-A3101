from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Post, Comment 
from .serializers import UserSerializer, PostSerializer, CommentSerializer
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from .permissions import IsPostAuthor
from rest_framework.authentication import TokenAuthentication

# --- SINGLETON IMPORTS ---
from singletons.config_manager import ConfigManager
from singletons.logger_singleton import LoggerSingleton

# --- FACTORY IMPORTS ---
from factories.post_factory import PostFactory

# Initialize Singletons
logger = LoggerSingleton().get_logger()
config = ConfigManager()

@method_decorator(csrf_exempt, name='dispatch')
class UserListCreate(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        if not username or not password:
            logger.warning("User creation attempt failed: Missing credentials.")
            return Response({"error": "Username and password required"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, email=email)
        logger.info(f"User created successfully: {username}")
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@method_decorator(csrf_exempt, name='dispatch')
class PostListCreate(APIView):
    # Add these two lines so 'request.user' works correctly
    authentication_classes = [TokenAuthentication] 
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit = config.get_setting("DEFAULT_PAGE_SIZE")
        posts = Post.objects.all()[:limit]
        logger.info(f"Accessed Post List. Applied limit: {limit}")
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        # EVERYTHING BELOW MUST BE INDENTED 
        data = request.data
        try:
            # Get the user from the Token provided in the Postman header
            author = request.user 

            # Call the factory and pass the author object
            post = PostFactory.create_post(
                post_type=data['post_type'],
                title=data['title'],
                content=data.get('content', ''),
                metadata=data.get('metadata', {}),
                author=author  
            )
            
            logger.info(f"Post created by {author.username}: ID {post.id}")
            return Response({'message': 'Post created successfully!', 'post_id': post.id}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Post creation failed: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
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
            logger.info("New comment added.")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class PostDetailView(APIView):
    permission_classes = [IsAuthenticated, IsPostAuthor]

    def get(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            self.check_object_permissions(request, post)
            logger.info(f"Post {pk} retrieved by author {request.user.username}")
            return Response({"content": post.content})
        except Post.DoesNotExist:
            logger.warning(f"Failed access: Post {pk} does not exist.")
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

class ProtectedView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info(f"Authenticated access to ProtectedView by {request.user.username}")
        return Response({"message": "Authenticated!"})
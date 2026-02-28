from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User as AuthUser, Group 
from django.contrib.auth import authenticate, login
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import NotFound
from .models import Post, Comment, Like
from .serializers import UserSerializer, PostSerializer, CommentSerializer
from .permissions import IsPostAuthor
from singletons.logger_singleton import LoggerSingleton
from factories.post_factory import PostFactory
from rest_framework.pagination import PageNumberPagination

logger = LoggerSingleton().get_logger()

class UserListCreate(APIView):
    def get(self, request):
        users = AuthUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        if username and password:
            user = AuthUser.objects.create_user(username=username, email=email, password=password)
            user_group, created = Group.objects.get_or_create(name="StandardUser")
            user.groups.add(user_group)
            return Response({
                "username": user.username,
                "group": user_group.name,
                "message": "User created and assigned to group!"
            }, status=status.HTTP_201_CREATED)
        return Response({"error": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST)

class UserLogin(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({"message": "Login successful!"}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)

class PostListCreate(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

class CreatePostView(APIView):
    authentication_classes = [TokenAuthentication] 
    permission_classes = [IsAuthenticated]
    def post(self, request):
        data = request.data
        try:
            post = PostFactory.create_post(
                post_type=data.get('post_type', 'text'),
                title=data.get('title'),
                author=request.user, 
                content=data.get('content', ''),
                metadata=data.get('metadata', {})
            )
            logger.info(f"Post ID {post.id} successfully created via Factory by user: {request.user.username}")
            return Response({'message': 'Post created successfully!', 'post_id': post.id}, status=status.HTTP_201_CREATED)
        except ValueError as e:
            logger.error(f"Factory validation failed: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CommentCreateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
            comments = post.comments.all()
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
            text = request.data.get('text')
            if not text:
                return Response({"error": "Comment text is required"}, status=status.HTTP_400_BAD_REQUEST)
            Comment.objects.create(post=post, author=request.user, text=text)
            logger.info(f"User {request.user.username} commented on Post ID {post_id}")
            return Response({"message": "Comment added successfully!"}, status=status.HTTP_201_CREATED)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

class LikeToggleView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
            like, created = Like.objects.get_or_create(user=request.user, post=post)
            if not created:
                like.delete()
                logger.info(f"User {request.user.username} un-liked Post ID {post_id}")
                return Response({"message": "Post un-liked"}, status=status.HTTP_200_OK)
            logger.info(f"User {request.user.username} liked Post ID {post_id}")
            return Response({"message": "Post liked successfully!"}, status=status.HTTP_201_CREATED)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

class PostDetailView(APIView):
    permission_classes = [IsAuthenticated, IsPostAuthor]
    def get(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            self.check_object_permissions(request, post)
            return Response({"content": post.content})
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
    def delete(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            self.check_object_permissions(request, post)
            post.delete()
            return Response({"message": "Post deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

class CommentListCreate(APIView):
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

class NewsFeedPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50

class NewsFeedView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = Post.objects.all().order_by('-created_at')
        
        post_type = request.query_params.get('post_type')
        if post_type:
            posts = posts.filter(post_type=post_type)
        
        paginator = NewsFeedPagination()
        try:
            paginated_posts = paginator.paginate_queryset(posts, request)
        except NotFound:
            return Response({
                "error": "Invalid page",
                "message": "The requested page does not exist."
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = PostSerializer(paginated_posts, many=True)
        logger.info(f"User {request.user.username} accessed the news feed.")
        return paginator.get_paginated_response(serializer.data)
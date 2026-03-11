# This file defines API views for the posts application.
# Views handle CRUD operations for users, posts, comments, and likes.
# It also implements Google login integration, news feed retrieval, 
# and enforces object-level permissions to ensure secure access.
# Logging is used extensively for traceability and debugging.

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from factories.post_factory import PostFactory

from .singletons.logger_singleton import LoggerSingleton
from .models import Post, Comment, Like
from .serializers import (
    UserSerializer,
    PostSerializer,
    CommentSerializer,
    LikeSerializer,
)
from .permissions import IsPostAuthor, IsCommentAuthor
from rest_framework.pagination import PageNumberPagination


# Dynamically get the active user model
User = get_user_model()

# Initialize a singleton logger for consistent logging across views
logger = LoggerSingleton().get_logger()

# -------------------- USERS -------------------- #
class UserListCreate(APIView):
    """
    API view to list all users or create a new user.
    GET: Returns a list of all users.
    POST: Creates a new user with validated input.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Retrieve all users from the database and return serialized data.
        """
        logger.info("GET /users/")
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Create a new user from the provided request data.
        Logs success or failure and returns appropriate HTTP status.
        """
        logger.info("POST /users/ (create user)")
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            logger.info(
                f"User created: username={user.username}, id={user.id}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.warning(f"User create failed: errors={serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------- POSTS -------------------- #
class PostListCreate(APIView):
    """
    API view to list all posts or create a new post.
    GET: Returns all posts in descending order of creation time.
    POST: Creates a new post using PostFactory and validates input.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info(f"GET /posts/ by user={request.user.username}")
        posts = Post.objects.all().order_by("-created_at")
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Create a new post using the PostFactory.
        Validates post_type, content, and optional metadata.
        """
        logger.info(f"POST /posts/ by user={request.user.username}")
        content = request.data.get('content', '')
        post_type = request.data.get('post_type', 'text')
        metadata = request.data.get('metadata', {})

        # --- Strict Privacy Validation ---
        privacy_level = request.data.get('privacy_level')

        if privacy_level is None:
            logger.warning(f"Post creation failed: Missing privacy_level")
            return Response(
                {"error": "privacy_level is required. Use 1 for Private, 2 for Public."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Pass the privacy_level into your Factory
            post = PostFactory.create_post(
                post_type=post_type,
                author=request.user,
                content=content,
                metadata=metadata,
                privacy_level=privacy_level 
            )
            
            logger.info(f"Post created via Factory: post_id={post.id}")
            return Response(PostSerializer(post).data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            # 4. Handle validation errors (like blank content)
            logger.warning(f"Post creation failed: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PostDetail(APIView):
    """
    API view to retrieve, update, or delete a specific post.
    Enforces that only the author can update or delete the post.
    """
    permission_classes = [IsAuthenticated, IsPostAuthor]

    def get(self, request, pk):
        logger.info(f"GET /posts/{pk}/ by user={request.user.username}")
        post = get_object_or_404(Post, pk=pk)
        self.check_object_permissions(request, post)
        return Response(PostSerializer(post).data)

    def put(self, request, pk):
        """
        Update a post if the requesting user is the author.
        Validates the updated data and logs success or failure.
        """
        logger.info(f"PUT /posts/{pk}/ by user={request.user.username}")
        post = get_object_or_404(Post, pk=pk)
        self.check_object_permissions(request, post)
        serializer = PostSerializer(post, data=request.data)

        if serializer.is_valid():
            updated_post = serializer.save(author=request.user)
            logger.info(
                f"Post updated: post_id={updated_post.id}, user={request.user.username}")
            return Response(PostSerializer(updated_post).data)

        logger.warning(
            f"Post update failed: post_id={pk}, user={request.user.username}, errors={serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete a post if the requesting user is the author.
        Logs deletion event and returns HTTP 204 on success.
        """
        logger.info(f"DELETE /posts/{pk}/ by user={request.user.username}")
        post = get_object_or_404(Post, pk=pk)
        self.check_object_permissions(request, post)
        post.delete()
        logger.info(
            f"Post deleted: post_id={pk}, by user={request.user.username}")
        return Response(status=status.HTTP_204_NO_CONTENT)

# -------------------- LIKES -------------------- #
class PostLike(APIView):
    """
    API view to like a post.
    Prevents duplicate likes by the same user for the same post.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        logger.info(f"POST /posts/{pk}/like/ by user={request.user.username}")
        like, created = Like.objects.get_or_create(
            user=request.user, post=post)
        
        if not created:
            logger.warning(
                f"Duplicate like blocked: user={request.user.username}, post_id={pk}")
            return Response(
                {"detail": "You already liked this post."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(LikeSerializer(like).data, status=status.HTTP_201_CREATED)


# -------------------- COMMENTS -------------------- #
class PostComment(APIView):
    """
    API view to add a comment to a specific post.
    Validates that the comment text is not empty.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        logger.info(
            f"POST /posts/{pk}/comment/ by user={request.user.username}")

        text = (request.data.get("text") or "").strip()
        if not text:
            return Response(
                {"detail": "Comment text is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        comment = Comment.objects.create(
            text=text,
            author=request.user,
            post=post
        )

        logger.info(
            f"Comment created: comment_id={comment.id}, post_id={pk}, user={request.user.username}")
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)


class PostComments(APIView):
    """
    API view to retrieve all comments for a specific post.
    Returns comments in descending order of creation.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        logger.info(
            f"GET /posts/{pk}/comments/ by user={request.user.username}")

        comments = Comment.objects.filter(post=post).order_by("-created_at")
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class CommentListCreate(APIView):
    """
    API view to list all comments or create a new comment globally.
    Validates that post exists and comment text is not empty.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info(f"GET /comments/ by user={request.user.username}")
        comments = Comment.objects.all().order_by("-created_at")
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        logger.info(f"POST /comments/ by user={request.user.username}")

        post_id = request.data.get("post")
        text = (request.data.get("text") or "").strip()

        if not post_id:
            return Response({"detail": "post is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not text:
            return Response({"detail": "text is required."}, status=status.HTTP_400_BAD_REQUEST)

        post = get_object_or_404(Post, pk=post_id)

        comment = Comment.objects.create(
            text=text,
            author=request.user,
            post=post
        )

        logger.info(
            f"Comment created: comment_id={comment.id}, post_id={post.id}, author={request.user.username}")
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)


class CommentDetail(APIView):
    """
    API view to delete a specific comment.
    Ensures that only the comment's author can perform deletion.
    """
    permission_classes = [IsAuthenticated, IsCommentAuthor]

    def delete(self, request, pk):
        logger.info(f"DELETE /comments/{pk}/ by user={request.user.username}")
        comment = get_object_or_404(Comment, pk=pk)
        self.check_object_permissions(request, comment)

        comment.delete()
        logger.info(
            f"Comment deleted: comment_id={pk}, by user={request.user.username}")
        return Response(status=status.HTTP_204_NO_CONTENT)


# -------------------- NEWS FEED -------------------- #
class NewsFeedPagination(PageNumberPagination):
    """
    Custom pagination class for the news feed.
    """
    page_size = 5  # Number of posts per page
    page_size_query_param = 'page_size'
    max_page_size = 50

class NewsFeedView(APIView):
    """
    API view for paginated news feed.
    Supports filtering by posts liked by the requesting user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info(f"User {request.user.username} accessing news feed.")
        
        # Retrieve posts in descending order
        # Only show Public posts OR the user's own Private posts
        posts = Post.objects.filter(
            Q(privacy_level=2) | Q(author=request.user)
        ).order_by('-created_at')

        # Filter by liked posts if requested
        liked_only = request.query_params.get('liked_only')
        if liked_only == 'true':
            posts = posts.filter(likes__user=request.user)
            logger.info(f"Filtering feed for posts liked by {request.user.username}")

        # Apply pagination
        paginator = NewsFeedPagination()
        try:
            paginated_posts = paginator.paginate_queryset(posts, request)
        except Exception:
            return Response(
                {"error": "Invalid page", "message": "The requested page does not exist."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Serialize and return paginated posts
        serializer = PostSerializer(paginated_posts, many=True)
        return paginator.get_paginated_response(serializer.data)
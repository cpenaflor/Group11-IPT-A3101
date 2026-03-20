# This file contains all API views for users, posts, comments, likes, and news feed.
# It also implements role-based access control and privacy-level rules.
from .pagination import NewsFeedPagination
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination

from factories.post_factory import PostFactory

from .singletons.logger_singleton import LoggerSingleton
from .models import Post, Comment, Like
from .serializers import (
    UserSerializer,
    PostSerializer,
    CommentSerializer,
    LikeSerializer,
)

# Get the active custom user model
User = get_user_model()

# Shared logger instance
logger = LoggerSingleton().get_logger()

#  Helper functions


def is_admin(user):
    # Returns True if the authenticated user has admin role
    return user.is_authenticated and getattr(user, "role", None) == 1


def is_public(post):
    # Returns True if the post is public
    return getattr(post, "privacy_level", None) == 2


def can_view_post(user, post):
    """
    Determines whether a user can view a given post.

    Rules:
    - Anyone can view a public post
    - Unauthenticated users cannot view non-public posts
    - Admins can view any post
    - Authors can view their own posts
    - All other access is denied
    """
    # Public posts are visible to everyone, including guests
    if is_public(post):
        return True
    # Guests cannot view private posts
    if not user.is_authenticated:
        return False

    # Admin can view any post
    if is_admin(user):
        return True

    # Owner can view their own post
    if post.author == user:
        return True

    # Otherwise, access is denied
    return False


def can_interact_with_post(user, post):
    # Access rules for liking/commenting:
    # - admin can interact with any post
    # - owner can interact with own post
    # - anyone authenticated can interact with public post
    if not user.is_authenticated:
        return False
    if is_admin(user):
        return True
    if post.author == user:
        return True
    if is_public(post):
        return True
    return False


#  User views

class UserListCreate(APIView):
    # Allow anyone to create a user or list users
    permission_classes = [AllowAny]

    def get(self, request):
        # Return all users
        logger.info("GET /users/")
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Create a new user
        logger.info("POST /users/ (create user)")
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            logger.info(
                f"User created: username={user.username}, id={user.id}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.warning(f"User create failed: errors={serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#  Post views

class PostListCreate(APIView):
    # Only authenticated users can list/create posts
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Return posts based on user role:
        # - admin sees all posts
        # - normal user sees public posts + own posts
        logger.info(
            f"GET /posts/ by user={request.user.username}, role={getattr(request.user, 'role', None)}"
        )

        if is_admin(request.user):
            posts = Post.objects.all().order_by("-created_at")
        else:
            posts = Post.objects.filter(
                Q(privacy_level=2) | Q(author=request.user)
            ).order_by("-created_at")

        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Create a new post using the factory
        logger.info(f"POST /posts/ by user={request.user.username}")

        content = request.data.get("content", "")
        post_type = request.data.get("post_type", "text")
        metadata = request.data.get("metadata", {})
        privacy_level = request.data.get("privacy_level")

        # Require privacy_level in request body
        if privacy_level is None:
            logger.warning("Post creation failed: Missing privacy_level")
            return Response(
                {"error": "privacy_level is required. Use 1 for Private, 2 for Public."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Make sure privacy_level is integer
        try:
            privacy_level = int(privacy_level)
        except (TypeError, ValueError):
            return Response(
                {"error": "privacy_level must be an integer. Use 1 for Private, 2 for Public."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            post = PostFactory.create_post(
                post_type=post_type,
                author=request.user,
                content=content,
                metadata=metadata,
                privacy_level=privacy_level,
            )
            logger.info(f"Post created via Factory: post_id={post.id}")
            return Response(PostSerializer(post).data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            logger.warning(f"Post creation failed: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PostDetail(APIView):
    # Only authenticated users can access post detail routes
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        # Retrieve a single post if user is allowed to view it
        logger.info(
            f"GET /posts/{pk}/ by user={request.user.username}, role={getattr(request.user, 'role', None)}"
        )
        post = get_object_or_404(Post, pk=pk)

        if not can_view_post(request.user, post):
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(PostSerializer(post).data)

    def put(self, request, pk):
        # Only the author can edit the post
        logger.info(
            f"PUT /posts/{pk}/ by user={request.user.username}, role={getattr(request.user, 'role', None)}"
        )
        post = get_object_or_404(Post, pk=pk)

        if post.author != request.user:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            updated_post = serializer.save(author=request.user)
            logger.info(
                f"Post updated: post_id={updated_post.id}, user={request.user.username}"
            )
            return Response(PostSerializer(updated_post).data)

        logger.warning(
            f"Post update failed: post_id={pk}, user={request.user.username}, errors={serializer.errors}"
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        # Only admin can delete any post
        logger.info(
            f"DELETE /posts/{pk}/ by user={request.user.username}, role={getattr(request.user, 'role', None)}"
        )
        post = get_object_or_404(Post, pk=pk)

        if is_admin(request.user):
            post.delete()
            logger.info(
                f"Post deleted by admin: post_id={pk}, user={request.user.username}"
            )
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {"detail": "You do not have permission to perform this action."},
            status=status.HTTP_403_FORBIDDEN,
        )


#  Like views

class PostLike(APIView):
    # Only authenticated users can like posts
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        # Like a post if user is allowed to interact with it
        post = get_object_or_404(Post, pk=pk)
        logger.info(f"POST /posts/{pk}/like/ by user={request.user.username}")

        if not can_interact_with_post(request.user, post):
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        like, created = Like.objects.get_or_create(
            user=request.user, post=post)

        if not created:
            logger.warning(
                f"Duplicate like blocked: user={request.user.username}, post_id={pk}"
            )
            return Response(
                {"detail": "You already liked this post."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(LikeSerializer(like).data, status=status.HTTP_201_CREATED)


#  Comment views

class PostComment(APIView):
    # Only authenticated users can comment
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        # Add a comment to a post if user is allowed
        post = get_object_or_404(Post, pk=pk)
        logger.info(
            f"POST /posts/{pk}/comment/ by user={request.user.username}")

        if not can_interact_with_post(request.user, post):
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        text = (request.data.get("text") or "").strip()
        if not text:
            return Response(
                {"detail": "Comment text is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        comment = Comment.objects.create(
            text=text,
            author=request.user,
            post=post,
        )

        logger.info(
            f"Comment created: comment_id={comment.id}, post_id={pk}, user={request.user.username}"
        )
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)


class PostComments(APIView):
    # Only authenticated users can view comments of an accessible post
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        # Return comments for a post if user can view the post
        post = get_object_or_404(Post, pk=pk)
        logger.info(
            f"GET /posts/{pk}/comments/ by user={request.user.username}")

        if not can_view_post(request.user, post):
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        comments = Comment.objects.filter(post=post).order_by("-created_at")
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class CommentListCreate(APIView):
    # Only authenticated users can list or create comments
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Admin sees all comments, normal user sees only own comments
        logger.info(f"GET /comments/ by user={request.user.username}")

        if is_admin(request.user):
            comments = Comment.objects.all().order_by("-created_at")
        else:
            comments = Comment.objects.filter(
                author=request.user).order_by("-created_at")

        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Create a comment globally by passing post id
        logger.info(f"POST /comments/ by user={request.user.username}")

        post_id = request.data.get("post")
        text = (request.data.get("text") or "").strip()

        if not post_id:
            return Response(
                {"detail": "post is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not text:
            return Response(
                {"detail": "text is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        post = get_object_or_404(Post, pk=post_id)

        if not can_interact_with_post(request.user, post):
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        comment = Comment.objects.create(
            text=text,
            author=request.user,
            post=post,
        )

        logger.info(
            f"Comment created: comment_id={comment.id}, post_id={post.id}, author={request.user.username}"
        )
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)


class CommentDetail(APIView):
    # Only authenticated users can access comment detail routes
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        # Admin or comment owner can view comment detail
        logger.info(f"GET /comments/{pk}/ by user={request.user.username}")
        comment = get_object_or_404(Comment, pk=pk)

        if is_admin(request.user) or comment.author == request.user:
            return Response(CommentSerializer(comment).data)

        return Response(
            {"detail": "You do not have permission to perform this action."},
            status=status.HTTP_403_FORBIDDEN,
        )

    def put(self, request, pk):
        # Only comment owner can edit
        logger.info(f"PUT /comments/{pk}/ by user={request.user.username}")
        comment = get_object_or_404(Comment, pk=pk)

        if comment.author != request.user:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = CommentSerializer(
            comment, data=request.data, partial=True)
        if serializer.is_valid():
            updated_comment = serializer.save(
                author=request.user, post=comment.post)
            logger.info(
                f"Comment updated: comment_id={updated_comment.id}, user={request.user.username}"
            )
            return Response(CommentSerializer(updated_comment).data)

        logger.warning(
            f"Comment update failed: comment_id={pk}, user={request.user.username}, errors={serializer.errors}"
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        # Only admin can delete any comment
        logger.info(f"DELETE /comments/{pk}/ by user={request.user.username}")
        comment = get_object_or_404(Comment, pk=pk)

        if is_admin(request.user):
            comment.delete()
            logger.info(
                f"Comment deleted by admin: comment_id={pk}, user={request.user.username}"
            )
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {"detail": "You do not have permission to perform this action."},
            status=status.HTTP_403_FORBIDDEN,
        )


# News feed

class NewsFeedView(APIView):
    """
    Returns the news feed.

    Access rules:
    - Guests can view only public posts
    - Authenticated users can view public posts and their own posts
    - Admins can view all posts

    Supports:
    - pagination
    - filtering liked posts for authenticated users
    """
    # Allow both guests and logged-in users to access the feed endpoint
    permission_classes = [AllowAny]

    @method_decorator(cache_page(60))
    def get(self, request):
        # Check whether the requester is logged in
        if request.user.is_authenticated:
            logger.info(f"User {request.user.username} accessing news feed.")

            # Admin can view all posts
            if is_admin(request.user):
                posts = Post.objects.all().select_related("author").order_by("-created_at")

            # Regular authenticated users can view:
            # - public posts
            # - their own posts
            else:
                posts = Post.objects.filter(
                    Q(privacy_level=2) | Q(author=request.user)
                ).select_related("author").order_by("-created_at")

            # Optional filter: show only posts liked by the current user
            liked_only = request.query_params.get("liked_only")
            if liked_only == "true":
                posts = posts.filter(likes__user=request.user)
                logger.info(
                    f"Filtering feed for posts liked by {request.user.username}"
                )

        # Guest users can only view public posts
        else:
            logger.info("Guest accessing public news feed.")
            posts = Post.objects.filter(
                privacy_level=2
            ).select_related("author").order_by("-created_at")

        # Apply pagination to improve performance and response size
        paginator = NewsFeedPagination()
        try:
            paginated_posts = paginator.paginate_queryset(posts, request)
        except Exception:
            return Response(
                {
                    "error": "Invalid page",
                    "message": "The requested page does not exist.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Serialize paginated results and return paginated response
        serializer = PostSerializer(paginated_posts, many=True)
        return paginator.get_paginated_response(serializer.data)

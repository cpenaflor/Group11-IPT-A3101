# This file defines URL patterns for the posts application.
# Each URL maps an HTTP endpoint to a corresponding view that handles
# CRUD operations, likes, comments, and news feed functionality.
# It also includes endpoints for user authentication and Google OAuth login.

from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from connectly_project.authentication.views import GoogleLoginView

from .views import (
    UserListCreate,
    PostListCreate, PostDetail,
    CommentListCreate, CommentDetail,
    PostLike, PostComment, PostComments, NewsFeedView,
)

# List of URL patterns for the posts app
urlpatterns = [
    # User endpoints
    path("users/", UserListCreate.as_view(), name="users"), # List all users or create a new user
    path("token/", obtain_auth_token, name="token"), # Obtain token for user authentication (DRF token auth)

    # Post endpoints
    path("posts/", PostListCreate.as_view(), name="posts"),   # List all posts or create a new post
    path("posts/<int:pk>/", PostDetail.as_view(), name="post-detail"),   # Retrieve, update, or delete a specific post

    # Comment endpoints
    path("comments/", CommentListCreate.as_view(), name="comments"),  # List all comments or create a new comment
    path("comments/<int:pk>/", CommentDetail.as_view(), name="comment-detail"),  # Delete a specific comment

    # Homework 5: Likes and comments on specific posts
    path("posts/<int:pk>/like/", PostLike.as_view(), name="post-like"),  # Like a specific post
    path("posts/<int:pk>/comment/", PostComment.as_view(), name="post-comment"),  # Comment on a specific post
    path("posts/<int:pk>/comments/", PostComments.as_view(), name="post-comments"), # List all comments for a specific post

    # Homework 6: Google OAuth login endpoints
    path('api/auth/google/login/', GoogleLoginView.as_view(), name='google-login'),  # Login via Google OAuth
    path('auth/google/login/', GoogleLoginView.as_view(), name='google-login'),  # Alternative path for Google OAuth login

    # Homework 7: News feed endpoint
    path('feed/', NewsFeedView.as_view(), name='news-feed'), # Retrieve paginated news feed with sorting and filtering
]
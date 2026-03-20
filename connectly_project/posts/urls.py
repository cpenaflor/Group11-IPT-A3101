# This file maps API endpoints to the views that handle them.
# It includes routes for:
# - users
# - authentication token login
# - posts
# - comments
# - likes
# - post-specific comments
# - Google OAuth login
# - news feed

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
    # List all users or create a new user
    path("users/", UserListCreate.as_view(), name="users"),
    # Obtain token for user authentication (DRF token auth)
    path("token/", obtain_auth_token, name="token"),

    # Post endpoints
    # List all posts or create a new post
    path("posts/", PostListCreate.as_view(), name="posts"),
    # Retrieve, update, or delete a specific post
    path("posts/<int:pk>/", PostDetail.as_view(), name="post-detail"),

    # Comment endpoints
    # List all comments or create a new comment
    path("comments/", CommentListCreate.as_view(), name="comments"),
    path("comments/<int:pk>/", CommentDetail.as_view(),
         name="comment-detail"),  # Delete a specific comment

    # Homework 5: Likes and comments on specific posts
    path("posts/<int:pk>/like/", PostLike.as_view(),
         name="post-like"),  # Like a specific post
    path("posts/<int:pk>/comment/", PostComment.as_view(),
         name="post-comment"),  # Comment on a specific post
    path("posts/<int:pk>/comments/", PostComments.as_view(),
         name="post-comments"),  # List all comments for a specific post

    # Homework 6: Google OAuth login endpoints
    # REST API endpoint for exchanging a Google OAuth token for a JWT/session token
    path('api/auth/google/login/', GoogleLoginView.as_view(), name='google-login'),
    # Social login landing page for browser-based authentication and user redirection.
    path('accounts/google/login/', GoogleLoginView.as_view(), name='google-login'),

    # Homework 7: News feed endpoint
    # Retrieve paginated news feed with sorting and filtering
    path('feed/', NewsFeedView.as_view(), name='news-feed'),
]

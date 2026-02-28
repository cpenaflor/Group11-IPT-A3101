from django.urls import path
from .views import (
    UserListCreate, PostListCreate, CommentListCreate, 
    UserLogin, PostDetailView, CreatePostView,
    CommentCreateView, LikeToggleView, NewsFeedView
)

urlpatterns = [
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    path('login/', UserLogin.as_view(), name='user-login'),
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'), 
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),
    path('create/', CreatePostView.as_view(), name='create-post'),
    path('<int:post_id>/comments/', CommentCreateView.as_view(), name='post-comments'),
    path('<int:post_id>/like/', LikeToggleView.as_view(), name='like-post'),
    path('feed/', NewsFeedView.as_view(), name='news-feed'),
]
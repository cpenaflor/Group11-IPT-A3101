from django.urls import path
from .views import UserListCreate, PostListCreate, CommentListCreate, UserLogin, PostDetailView
from .views import CreatePostView

urlpatterns = [
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    path('login/', UserLogin.as_view(), name='user-login'),
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'), 
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),
    path('create/', CreatePostView.as_view(), name='create-post'),
]
from django.urls import path
from .views import UserListCreate, PostListCreate, CommentListCreate, PostDetailView, ProtectedView

urlpatterns = [
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    # Use this path for testing your Factory Pattern
    path('factory-create/', PostListCreate.as_view(), name='post-factory-create'),
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('protected/', ProtectedView.as_view(), name='protected-view'),
]
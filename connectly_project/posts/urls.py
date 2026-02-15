from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    UserListCreate,
    PostListCreate, PostDetail,
    CommentListCreate, CommentDetail,
    PostLike, PostComment, PostComments,
)

urlpatterns = [
    path("users/", UserListCreate.as_view(), name="users"),
    path("token/", obtain_auth_token, name="token"),

    path("posts/", PostListCreate.as_view(), name="posts"),
    path("posts/<int:pk>/", PostDetail.as_view(), name="post-detail"),

    path("comments/", CommentListCreate.as_view(), name="comments"),
    path("comments/<int:pk>/", CommentDetail.as_view(), name="comment-detail"),

    # Homework 5
    path("posts/<int:pk>/like/", PostLike.as_view(), name="post-like"),
    path("posts/<int:pk>/comment/", PostComment.as_view(), name="post-comment"),
    path("posts/<int:pk>/comments/", PostComments.as_view(), name="post-comments"),
]

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny

from .singletons.logger_singleton import LoggerSingleton
from .models import Post, Comment, Like
from .serializers import (
    UserSerializer,
    PostSerializer,
    CommentSerializer,
    LikeSerializer,
)
from .permissions import IsPostAuthor, IsCommentAuthor

# Singleton logger instance
logger = LoggerSingleton().get_logger()

# USERS


class UserListCreate(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        logger.info("GET /users/")
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        logger.info("POST /users/ (create user)")
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            logger.info(
                f"User created: username={user.username}, id={user.id}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.warning(f"User create failed: errors={serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# POSTS


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication

class PostListCreate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info(f"GET /posts/ by user={request.user.username}")
        posts = Post.objects.all().order_by("-created_at")
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        logger.info(f"POST /posts/ by user={request.user.username}")
        serializer = PostSerializer(data=request.data)

        if serializer.is_valid():
            # author set server-side
            post = serializer.save(author=request.user)
            logger.info(
                f"Post created: post_id={post.id}, author={request.user.username}"
            )
            return Response(PostSerializer(post).data, status=status.HTTP_201_CREATED)

        logger.warning(
            f"Post create failed: user={request.user.username}, errors={serializer.errors}"
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetail(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsPostAuthor]

    def get(self, request, pk):
        logger.info(f"GET /posts/{pk}/ by user={request.user.username}")
        post = get_object_or_404(Post, pk=pk)
        self.check_object_permissions(request, post)
        return Response(PostSerializer(post).data)

    def put(self, request, pk):
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
        logger.info(f"DELETE /posts/{pk}/ by user={request.user.username}")
        post = get_object_or_404(Post, pk=pk)
        self.check_object_permissions(request, post)

        post.delete()
        logger.info(
            f"Post deleted: post_id={pk}, by user={request.user.username}")
        return Response(status=status.HTTP_204_NO_CONTENT)

# HOMEWORK 5: LIKES + POST COMMENTS
# Like a post (prevents duplicate likes)


class PostLike(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        logger.info(f"POST /posts/{pk}/like/ by user={request.user.username}")

        # safest duplicate-prevention pattern
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

# Comment on a specific post (validates non-empty text)


class PostComment(APIView):
    authentication_classes = [TokenAuthentication]
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

# Get all comments for a specific post


class PostComments(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        logger.info(
            f"GET /posts/{pk}/comments/ by user={request.user.username}")

        comments = Comment.objects.filter(post=post).order_by("-created_at")
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

# COMMENTS (GLOBAL)


class CommentListCreate(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info(f"GET /comments/ by user={request.user.username}")
        comments = Comment.objects.all().order_by("-created_at")
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Optional endpoint: create a comment by passing post id.
        Safer version: validates post exists and text is not empty.
        """
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
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsCommentAuthor]

    def delete(self, request, pk):
        logger.info(f"DELETE /comments/{pk}/ by user={request.user.username}")
        comment = get_object_or_404(Comment, pk=pk)
        self.check_object_permissions(request, comment)

        comment.delete()
        logger.info(
            f"Comment deleted: comment_id={pk}, by user={request.user.username}")
        return Response(status=status.HTTP_204_NO_CONTENT)

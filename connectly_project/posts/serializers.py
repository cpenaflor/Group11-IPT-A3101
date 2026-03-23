# This file contains serializers for users, posts, comments, and likes.
# Serializers validate request data and convert model instances to JSON.

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Comment, Like

# Get the active custom user model
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    # Password is write-only so it will not be exposed in responses
    password = serializers.CharField(write_only=True, required=True)
    # Make role required
    role = serializers.IntegerField(required=True)

    class Meta:
        # Serializer for the custom user model
        model = User
        fields = ["id", "username", "email", "password", "role"]

    def validate_role(self, value):
        # Allow only 1=Admin or 2=User
        if value not in [1, 2]:
            raise serializers.ValidationError(
                "Invalid role. Use 1=Admin, 2=User."
            )
        return value

    def create(self, validated_data):
        # Create a new user with hashed password
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
            role=validated_data["role"],
        )


class CommentSerializer(serializers.ModelSerializer):
    # Show username of comment author as read-only
    author = serializers.ReadOnlyField(source="author.username")

    class Meta:
        # Serializer for comment model
        model = Comment
        fields = ["id", "text", "author", "post", "created_at"]


class PostSerializer(serializers.ModelSerializer):
    # Privacy level is explicitly validated and serialized
    privacy_level = serializers.IntegerField()

    # Show author's username only
    author = serializers.ReadOnlyField(source="author.username")

    # Computed fields for counts
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    # Nested comments for each post
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        # Serializer for post model
        model = Post
        fields = [
            "id",
            "content",
            "author",
            "created_at",
            "like_count",
            "comment_count",
            "comments",
            "privacy_level",
        ]

    def validate_privacy_level(self, value):
        # Allow only 1=Private or 2=Public
        if value not in [1, 2]:
            raise serializers.ValidationError(
                "Invalid privacy level. Use 1=Private, 2=Public."
            )
        return value

    def get_like_count(self, obj):
        # Return total likes of the post
        return obj.likes.count()

    def get_comment_count(self, obj):
        # Return total comments of the post
        return obj.comments.count()


class LikeSerializer(serializers.ModelSerializer):
    # Show username of the user who liked the post
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        # Serializer for like model
        model = Like
        fields = ["id", "user", "post", "created_at"]

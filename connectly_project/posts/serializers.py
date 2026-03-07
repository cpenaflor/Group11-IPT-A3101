# This file defines serializers for the posts application.
# Serializers convert complex model instances into native Python datatypes
# that can then be rendered into JSON for API responses, and vice versa.
# They also handle validation and object creation for API requests.

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Comment, Like

# Dynamically retrieve the custom user model
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomUser model.
    Handles serialization and deserialization of user data,
    including secure password handling during creation.
    """
    # Ensure password is write-only and required for user creation
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        """
        Create a new user with a hashed password.
        Uses the create_user method to ensure the password is stored securely.
        """
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )

class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Comment model.
    Includes the author's username as a read-only field.
    """
    author = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model = Comment
        fields = ["id", "text", "author", "post", "created_at"]

class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for the Post model.
    Includes counts of likes and comments, as well as nested comment data.
    """
    # Include the author's username as a read-only field
    author = serializers.ReadOnlyField(source="author.username")

    # Include dynamic counts for likes and comments
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    
    # Include full serialized data for comments associated with the post
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        # Fields included in API responses
        fields = ["id", "content", "author", "created_at", 
                  "like_count", "comment_count", "comments"]

    def get_like_count(self, obj):
        """
        Return the total number of likes for this post.
        """
        return obj.likes.count()

    def get_comment_count(self, obj):
        """
        Return the total number of comments for this post.
        """
        return obj.comments.count()


class LikeSerializer(serializers.ModelSerializer):
    """
    Serializer for the Like model.
    Includes the username of the user who liked the post.
    """
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Like
        fields = ["id", "user", "post", "created_at"]

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
        fields = ["id", "username", "email", "password", "role"]

    def validate_role(self, value):
        """
        Ensure the role is one of the allowed integers (1, 2, 3)
        """
        if value not in [1, 2, 3]:
            raise serializers.ValidationError(
                "Invalid role. Use 1=Admin, 2=User."
            )
        return value

    def create(self, validated_data):
        """
        Create a new user with a hashed password.
        Uses the create_user method to ensure the password is stored securely.
        """
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
            role=validated_data.get("role", User.Roles.USER)
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
    # Explicitly include the privacy_level field for validation and serialization
    privacy_level = serializers.IntegerField()
    
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
                  "like_count", "comment_count", "comments", "privacy_level"]

    def validate_privacy_level(self, value):
        """
        Ensure the privacy level is either 1 (Private) or 2 (Public).
        """
        if value not in [1, 2]:
            raise serializers.ValidationError(
                "Invalid privacy level. Use 1=Private, 2=Public."
            )
        return value


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

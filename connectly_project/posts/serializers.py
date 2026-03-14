from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Comment, Like

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "role"]

    def validate_role(self, value):
        if value not in [1, 2]:
            raise serializers.ValidationError(
                "Invalid role. Use 1=Admin, 2=User."
            )
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
            role=validated_data.get("role", User.Roles.USER),
        )


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model = Comment
        fields = ["id", "text", "author", "post", "created_at"]


class PostSerializer(serializers.ModelSerializer):
    privacy_level = serializers.IntegerField()
    author = serializers.ReadOnlyField(source="author.username")
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
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
        if value not in [1, 2]:
            raise serializers.ValidationError(
                "Invalid privacy level. Use 1=Private, 2=Public."
            )
        return value

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_comment_count(self, obj):
        return obj.comments.count()


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Like
        fields = ["id", "user", "post", "created_at"]

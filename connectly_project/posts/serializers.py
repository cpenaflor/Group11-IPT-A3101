from rest_framework import serializers
from .models import User, Post, Comment
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Only include safe fields; DO NOT include 'password'
        fields = ['username', 'email']

class PostSerializer(serializers.ModelSerializer):
    # This allows us to see the text of related comments when viewing a post
    comments = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'content', 'author', 'created_at', 'comments']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'post', 'created_at']

    # Custom validation to ensure the post and author actually exist
    def validate_post(self, value):
        if not Post.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Post not found.")
        return value

    def validate_author(self, value):
        if not User.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Author not found.")
        return value
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Only list fields that are safe to show the public
        fields = ['username', 'email']  # Exclude 'password' here
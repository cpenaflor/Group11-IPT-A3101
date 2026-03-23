# This file defines the database models for the posts application.
# It includes models for posts, comments, and likes, and defines
# the relationships between users and their content.
# All models use Django's ORM to interact with the database.

from django.db import models
# Import settings to reference AUTH_USER_MODEL dynamically
from django.conf import settings


class Post(models.Model):
    """
    Model representing a user post.
    Posts can be of type text, image, or video, and include optional metadata.
    Each post is linked to an author (user) and a creation timestamp.
    """
    # Choices for post type
    POST_TYPES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
    )

    # Integer-based privacy choices
    class PrivacyLevel(models.IntegerChoices):
        PRIVATE = 1, "Private"
        PUBLIC = 2, "Public"

    # Main content of the post; can be empty for non-text posts
    content = models.TextField(blank=True)

    # Type of the post: text, image, or video
    post_type = models.CharField(
        max_length=10, choices=POST_TYPES, default='text')

    # Optional JSON metadata for storing additional information
    metadata = models.JSONField(null=True, blank=True)

    # New field: Privacy Level for the post, using IntegerChoices for better
    # readability and maintainability
    privacy_level = models.PositiveSmallIntegerField(
        choices=PrivacyLevel.choices,
        help_text="1=Private, 2=Public"
    )

    # Reference to the user who created the post
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="posts", on_delete=models.CASCADE)
    # Timestamp automatically set when the post is created
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a readable string representation of the post."""
        return f"Post by {self.author.username}"


class Comment(models.Model):
    """
    Model representing a comment on a post.
    Each comment is linked to a user (author) and a specific post.
    """
    # Text content of the comment
    text = models.TextField()

    # User who wrote the comment
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="comments", on_delete=models.CASCADE)

    # Post that the comment belongs to
    post = models.ForeignKey(
        Post, related_name="comments", on_delete=models.CASCADE)

    # Timestamp automatically set when the comment is created
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a readable string representation of the comment."""
        return f"Comment by {self.author.username} on Post {self.post.id}"


class Like(models.Model):
    """
    Model representing a 'like' on a post.
    Each like links a user to a post, and a user can only like a post once.
    """
    # User who liked the post
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="likes",
                             on_delete=models.CASCADE)

    # Post that was liked
    post = models.ForeignKey(Post, related_name="likes",
                             on_delete=models.CASCADE)

    # Timestamp automatically set when the like is created
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevent a user from liking the same post multiple times
        unique_together = ("user", "post")  # prevents duplicate likes

    def __str__(self):
        """Return a readable string representation of the like."""
        return f"{self.user.username} liked Post {self.post.id}"

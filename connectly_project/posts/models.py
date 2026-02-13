from django.db import models
from django.contrib.auth.models import User # Use built-in User for security features

class Post(models.Model):
    # --- FACTORY PATTERN CONFIGURATION ---
    POST_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    post_type = models.CharField(max_length=10, choices=POST_TYPES, default='text')
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True) # Stores factory-validated data
    # -------------------------------------

    author = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.post_type}) by {self.author.username}"

class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on Post {self.post.id}"
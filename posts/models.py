from django.db import models
from django.contrib.auth.models import User as AuthUser

class Post(models.Model):
    POST_TYPES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
    )
    
    title = models.CharField(max_length=255) 
    content = models.TextField(blank=True)
    post_type = models.CharField(max_length=10, choices=POST_TYPES, default='text') 
    metadata = models.JSONField(null=True, blank=True) 
    author = models.ForeignKey(AuthUser, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.author.username}"

class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(AuthUser, related_name='comments', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on Post {self.post.id}"
    
class Like(models.Model):
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(AuthUser, related_name='liked_posts', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user') 

    def __str__(self):
        return f"{self.user.username} liked {self.post.title}"
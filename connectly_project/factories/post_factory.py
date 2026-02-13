from posts.models import Post

class PostFactory:
    @staticmethod
    def create_post(post_type, title, content='', metadata=None, author=None):
        # 1. Ensure metadata is at least an empty dict to avoid 'NoneType' errors
        if metadata is None:
            metadata = {}

        # 2. Validate the post type against allowed types in the Model
        if post_type not in dict(Post.POST_TYPES):
            raise ValueError(f"Invalid post type: {post_type}")

        # 3. Validate type-specific requirements in metadata
        if post_type == 'image' and 'file_size' not in metadata:
            raise ValueError("Image posts require 'file_size' in metadata")
            
        if post_type == 'video' and 'duration' not in metadata:
            raise ValueError("Video posts require 'duration' in metadata")

        # 4. Centralized creation of the Post object (including the author)
        return Post.objects.create(
            title=title,
            content=content,
            post_type=post_type,
            metadata=metadata,
            author=author  # This is the key fix for your security setup
        )
    
    
from connectly_project.posts.models import Post

class PostFactory:
    """
    Factory class for creating Post instances with validation.
    This centralizes post creation logic and enforces rules for post types and metadata.
    """


    @staticmethod
    def create_post(post_type, author, content='', metadata=None):
        """
        Create a new Post instance with validation.

        Args:
            post_type (str): The type of the post ('text', 'image', or 'video').
            author (CustomUser): The user creating the post.
            content (str): The main textual content of the post.
            metadata (dict, optional): Additional post-specific data (e.g., file size for images, duration for videos).

        Raises:
            ValueError: If content is blank, post_type is invalid, or required metadata is missing.

        Returns:
            Post: The newly created Post object.
        """

        # Ensure the content is not blank or only whitespace
        if not content or not content.strip(): 
            raise ValueError("Post content cannot be blank.")
        
        # Ensure the post type is valid
        if post_type not in dict(Post.POST_TYPES):
            raise ValueError("Invalid post type")

        # Validate metadata based on post type requirements
        if post_type == 'image' and 'file_size' not in metadata:
            raise ValueError("Image posts require 'file_size' in metadata")
        if post_type == 'video' and 'duration' not in metadata:
            raise ValueError("Video posts require 'duration' in metadata")

        # Create and return the Post instance
        return Post.objects.create(
            content=content,
            post_type=post_type,
            metadata=metadata,
            author=author
        )


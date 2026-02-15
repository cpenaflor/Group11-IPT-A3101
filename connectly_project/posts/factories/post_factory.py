from posts.models import Post
from posts.singletons.config_manager import ConfigManager

class PostFactory:
    """
    Factory that creates Post objects with consistent validation rules.
    """
    @staticmethod
    def create_post(*, author, content: str):
        config = ConfigManager()
        min_len = config.get_setting("POST_MIN_LENGTH", 1)
        max_len = config.get_setting("POST_MAX_LENGTH", 500)

        if content is None:
            raise ValueError("content is required")

        content = content.strip()
        if len(content) < min_len:
            raise ValueError(f"content must be at least {min_len} character(s)")
        if len(content) > max_len:
            raise ValueError(f"content must be at most {max_len} character(s)")

        return Post.objects.create(author=author, content=content)

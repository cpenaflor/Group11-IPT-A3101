# This file defines the configuration for the 'posts' app.
# AppConfig classes are used by Django to configure application-specific
# settings and metadata during project startup.

from django.apps import AppConfig


class PostsConfig(AppConfig):
    """
    Configuration class for the 'posts' application.
    Specifies the full Python path to the app module.
    """
    # Full Python path to the posts app
    name = 'connectly_project.posts'
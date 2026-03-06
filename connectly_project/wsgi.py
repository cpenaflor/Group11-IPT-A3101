"""
WSGI config for connectly_project project.

This module exposes the WSGI callable as a module-level variable named `application`.
WSGI (Web Server Gateway Interface) is the standard interface between web servers and Python web applications/frameworks.

It is used by deployment servers to serve the Django application.

For more information, see:
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Set the default settings module for the Django project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connectly_project.settings')

# Get the WSGI application callable that the WSGI server can use to communicate with the Django application
application = get_wsgi_application()

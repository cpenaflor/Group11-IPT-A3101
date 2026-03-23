# This file defines custom permissions for the posts application.
# These permissions ensure that only the authors of posts or comments
# can perform certain actions, such as updating or deleting their own content.

from rest_framework.permissions import BasePermission


class IsPostAuthor(BasePermission):
    """
    Custom permission for post objects.

    Allows access if:
    - the requesting user is the author of the post, or
    - the requesting user is an admin (role == 1)
    """

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or getattr(request.user, "role", None) == 1


class IsCommentAuthor(BasePermission):
    """
    Custom permission for comment objects.

    Allows access if:
    - the requesting user is the author of the comment, or
    - the requesting user is an admin (role == 1)
    """

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or getattr(request.user, "role", None) == 1

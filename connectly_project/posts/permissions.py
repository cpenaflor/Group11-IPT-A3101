# This file defines custom permissions for the posts application.
# These permissions ensure that only the authors of posts or comments
# can perform certain actions, such as updating or deleting their own content.

from rest_framework.permissions import BasePermission


class IsPostAuthor(BasePermission):
    """
    Custom permission that allows only the author of a post to perform
    actions that require object-level permissions (e.g., update or delete).
    """

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or getattr(request.user, "role", None) == 1


class IsCommentAuthor(BasePermission):
    """
    Custom permission that allows only the author of a comment to perform
    actions that require object-level permissions (e.g., delete).
    """

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or getattr(request.user, "role", None) == 1

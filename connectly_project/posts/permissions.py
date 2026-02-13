from rest_framework.permissions import BasePermission

class IsPostAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        # This checks if the person logged in is the author of the specific post
        return obj.author == request.user
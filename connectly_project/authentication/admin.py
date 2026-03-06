# This file customizes the Django admin interface for the CustomUser model.
# It allows administrators to view, search, and manage user accounts,
# including email, username, and staff status.

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.contrib import admin

# Dynamically get the custom user model defined in settings.AUTH_USER_MODEL
User = get_user_model()

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin class for the CustomUser model.
    Extends Django's built-in UserAdmin to display email and username
    in the admin list view, and to enable searching by these fields.
    """
    # Columns displayed in the list view for users in the admin interface
    list_display = ('email', 'username', 'is_staff')

    # Fields that can be searched using the admin search bar
    search_fields = ('email', 'username')
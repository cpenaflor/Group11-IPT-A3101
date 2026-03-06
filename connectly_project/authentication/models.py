# This file defines the CustomUser model used for authentication.
# The CustomUser model extends Django's AbstractUser to use email as the
# unique identifier for login instead of the default username. Additional
# fields can be added in the future to extend user functionality.

from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """
    Custom user model that extends Django's AbstractUser.
    Overrides the default authentication behavior to use email
    as the USERNAME_FIELD for login and ensures email uniqueness.
    """
    # Unique email ensures no two accounts share the same email address
    email = models.EmailField(unique=True) # This makes sure no two accounts use the same email

    # Use email for authentication instead of the default username field
    USERNAME_FIELD = "email"

    # Specify required fields for creating superusers
    REQUIRED_FIELDS = ["username"]
    
    # Placeholder for future fields that may extend the user model
    # For example: bio, profile_picture, date_of_birth, etc.


    

    
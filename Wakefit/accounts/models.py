# type: ignore
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # We use AbstractUser to keep Django's built-in auth but allow for future fields
    is_customer = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username
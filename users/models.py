from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Please provide email")
        if not extra_fields.get("username"):
            raise ValueError("Please provide username")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        is_staff = extra_fields.setdefault("is_staff", True)
        is_superuser = extra_fields.setdefault("is_superuser", True)
        if not is_staff:
            raise ValueError("To create super user is_staff must be True")
        if not is_superuser:
            raise ValueError("To create super user is_superuser must be True")

        return self.create_user(email, password, **extra_fields)



class User(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    following = models.ManyToManyField(
        "self", symmetrical=False, related_name="followers",
        blank=True
    )
    image = models.ImageField(upload_to="users/profile_images/", blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    
    def __str__(self):
        return self.username

from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    username = None
    nickName = models.CharField(max_length=150, unique=True)

    USERNAME_FIELD = 'nickName'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.nickName

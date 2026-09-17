import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    username = None
    apelido = models.CharField(max_length=150, unique=True)
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    xp_total = models.IntegerField(default=0)
    streak_dias = models.IntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'apelido'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.apelido

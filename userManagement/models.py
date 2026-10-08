import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    username = None
    apelido = models.CharField(max_length=150, unique=True)
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    xp_total = models.IntegerField(default=0)
    streak_dias = models.IntegerField(default=0)
    is_primeiro_acesso = models.BooleanField(default=True)
    sexo = models.CharField(max_length=20, choices=SEXO_CHOICES, null=True, blank=True)
    idade = models.PositiveIntegerField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'apelido'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.apelido


class Interesse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'INTERESSE'

    def __str__(self):
        return self.nome


class UsuarioInteresse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interesses_usuario'
    )
    interesse = models.ForeignKey(
        Interesse, on_delete=models.CASCADE, related_name='usuarios_interessados'
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'USUARIO_INTERESSE'
        unique_together = ('usuario', 'interesse')

    def __str__(self):
        return f"{self.usuario} -> {self.interesse}"

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
    aceite_privacidade_versao = models.CharField(max_length=50, null=True, blank=True)
    aceite_privacidade_em = models.DateTimeField(null=True, blank=True)
    anonimizado_em = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'apelido'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.apelido


class Interesse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=50, unique=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        db_table = 'INTERESSE'
        ordering = ['nome']

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


class Consentimento(models.Model):
    TIPO_CHOICES = [
        ('DADOS_OPCIONAIS', 'Dados opcionais'),
        ('FOTO', 'Foto de perfil'),
        ('MARKETING', 'Marketing'),
        ('IA_EXTERNA', 'Uso de IA externa'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='consentimentos'
    )
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
    concedido_em = models.DateTimeField(auto_now_add=True)
    revogado_em = models.DateTimeField(null=True, blank=True)
    versao_documento = models.CharField(max_length=50, blank=True, default='')

    class Meta:
        db_table = 'CONSENTIMENTO'
        constraints = [
            models.UniqueConstraint(
                fields=['usuario', 'tipo'], name='unique_consentimento_usuario_tipo'
            )
        ]

    @property
    def ativo(self):
        return self.revogado_em is None

    def __str__(self):
        return f"{self.usuario} - {self.tipo} ({'ativo' if self.ativo else 'revogado'})"


class SolicitacaoRevisao(models.Model):
    TIPO_CHOICES = [
        ('NIVELAMENTO', 'Nivelamento'),
        ('PARECER', 'Parecer formativo'),
        ('RECOMENDACAO', 'Recomendação de trilha'),
    ]
    STATUS_CHOICES = [
        ('ABERTA', 'Aberta'),
        ('REVISADA', 'Revisada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='solicitacoes_revisao'
    )
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
    referencia_id = models.UUIDField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ABERTA')
    criado_em = models.DateTimeField(auto_now_add=True)
    respondido_em = models.DateTimeField(null=True, blank=True)
    resposta = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'SOLICITACAO_REVISAO'
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.usuario} - {self.tipo} ({self.status})"

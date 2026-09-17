import uuid
from django.db import models
from django.conf import settings


class Trilha(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titulo = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    habilidade = models.CharField(max_length=50)
    ativo = models.BooleanField(default=True)

    class Meta:
        db_table = 'TRILHA'

    def __str__(self):
        return self.titulo


class Modulo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trilha = models.ForeignKey(Trilha, related_name='modulos', on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    nivel = models.CharField(max_length=30)
    ordem_modulo = models.IntegerField(default=0)

    class Meta:
        db_table = 'MODULO'
        ordering = ['ordem_modulo']

    def __str__(self):
        return f"{self.trilha.titulo} - {self.titulo}"


class Matricula(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='matriculas', on_delete=models.CASCADE)
    trilha = models.ForeignKey(Trilha, related_name='matriculas', on_delete=models.CASCADE)
    status = models.CharField(max_length=30, default='EM_ANDAMENTO')
    criado_em = models.DateTimeField(auto_now_add=True)
    concluido_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'MATRICULA'
        constraints = [
            models.UniqueConstraint(fields=['usuario', 'trilha'], name='unique_usuario_trilha')
        ]

    def __str__(self):
        return f"Matricula {self.usuario} @ {self.trilha}"


class ProgressoModulo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    matricula = models.ForeignKey(Matricula, related_name='progresso_modulos', on_delete=models.CASCADE)
    modulo = models.ForeignKey(Modulo, related_name='progresso', on_delete=models.CASCADE)
    status = models.CharField(max_length=30, default='BLOQUEADO')
    concluido_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'PROGRESSO_MODULO'
        constraints = [
            models.UniqueConstraint(fields=['matricula', 'modulo'], name='unique_matricula_modulo')
        ]

    def __str__(self):
        return f"Progresso {self.modulo} ({self.status})"

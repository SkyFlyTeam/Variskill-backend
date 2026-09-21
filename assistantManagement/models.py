import uuid

from django.conf import settings
from django.db import models


class Sessao(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sessoes_assistente', db_column='usuario_id', on_delete=models.CASCADE)
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'SESSAO'
        indexes = [models.Index(fields=['usuario'], name='sessao_usuario_idx')]


class Mensagem(models.Model):
    class Remetente(models.TextChoices):
        USUARIO = 'USUARIO', 'Usuario'
        ASSISTENTE = 'ASSISTENTE', 'Assistente'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sessao = models.ForeignKey(Sessao, related_name='mensagens', db_column='sessao_id', on_delete=models.CASCADE)
    intencao = models.ForeignKey('intents.Intention', related_name='mensagens', db_column='intencao_id', on_delete=models.SET_NULL, null=True, blank=True)
    remetente = models.CharField(max_length=10, choices=Remetente.choices)
    conteudo = models.TextField()
    distancia = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'MENSAGEM'
        indexes = [models.Index(fields=['sessao'], name='mensagem_sessao_idx')]

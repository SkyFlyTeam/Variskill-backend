import uuid

from django.conf import settings
from django.db import models


class Conteudo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titulo = models.CharField(max_length=255)
    texto_explicativo = models.TextField(blank=True, default='')
    tempo_estimado_minutos = models.PositiveIntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'CONTEUDO'
        ordering = ['criado_em']

    def __str__(self):
        return self.titulo


class Atividade(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    modulo = models.ForeignKey('trackManagement.Modulo', related_name='atividades', on_delete=models.CASCADE)
    conteudo = models.OneToOneField(Conteudo, related_name='atividade', on_delete=models.SET_NULL, null=True, blank=True)
    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, default='')
    contexto_avaliacao = models.CharField(max_length=64)
    xp_recompensa = models.PositiveIntegerField(default=0)
    ordem = models.PositiveIntegerField()
    ativo = models.BooleanField(default=True)

    class Meta:
        db_table = 'ATIVIDADE'
        ordering = ['ordem']

    def __str__(self):
        return self.titulo


class ExecucaoAtividade(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='execucoes_atividade', on_delete=models.CASCADE,
    )
    atividade = models.ForeignKey(Atividade, related_name='execucoes', on_delete=models.CASCADE)
    resposta = models.JSONField()
    pontuacao_obtida = models.IntegerField()
    aprovado = models.BooleanField()
    executado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'EXECUCAO_ATIVIDADE'

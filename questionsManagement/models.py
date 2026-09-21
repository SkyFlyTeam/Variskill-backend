import uuid

from django.db import models


class Questao(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    atividade = models.ForeignKey('activityManagement.Atividade', related_name='questoes', on_delete=models.CASCADE)
    tipo_exercicio = models.CharField(max_length=30)
    enunciado = models.TextField()
    codigo_snippet = models.TextField(blank=True, default='')
    gabarito_esperado = models.CharField(max_length=255)
    explicacao = models.TextField(blank=True, default='')
    dica_conceitual = models.TextField(blank=True, default='')
    ordem_questao = models.IntegerField()
    peso_pontuacao = models.IntegerField(default=10)

    class Meta:
        db_table = 'QUESTAO'
        ordering = ['ordem_questao']


class QuestaoOpcao(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    questao = models.ForeignKey(Questao, related_name='opcoes', on_delete=models.CASCADE)
    texto_opcao = models.TextField()
    ordem = models.IntegerField()

    class Meta:
        db_table = 'QUESTAO_OPCAO'
        ordering = ['ordem']

import uuid

from django.db import models
from pgvector.django import VectorField

from intents.models import EMBEDDING_DIMENSIONS


class EntradaCorpus(models.Model):
    """Resposta conceitual da base de conhecimento do Coach (ex.: "Como definir uma variável em Python?")."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topico = models.CharField(max_length=100)
    pergunta = models.CharField(max_length=255, unique=True)
    resposta = models.TextField()
    ativo = models.BooleanField(default=True)

    class Meta:
        db_table = 'CORPUS_ENTRADA'
        ordering = ['topico', 'pergunta']

    def __str__(self):
        return self.pergunta


class PerguntaCorpus(models.Model):
    """Formulação de pergunta que leva a uma entrada do corpus; a busca semântica compara contra estes embeddings."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entrada = models.ForeignKey(
        EntradaCorpus, related_name='perguntas', on_delete=models.CASCADE, db_column='entrada_id',
    )
    texto = models.TextField()
    embedding = VectorField(dimensions=EMBEDDING_DIMENSIONS)

    class Meta:
        db_table = 'CORPUS_PERGUNTA'
        # Sem índice HNSW de propósito: o seed_corpus apaga e recria todas as linhas, e o HNSW (aproximado)
        # continua visitando as tuplas mortas até o vacuum, podendo não devolver nenhuma linha viva.
        # Com algumas centenas/milhares de formulações, a busca exata (varredura sequencial) leva milissegundos.

    def __str__(self):
        return self.texto[:50]

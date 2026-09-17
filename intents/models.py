import uuid

from django.db import models
from pgvector.django import HnswIndex, VectorField

EMBEDDING_DIMENSIONS = 384


class Intention(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=100, unique=True, db_column='codigo')
    system_action = models.CharField(max_length=255, db_column='acao_sistema')
    description = models.TextField(db_column='descricao')

    class Meta:
        db_table = 'INTENCAO'

    def __str__(self):
        return self.code


class IntentionExample(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    intention = models.ForeignKey(
        Intention, related_name='examples', on_delete=models.CASCADE, db_column='intencao_id',
    )
    text = models.TextField(db_column='texto')
    embedding = VectorField(dimensions=EMBEDDING_DIMENSIONS)

    class Meta:
        db_table = 'EXEMPLO_INTENCAO'
        indexes = [
            HnswIndex(
                name='exemplo_intencao_embedding_hnsw',
                fields=['embedding'],
                m=16,
                ef_construction=64,
                opclasses=['vector_cosine_ops'],
            ),
        ]

    def __str__(self):
        return self.text[:50]


class Response(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    intention = models.ForeignKey(
        Intention, related_name='responses', on_delete=models.CASCADE, db_column='intencao_id',
    )
    text = models.TextField(db_column='texto')

    class Meta:
        db_table = 'RESPOSTA'

    def __str__(self):
        return self.text[:50]

import uuid

from django.db import models
from pgvector.django import HnswIndex, VectorField

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


class DuvidaAssimilada(models.Model):
    """Dúvida de aluno assimilada ao corpus vetorial após resposta da IA externa (VAR-113).

    Diferente de EntradaCorpus (seed estático administrado via seed_corpus), esta tabela é
    alimentada incrementalmente pela ingestão assíncrona pós-IA: nunca é apagada e recriada em
    massa, então o índice HNSW não sofre do problema de tuplas mortas documentado em
    0002_remove_hnsw_corpus.py.

    O embedding usa EMBEDDING_DIMENSIONS (384), igual a PerguntaCorpus/IntentionExample, para
    compatibilidade com o EmbeddingService já existente no projeto (all-MiniLM-L6-v2).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    atividade = models.ForeignKey(
        'activityManagement.Atividade',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='duvidas_assimiladas',
    )
    modulo = models.ForeignKey(
        'trackManagement.Modulo',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='duvidas_assimiladas',
    )
    pergunta_texto = models.TextField()
    pergunta_normalizada = models.TextField()
    resposta_didatica = models.TextField()
    embedding = VectorField(dimensions=EMBEDDING_DIMENSIONS)
    contador_utilizacoes = models.PositiveIntegerField(default=1)
    feedbacks_positivos = models.PositiveIntegerField(default=0)
    feedbacks_negativos = models.PositiveIntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'DUVIDA_ASSIMILADA'
        indexes = [
            HnswIndex(
                name='duvida_assimilada_embed_hnsw',
                fields=['embedding'],
                m=16,
                ef_construction=64,
                opclasses=['vector_cosine_ops'],
            ),
        ]

    def __str__(self):
        return self.pergunta_texto[:50]

"""Busca semântica na base de conhecimento (corpus) do Coach."""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from pgvector.django import CosineDistance

from semanticSearch.models import EntradaCorpus, PerguntaCorpus


@dataclass
class ResultadoCorpus:
    entrada: EntradaCorpus | None
    similaridade: float
    # Entradas próximas, mas abaixo do limiar: úteis como "você quis dizer...?"
    relacionadas: list[EntradaCorpus] = field(default_factory=list)


class CorpusSearch:
    def __init__(self, similarity_threshold: float | None = None, related_threshold: float | None = None):
        self.similarity_threshold = (float(os.getenv("CORPUS_SIMILARITY_THRESHOLD", "0.80"))
                                     if similarity_threshold is None else similarity_threshold)
        self.related_threshold = (float(os.getenv("CORPUS_RELATED_THRESHOLD", "0.60"))
                                  if related_threshold is None else related_threshold)

    def buscar(self, vetor: list[float], limite_relacionadas: int = 3) -> ResultadoCorpus:
        candidatos = (PerguntaCorpus.objects.filter(entrada__ativo=True)
                      .annotate(distancia=CosineDistance("embedding", vetor))
                      .order_by("distancia").select_related("entrada")[:20])

        # Uma entrada pode ter várias formulações; mantém apenas a mais próxima de cada uma.
        melhores: dict = {}
        for candidato in candidatos:
            similaridade = 1.0 - float(candidato.distancia)
            if candidato.entrada_id not in melhores:
                melhores[candidato.entrada_id] = (candidato.entrada, similaridade)

        ranking = list(melhores.values())
        if not ranking:
            return ResultadoCorpus(entrada=None, similaridade=0.0)

        entrada, similaridade = ranking[0]
        if similaridade >= self.similarity_threshold:
            return ResultadoCorpus(entrada=entrada, similaridade=similaridade)

        relacionadas = [e for e, s in ranking if s >= self.related_threshold][:limite_relacionadas]
        return ResultadoCorpus(entrada=None, similaridade=similaridade, relacionadas=relacionadas)

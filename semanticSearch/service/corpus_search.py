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

    def _consultar_candidatos(self, vetor: list[float], topico: str | None = None) -> list[tuple[EntradaCorpus, float]]:
        qs = PerguntaCorpus.objects.filter(entrada__ativo=True)
        if topico:
            qs = qs.filter(entrada__topico__iexact=topico.strip())

        candidatos = (
            qs.annotate(distancia=CosineDistance("embedding", vetor))
            .order_by("distancia")
            .select_related("entrada")[:20]
        )

        # Uma entrada pode ter várias formulações; mantém apenas a mais próxima de cada uma.
        melhores: dict = {}
        for candidato in candidatos:
            similaridade = 1.0 - float(candidato.distancia)
            if candidato.entrada_id not in melhores:
                melhores[candidato.entrada_id] = (candidato.entrada, similaridade)

        return list(melhores.values())

    def buscar(
        self,
        vetor: list[float],
        limite_relacionadas: int = 3,
        topico: str | None = None,
        estrito: bool = False,
    ) -> ResultadoCorpus:
        ranking = self._consultar_candidatos(vetor, topico=topico) if topico else []

        # Se filtrou por tópico sem modo estrito e não atingiu o limiar, consulta o corpus geral como fallback
        if not topico or (not estrito and (not ranking or ranking[0][1] < self.similarity_threshold)):
            ranking_geral = self._consultar_candidatos(vetor, topico=None)
            if not ranking or (ranking_geral and ranking_geral[0][1] > ranking[0][1]):
                ranking = ranking_geral

        if not ranking:
            return ResultadoCorpus(entrada=None, similaridade=0.0)

        entrada, similaridade = ranking[0]
        if similaridade >= self.similarity_threshold:
            return ResultadoCorpus(entrada=entrada, similaridade=similaridade)

        relacionadas = [e for e, s in ranking if s >= self.related_threshold][:limite_relacionadas]
        return ResultadoCorpus(entrada=None, similaridade=similaridade, relacionadas=relacionadas)

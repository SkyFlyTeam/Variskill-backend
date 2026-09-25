from __future__ import annotations

import os
from typing import Any
from pgvector.django import CosineDistance
from intents.models import IntentionExample

FALLBACK_TEXT = "Hmm, não entendi muito bem. Pode reformular sua pergunta?"


class IntentClassifier:
    def __init__(self, similarity_threshold: float | None = None):
        self.similarity_threshold = (float(os.getenv("NLP_SIMILARITY_THRESHOLD", "0.70"))
                                     if similarity_threshold is None else similarity_threshold)

    def classificar(self, vetor: list[float], contexto: dict[str, Any] | None = None) -> dict[str, Any]:
        resultado = (IntentionExample.objects.annotate(distancia=CosineDistance("embedding", vetor))
                     .order_by("distancia").select_related("intention").first())
        if resultado is None:
            return self._fallback(0.0)
        similaridade = 1.0 - float(resultado.distancia)
        if similaridade < self.similarity_threshold:
            return self._fallback(similaridade)
        response = resultado.intention.responses.order_by("?").first()
        texto = response.text if response else FALLBACK_TEXT
        for chave, valor in (contexto or {}).items():
            texto = texto.replace("{" + chave + "}", str(valor))
        return {"intencao": resultado.intention.code, "similaridade": similaridade,
                "resposta_texto": texto, "dados_extras": contexto or {}}

    @staticmethod
    def _fallback(similaridade: float) -> dict[str, Any]:
        return {"intencao": "FALLBACK", "similaridade": similaridade,
                "resposta_texto": FALLBACK_TEXT, "dados_extras": {}}

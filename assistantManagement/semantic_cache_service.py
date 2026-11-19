"""Busca prioritária por dúvidas semanticamente semelhantes já assimiladas (VAR-114).

Consultado antes de acionar a IA externa: se uma dúvida já assimilada for suficientemente
parecida (similaridade de cosseno >= threshold), reaproveita a resposta didática já existente
em vez de gerar uma nova.
"""

from __future__ import annotations

import re
from typing import Optional

from django.db.models import F
from pgvector.django import CosineDistance

from semanticSearch.models import DuvidaAssimilada
from semanticSearch.service.nlp.embedding_service import EmbeddingService

DEFAULT_THRESHOLD = 0.85

# Piso de segurança: nenhum resultado é considerado match abaixo deste valor, mesmo que o
# chamador informe um threshold menor.
SIMILARITY_FLOOR = 0.70


def _normalizar_pergunta(texto: Optional[str]) -> str:
    """Normaliza a pergunta de entrada: minúsculo e sem pontuação excedente."""
    if not texto or not isinstance(texto, str):
        return ""
    texto_normalizado = texto.strip().lower()
    texto_normalizado = re.sub(r"[^\w\s]", " ", texto_normalizado, flags=re.UNICODE)
    return re.sub(r"\s+", " ", texto_normalizado).strip()


class SemanticCacheService:
    @staticmethod
    def buscar_duvida_semelhante(
        pergunta: str,
        atividade_id=None,
        modulo_id=None,
        threshold: float = DEFAULT_THRESHOLD,
    ) -> Optional[dict]:
        """Busca a dúvida assimilada mais parecida com `pergunta` no escopo informado.

        Escopo: se `atividade_id` for informado, busca restrita àquela atividade; senão, se
        `modulo_id` for informado, busca em todo o módulo ativo; senão, busca global.

        Em caso de match (similaridade >= max(threshold, SIMILARITY_FLOOR)), incrementa
        `contador_utilizacoes` atomicamente e retorna a resposta didática, o id da dúvida e a
        similaridade. Caso contrário, retorna None.
        """
        pergunta_normalizada = _normalizar_pergunta(pergunta)
        if not pergunta_normalizada:
            return None

        embedding_pergunta = EmbeddingService.get_instance().gerar_embedding(pergunta_normalizada)

        candidatos = DuvidaAssimilada.objects.all()
        if atividade_id is not None:
            candidatos = candidatos.filter(atividade_id=atividade_id)
        elif modulo_id is not None:
            candidatos = candidatos.filter(modulo_id=modulo_id)

        duvida = (
            candidatos
            .annotate(distancia=CosineDistance('embedding', embedding_pergunta))
            .order_by('distancia')
            .first()
        )
        if duvida is None:
            return None

        similaridade = 1.0 - float(duvida.distancia)
        if similaridade < max(threshold, SIMILARITY_FLOOR):
            return None

        DuvidaAssimilada.objects.filter(pk=duvida.pk).update(
            contador_utilizacoes=F('contador_utilizacoes') + 1
        )

        return {
            'duvida_id': str(duvida.pk),
            'resposta_didatica': duvida.resposta_didatica,
            'similaridade': similaridade,
        }

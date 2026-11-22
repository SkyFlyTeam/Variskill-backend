"""Busca prioritária por dúvidas semanticamente semelhantes já assimiladas (VAR-114).

Consultado antes de acionar a IA externa: se uma dúvida já assimilada for suficientemente
parecida (similaridade de cosseno >= threshold), reaproveita a resposta didática já existente
em vez de gerar uma nova.
"""

from __future__ import annotations

import re
from typing import Optional

from django.conf import settings
from django.db.models import F
from pgvector.django import CosineDistance

from semanticSearch.models import DuvidaAssimilada
from semanticSearch.service.nlp.embedding_service import EmbeddingService
from semanticSearch.service.vetorizacao import vetorizar_duvida

# Piso de segurança: nenhum resultado é considerado match abaixo deste valor, mesmo que o
# chamador informe um threshold menor.
SIMILARITY_FLOOR = 0.70


def _tem_conteudo(texto: Optional[str]) -> bool:
    """Indica se a pergunta tem ao menos uma palavra (não é vazia nem só pontuação)."""
    if not texto or not isinstance(texto, str):
        return False
    return bool(re.sub(r"[^\w]", "", texto, flags=re.UNICODE))


class SemanticCacheService:
    @staticmethod
    def buscar_duvida_semelhante(
        pergunta: Optional[str] = None,
        atividade_id=None,
        modulo_id=None,
        threshold: Optional[float] = None,
        vetor: Optional[list[float]] = None,
        somente_globais: bool = False,
        questao_id=None,
    ) -> Optional[dict]:
        """Busca a dúvida assimilada mais parecida no escopo informado.

        O vetor pode ser informado já calculado (chat/suporte, que já vetorizaram a mensagem);
        senão é gerado a partir de `pergunta` pelo mesmo pipeline da ingestão.

        Escopo (vale o primeiro informado): `questao_id` restringe à questão (dicas);
        `atividade_id` à atividade; `somente_globais` às dúvidas conceituais sem atividade;
        `modulo_id` ao módulo; sem nada, busca em todo o caderno.
        Dúvidas mal avaliadas pelos estudantes são ignoradas.

        Em caso de match (similaridade >= max(threshold, SIMILARITY_FLOOR)), incrementa
        `contador_utilizacoes` atomicamente e retorna a resposta didática, o id da dúvida e a
        similaridade. Caso contrário, retorna None.
        """
        if vetor is None:
            if not _tem_conteudo(pergunta):
                return None
            _, vetor = vetorizar_duvida(pergunta, embedding_service=EmbeddingService.get_instance())

        if threshold is None:
            threshold = settings.SEMANTIC_CACHE_THRESHOLD

        duvida = (
            DuvidaAssimilada.objects
            .no_escopo(
                questao_id=questao_id,
                atividade_id=atividade_id,
                modulo_id=modulo_id,
                somente_globais=somente_globais,
            )
            .utilizaveis()
            .annotate(distancia=CosineDistance('embedding', vetor))
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

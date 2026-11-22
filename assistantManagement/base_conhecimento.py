"""Base de conhecimento local do Coach: ponto único de consulta e assimilação de dúvidas.

Por trás deste serviço existem duas fontes, consultadas nesta ordem:

1. Apostila (EntradaCorpus/PerguntaCorpus): conteúdo curado pelo time, mantido pelo seed_corpus.
2. Caderno (DuvidaAssimilada): respostas da IA externa assimiladas após dúvidas reais dos
   estudantes, com índice HNSW, escopo por atividade e filtro por feedback.

Os handlers do chat e o suporte contextual só conhecem `buscar` e `assimilar_async`: se nada for
encontrado, acionam a IA externa e entregam a resposta para assimilação em background.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from django.conf import settings

from assistantManagement.semantic_cache_service import SemanticCacheService
from semanticSearch.models import DuvidaAssimilada, EntradaCorpus, PerguntaCorpus
from semanticSearch.service.corpus_search import CorpusSearch
from semanticSearch.service.ingestion_service import DuvidaAssimiladaIngestionService
from semanticSearch.service.vetorizacao import vetorizar_duvida

# Valores de Mensagem.origem_resposta para respostas locais.
ORIGEM_APOSTILA = "PLN_LOCAL"
ORIGEM_CACHE_SEMANTICO = "CACHE_SEMANTICO"


@dataclass
class RespostaLocal:
    texto: str
    origem: str
    similaridade: float
    entrada_corpus: Optional[EntradaCorpus] = None
    duvida_assimilada_id: Optional[str] = None


@dataclass
class ResultadoBaseConhecimento:
    resposta: Optional[RespostaLocal] = None
    # Entradas da apostila próximas, mas abaixo do limiar: úteis como "você quis dizer...?"
    relacionadas: list = field(default_factory=list)


class BaseConhecimento:
    @staticmethod
    def buscar(vetor: list[float], topico: Optional[str] = None, questao_id=None) -> ResultadoBaseConhecimento:
        """Consulta apostila e depois caderno.

        `questao_id` informado (dicas) restringe o caderno às dicas daquela questão, já que a resposta
        da IA cita o enunciado; sem ele (dúvidas conceituais do chat), só as dúvidas globais, sem
        atividade, são consideradas.
        """
        threshold = settings.SEMANTIC_CACHE_THRESHOLD

        corpus = CorpusSearch(similarity_threshold=threshold).buscar(vetor, topico=topico)
        if corpus.entrada:
            return ResultadoBaseConhecimento(
                resposta=RespostaLocal(
                    texto=corpus.entrada.resposta,
                    origem=ORIGEM_APOSTILA,
                    similaridade=corpus.similaridade,
                    entrada_corpus=corpus.entrada,
                ),
            )

        cache = SemanticCacheService.buscar_duvida_semelhante(
            vetor=vetor,
            questao_id=questao_id,
            somente_globais=questao_id is None,
            threshold=threshold,
        )
        if cache:
            return ResultadoBaseConhecimento(
                resposta=RespostaLocal(
                    texto=cache["resposta_didatica"],
                    origem=ORIGEM_CACHE_SEMANTICO,
                    similaridade=cache["similaridade"],
                    duvida_assimilada_id=cache["duvida_id"],
                ),
                relacionadas=corpus.relacionadas,
            )

        return ResultadoBaseConhecimento(relacionadas=corpus.relacionadas)

    @classmethod
    def buscar_por_texto(cls, texto: str, topico: Optional[str] = None, questao_id=None) -> ResultadoBaseConhecimento:
        """Vetoriza `texto` e consulta a base; não carrega o modelo de embedding se a base estiver vazia."""
        if not cls._possui_conteudo(questao_id):
            return ResultadoBaseConhecimento()
        _, vetor = vetorizar_duvida(texto)
        return cls.buscar(vetor, topico=topico, questao_id=questao_id)

    @staticmethod
    def _possui_conteudo(questao_id=None) -> bool:
        if PerguntaCorpus.objects.filter(entrada__ativo=True).exists():
            return True
        return (
            DuvidaAssimilada.objects
            .no_escopo(questao_id=questao_id, somente_globais=questao_id is None)
            .utilizaveis()
            .exists()
        )

    @staticmethod
    def assimilar_async(pergunta: str, resposta: str, questao_id=None, atividade_id=None, modulo_id=None):
        """Assimila em background a resposta da IA externa no caderno de dúvidas.

        Dicas informam `questao_id` (e atividade/módulo como contexto); dúvidas conceituais do chat
        não informam questão nem atividade e ficam no escopo global.
        """
        return DuvidaAssimiladaIngestionService.assimilar_duvida_async(
            pergunta=pergunta,
            resposta=resposta,
            questao_id=questao_id,
            atividade_id=atividade_id,
            modulo_id=modulo_id,
        )

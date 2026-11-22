import logging
import threading
from typing import Optional

from django.conf import settings
from django.db import close_old_connections, transaction
from pgvector.django import CosineDistance

from semanticSearch.models import DuvidaAssimilada
from semanticSearch.service.sanitizer import TextSanitizer
from semanticSearch.service.vetorizacao import vetorizar_duvida

logger = logging.getLogger(__name__)

# Tamanho mínimo razoável para uma dúvida conceitual (evita "oi", "valeu", "teste", etc.)
MIN_CARACTERES_DUVIDA = 10
MIN_CARACTERES_RESPOSTA = 20


class DuvidaAssimiladaIngestionService:
    """
    Assimila dúvidas respondidas pela IA externa no caderno de dúvidas (DuvidaAssimilada),
    para que perguntas semelhantes sejam respondidas localmente (VAR-115).

    A apostila (EntradaCorpus/PerguntaCorpus) é conteúdo curado, mantido apenas pelo seed_corpus,
    e não recebe respostas geradas pela IA.
    """

    @classmethod
    def assimilar_duvida(
        cls,
        pergunta: str,
        resposta: str,
        atividade_id=None,
        modulo_id=None,
        questao_id=None,
    ) -> Optional[DuvidaAssimilada]:
        """
        Higieniza, valida, vetoriza e persiste a dúvida de forma transacional.
        Retorna a DuvidaAssimilada criada (ou a duplicata já existente), ou None se os dados
        forem inválidos.
        """
        pergunta_limpa = TextSanitizer.sanitizar(pergunta, remover_saudacao=True)
        resposta_limpa = TextSanitizer.sanitizar(resposta, remover_saudacao=False)

        # 1. Validação de conteúdo mínimo útil
        if len(pergunta_limpa) < MIN_CARACTERES_DUVIDA or len(resposta_limpa) < MIN_CARACTERES_RESPOSTA:
            logger.info(
                "Dúvida descartada por tamanho (pergunta=%d, resposta=%d chars)",
                len(pergunta_limpa),
                len(resposta_limpa),
            )
            return None

        # 2. Vetoriza pelo mesmo pipeline usado na busca
        try:
            pergunta_normalizada, vetor = vetorizar_duvida(pergunta)
        except Exception as exc:
            logger.error("Falha ao gerar embedding para assimilação de dúvida: %s", exc)
            return None

        # 3. Persistência atômica com proteção anti-duplicação semântica no mesmo escopo
        try:
            with transaction.atomic():
                duplicata = cls._buscar_duplicata(vetor, questao_id=questao_id, atividade_id=atividade_id)
                if duplicata is not None:
                    logger.info(
                        "Dúvida quase idêntica já assimilada (ID: %s); evitando duplicação.",
                        duplicata.id,
                    )
                    return duplicata

                duvida = DuvidaAssimilada.objects.create(
                    questao_id=questao_id,
                    atividade_id=atividade_id,
                    modulo_id=modulo_id,
                    pergunta_texto=pergunta_limpa,
                    pergunta_normalizada=pergunta_normalizada,
                    resposta_didatica=resposta_limpa,
                    embedding=vetor,
                )
                logger.info(
                    "Dúvida assimilada (ID: %s, questao=%s, atividade=%s, %d chars)",
                    duvida.id,
                    questao_id,
                    atividade_id,
                    len(pergunta_limpa),
                )
                return duvida

        except Exception as exc:
            logger.error("Erro ao persistir dúvida assimilada: %s", exc)
            return None

    @staticmethod
    def _buscar_duplicata(vetor: list[float], questao_id=None, atividade_id=None) -> Optional[DuvidaAssimilada]:
        # Dúvidas mal avaliadas não contam como duplicata: a nova resposta da IA as substitui na busca.
        candidata = (
            DuvidaAssimilada.objects
            .no_escopo(
                questao_id=questao_id,
                atividade_id=atividade_id,
                somente_globais=questao_id is None and atividade_id is None,
            )
            .utilizaveis()
            .annotate(distancia=CosineDistance("embedding", vetor))
            .order_by("distancia")
            .first()
        )
        if candidata is None:
            return None
        similaridade = 1.0 - float(candidata.distancia)
        return candidata if similaridade >= settings.ANTI_DUPLICATION_THRESHOLD else None

    @classmethod
    def assimilar_duvida_async(
        cls,
        pergunta: str,
        resposta: str,
        atividade_id=None,
        modulo_id=None,
        questao_id=None,
    ) -> threading.Thread:
        """
        Dispara a assimilação em background (thread daemon), sem atrasar a resposta ao estudante,
        liberando as conexões do banco ao concluir.
        """
        def _target():
            try:
                cls.assimilar_duvida(
                    pergunta=pergunta,
                    resposta=resposta,
                    atividade_id=atividade_id,
                    modulo_id=modulo_id,
                    questao_id=questao_id,
                )
            except Exception as e:
                logger.error("Erro inesperado na thread de assimilação de dúvida: %s", e)
            finally:
                close_old_connections()

        thread = threading.Thread(target=_target, daemon=True)
        thread.start()
        return thread

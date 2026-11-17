import logging
import threading
from typing import Optional

from django.db import transaction

from semanticSearch.models import EntradaCorpus, PerguntaCorpus
from semanticSearch.service.sanitizer import TextSanitizer
from semanticSearch.service.text_embedding_service import TextEmbeddingService

logger = logging.getLogger(__name__)

# Tamanho mínimo razoável para uma dúvida conceitual (evita "oi", "valeu", "teste", etc.)
MIN_CARACTERES_DUVIDA = 10
MIN_CARACTERES_RESPOSTA = 20


class CorpusIngestionService:
    """
    Serviço responsável por assimilar dúvidas respondidas pela IA externa,
    vetorizá-las e inseri-las no corpus de busca semântica (VAR-115).
    """

    @classmethod
    def assimilar_duvida(
        cls,
        pergunta: str,
        resposta: str,
        topico: str = "Dúvidas Frequentes",
    ) -> Optional[EntradaCorpus]:
        """
        Higieniza, valida, vetoriza e persiste uma nova entrada no corpus de forma síncrona/transacional.
        Retorna a EntradaCorpus criada/atualizada, ou None caso os dados sejam inválidos/redundantes.
        """
        pergunta_limpa, resposta_limpa = TextSanitizer.preparar_para_corpus(pergunta, resposta)

        # 1. Validação de conteúdo mínimo útil
        if len(pergunta_limpa) < MIN_CARACTERES_DUVIDA or len(resposta_limpa) < MIN_CARACTERES_RESPOSTA:
            logger.info("Dúvida ou resposta muito curta para assimilação no corpus: '%s'", pergunta_limpa)
            return None

        # 2. Gerar vetor de embedding da pergunta aplicando o pipeline padrão de PLN
        try:
            embedding_service = TextEmbeddingService()
            vetor = embedding_service.gerar_embedding(pergunta_limpa)
        except Exception as exc:
            logger.error("Falha ao gerar embedding para assimilação de dúvida: %s", exc)
            return None

        # 3. Persistência atômica e idempotente no banco vetorial
        try:
            with transaction.atomic():
                topico_limpo = (topico or "Dúvidas Frequentes").strip()[:100]

                entrada, criada = EntradaCorpus.objects.get_or_create(
                    pergunta=pergunta_limpa,
                    defaults={
                        "topico": topico_limpo,
                        "resposta": resposta_limpa,
                        "ativo": True,
                    },
                )

                # Se a pergunta já existia com resposta anterior, mantém ou atualiza
                if not criada and not entrada.resposta:
                    entrada.resposta = resposta_limpa
                    entrada.save(update_fields=["resposta"])

                # Garante que a formulação da pergunta com seu embedding esteja registrada em PerguntaCorpus
                pergunta_corpus, _ = PerguntaCorpus.objects.get_or_create(
                    entrada=entrada,
                    texto=pergunta_limpa,
                    defaults={"embedding": vetor},
                )

                logger.info(
                    "Dúvida assimilada no corpus com sucesso (ID: %s, Criada: %s): '%s'",
                    entrada.id,
                    criada,
                    pergunta_limpa,
                )
                return entrada

        except Exception as exc:
            logger.error("Erro ao persistir assimilação de dúvida no corpus: %s", exc)
            return None

    @classmethod
    def assimilar_duvida_async(
        cls,
        pergunta: str,
        resposta: str,
        topico: str = "Dúvidas Frequentes",
    ) -> threading.Thread:
        """
        Dispara a assimilação e vetorização em background (thread daemon),
        garantindo latência zero na resposta ao estudante.
        """
        def _target():
            try:
                cls.assimilar_duvida(pergunta=pergunta, resposta=resposta, topico=topico)
            except Exception as e:
                logger.error("Erro inesperado na thread de assimilação de dúvida: %s", e)

        thread = threading.Thread(target=_target, daemon=True)
        thread.start()
        return thread

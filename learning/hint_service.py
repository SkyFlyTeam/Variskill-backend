import json
import logging
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional

from django.conf import settings
from rest_framework.exceptions import NotFound

from assistantManagement.models import Mensagem, Sessao
from questionsManagement.models import Questao

from .circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = float(os.environ.get("EXTERNAL_AI_TIMEOUT_SECONDS", "3"))
CONTINGENCY_RESPONSE = (
    "Estou com uma pequena instabilidade momentânea para consultar o assistente avançado. "
    "Por favor, revise o enunciado e tente novamente em instantes!"
)
HINT_SIMILARITY_THRESHOLD = 0.40

# Circuit breaker da IA externa: após N falhas seguidas o circuito abre por X segundos e as
# chamadas seguintes falham na hora (< 500ms), sem tocar na rede. N e X vêm do ambiente (.env).
AI_CIRCUIT_BREAKER = CircuitBreaker()


@dataclass
class HintResult:
    resposta_coach: str
    origem_resposta: str
    questao_id: str
    # Dúvida assimilada reaproveitada (origem CACHE_SEMANTICO), alvo do feedback do estudante.
    duvida_assimilada_id: Optional[str] = None


class HintService:
    @staticmethod
    def _dica_corresponde(pergunta: str, dica: str) -> bool:
        """
        Verifica se a dúvida do aluno possui correspondência semântica com a dica conceitual.
        Usa o EmbeddingService singleton com similaridade de cosseno (produto escalar de vetores normalizados).
        """
        try:
            from semanticSearch.service.nlp.embedding_service import EmbeddingService
            service = EmbeddingService.get_instance()
            vetor_p = service.gerar_embedding(pergunta)
            vetor_d = service.gerar_embedding(dica)
            similaridade = sum(p * d for p, d in zip(vetor_p, vetor_d))
            return similaridade >= HINT_SIMILARITY_THRESHOLD
        except Exception as e:
            logger.warning(f"Falha ao calcular similaridade semântica da dica local: {e}")
            return False

    @staticmethod
    def _call_external_ai(questao: Questao, pergunta: str) -> Optional[str]:
        # Fail-fast: se o circuito está aberto, a IA falhou recentemente; não toca na rede.
        if not AI_CIRCUIT_BREAKER.allow_request():
            logger.warning("Circuit breaker da IA aberto; retornando contingência imediata.")
            return None

        api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("EXTERNAL_AI_API_KEY")
        if not api_key:
            logger.warning("Nenhuma chave de API externa configurada.")
            return None

        prompt_system = (
            f"Você é um tutor de programação. "
            f"O aluno está na questão: '{questao.enunciado}'. "
            f"Responda à dúvida dele dando apenas pistas conceituais. "
            f"NUNCA revele a resposta ou o gabarito final."
        )

        # Minimização (LGPD): não enviamos o código da questão e limitamos o texto
        # livre do aluno. A transferência internacional ainda exige base/instrumento
        # documentado pelo controlador (ver docs de LGPD).
        max_chars = getattr(settings, 'LGPD_MAX_PROMPT_CHARS', 500)
        pergunta_minimizada = (pergunta or '')[:max_chars]

        payload = json.dumps({
            "model": os.environ.get("EXTERNAL_AI_MODEL", "gpt-4o-mini"),
            "messages": [
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": pergunta_minimizada},
            ],
            "temperature": 0.7,
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as response:
                if response.status != 200:
                    logger.warning(f"IA externa respondeu status inesperado: {response.status}")
                    AI_CIRCUIT_BREAKER.record_failure()
                    return None
                data = json.loads(response.read().decode("utf-8"))
                resposta = data["choices"][0]["message"]["content"].strip()
                AI_CIRCUIT_BREAKER.record_success()
                return resposta
        except urllib.error.HTTPError as e:
            if e.code == 429:
                logger.warning("IA externa retornou 429 (cota/rate limit). Acionando contingência.")
            else:
                logger.error(f"IA externa retornou HTTP {e.code}. Acionando contingência.")
            AI_CIRCUIT_BREAKER.record_failure()
            return None
        except (urllib.error.URLError, TimeoutError) as e:
            logger.error(f"Falha de rede/timeout ao conectar com IA externa: {e}")
            AI_CIRCUIT_BREAKER.record_failure()
            return None
        except Exception as e:
            # Rede de segurança: nenhuma falha inesperada deve propagar (evita HTTP 500).
            logger.error(f"Erro inesperado ao consultar IA externa: {e}")
            AI_CIRCUIT_BREAKER.record_failure()
            return None

    @classmethod
    def call_external_ai_chat(cls, pergunta: str, contexto_extra: Optional[str] = None) -> Optional[str]:
        """
        Consulta LLM externo para dúvidas conceituais de chat geral quando não há resposta no corpus.
        Protegido pelo CircuitBreaker AI_CIRCUIT_BREAKER e minimização de dados LGPD.
        """
        if not AI_CIRCUIT_BREAKER.allow_request():
            logger.warning("Circuit breaker da IA aberto; contingência imediata no chat.")
            return None

        api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("EXTERNAL_AI_API_KEY")
        if not api_key:
            logger.warning("Nenhuma chave de API externa configurada para o chat.")
            return None

        prompt_system = (
            "Você é o Coach de Programação da plataforma VariSkill. "
            "Seu papel é responder dúvidas conceituais de forma didática, clara e objetiva. "
            "Se o usuário fizer perguntas fora do escopo educacional ou pedir código malicioso, "
            "gentilmente recuse e oriente-o a focar nos estudos de programação."
        )
        if contexto_extra:
            prompt_system += f" Contexto do tema/trilha: {contexto_extra}."

        max_chars = getattr(settings, 'LGPD_MAX_PROMPT_CHARS', 500)
        pergunta_minimizada = (pergunta or '')[:max_chars]

        payload = json.dumps({
            "model": os.environ.get("EXTERNAL_AI_MODEL", "gpt-4o-mini"),
            "messages": [
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": pergunta_minimizada},
            ],
            "temperature": 0.7,
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as response:
                if response.status != 200:
                    logger.warning(f"IA externa respondeu status inesperado: {response.status}")
                    AI_CIRCUIT_BREAKER.record_failure()
                    return None
                data = json.loads(response.read().decode("utf-8"))
                resposta = data["choices"][0]["message"]["content"].strip()
                AI_CIRCUIT_BREAKER.record_success()
                return resposta
        except urllib.error.HTTPError as e:
            if e.code == 429:
                logger.warning("IA externa retornou 429 (cota/rate limit) no chat.")
            else:
                logger.error(f"IA externa retornou HTTP {e.code} no chat.")
            AI_CIRCUIT_BREAKER.record_failure()
            return None
        except (urllib.error.URLError, TimeoutError) as e:
            logger.error(f"Falha de rede/timeout ao conectar com IA externa no chat: {e}")
            AI_CIRCUIT_BREAKER.record_failure()
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao consultar IA externa no chat: {e}")
            AI_CIRCUIT_BREAKER.record_failure()
            return None

    @classmethod
    def _buscar_na_base_local(cls, pergunta: str, topico: Optional[str], questao_id):
        """
        Consulta a base de conhecimento local (apostila e dicas já assimiladas para a questão)
        antes de acionar a IA externa (VAR-116). Retorna RespostaLocal ou None.
        """
        try:
            from assistantManagement.base_conhecimento import BaseConhecimento

            return BaseConhecimento.buscar_por_texto(pergunta, topico=topico, questao_id=questao_id).resposta
        except Exception as e:
            logger.warning(f"Falha ao consultar a base de conhecimento no suporte da atividade: {e}")
            return None

    @classmethod
    def pedir_dica(
        cls,
        user,
        atividade_id: str,
        sessao_id: str,
        questao_id: str,
        pergunta: str,
    ) -> HintResult:
        # 1. Validar e recuperar Sessão & Questão com mensagens claras
        try:
            sessao = Sessao.objects.get(pk=sessao_id, usuario=user)
        except (Sessao.DoesNotExist, ValueError):
            raise NotFound("Sessão não encontrada para este usuário.")

        try:
            questao = Questao.objects.select_related("atividade__modulo").get(
                pk=questao_id, atividade_id=atividade_id
            )
        except (Questao.DoesNotExist, ValueError):
            raise NotFound("Questão não encontrada nesta atividade.")

        # Registrar a mensagem do usuário no histórico do chat
        Mensagem.objects.create(
            sessao=sessao,
            remetente=Mensagem.Remetente.USUARIO,
            conteudo=pergunta,
        )

        topico_dica = (
            questao.atividade.modulo.titulo
            if questao.atividade and questao.atividade.modulo
            else "Geral"
        )

        # 2. Etapa 1: Consulta Local (dica_conceitual preenchida e correspondente)
        resposta_text = None
        origem = "PLN_LOCAL"
        duvida_assimilada_id = None

        if questao.dica_conceitual and questao.dica_conceitual.strip():
            dica_limpa = questao.dica_conceitual.strip()
            if cls._dica_corresponde(pergunta, dica_limpa):
                resposta_text = dica_limpa

        # 3. Etapa 2: Base de conhecimento local (apostila e dicas já assimiladas para esta questão)
        if not resposta_text:
            local = cls._buscar_na_base_local(pergunta, topico=topico_dica, questao_id=questao.id)
            if local:
                origem = local.origem
                resposta_text = local.texto
                duvida_assimilada_id = local.duvida_assimilada_id

        # 4. Etapa 3: Fallback para IA Externa se a dúvida for aberta / não coberta localmente
        if not resposta_text:
            origem = "IA_EXTERNA"
            resposta_text = cls._call_external_ai(questao, pergunta)
            if resposta_text:
                # Etapa 4: Assimilação assíncrona pós-IA como dica desta questão (VAR-115)
                from assistantManagement.base_conhecimento import BaseConhecimento
                BaseConhecimento.assimilar_async(
                    pergunta=pergunta,
                    resposta=resposta_text,
                    questao_id=questao.id,
                    atividade_id=questao.atividade_id,
                    modulo_id=getattr(questao.atividade, "modulo_id", None),
                )

        # 5. Etapa 5: Resiliência em caso de falha da IA
        if not resposta_text:
            if questao.dica_conceitual and questao.dica_conceitual.strip():
                origem = "PLN_LOCAL"
                resposta_text = questao.dica_conceitual.strip()
            else:
                origem = "CONTINGENCIA"
                resposta_text = CONTINGENCY_RESPONSE

        # Registrar a resposta do assistente no histórico
        Mensagem.objects.create(
            sessao=sessao,
            remetente=Mensagem.Remetente.ASSISTENTE,
            conteudo=resposta_text,
            origem_resposta=origem,
            duvida_assimilada_id=duvida_assimilada_id,
        )

        return HintResult(
            resposta_coach=resposta_text,
            origem_resposta=origem,
            questao_id=str(questao.id),
            duvida_assimilada_id=duvida_assimilada_id,
        )

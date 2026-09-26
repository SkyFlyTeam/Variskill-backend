import json
import logging
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional

from assistantManagement.models import Mensagem, Sessao
from questionsManagement.models import Questao

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 5
CONTINGENCY_RESPONSE = (
    "Estou com uma pequena instabilidade momentânea para consultar o assistente avançado. "
    "Por favor, revise o enunciado e tente novamente em instantes!"
)


@dataclass
class HintResult:
    resposta_coach: str
    origem_resposta: str
    questao_id: str


class HintService:
    @staticmethod
    def _call_external_ai(questao: Questao, pergunta: str) -> Optional[str]:
        api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("EXTERNAL_AI_API_KEY")
        if not api_key:
            logger.warning("Nenhuma chave de API externa configurada.")
            return None

        prompt_system = (
            f"Você é um tutor de programação. "
            f"O aluno está na questão: '{questao.enunciado}' com o código '{questao.codigo_snippet}'. "
            f"Responda à dúvida dele dando apenas pistas conceituais. NUNCA revele a resposta ou o gabarito final."
        )

        payload = json.dumps({
            "model": os.environ.get("EXTERNAL_AI_MODEL", "gpt-4o-mini"),
            "messages": [
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": pergunta},
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
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    return data["choices"][0]["message"]["content"].strip()
                return None
        except Exception as e:
            logger.error(f"Falha/Timeout ao conectar com IA externa: {e}")
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
        # 1. Validar e recuperar Sessão & Questão
        sessao = Sessao.objects.get(pk=sessao_id, usuario=user)
        questao = Questao.objects.get(pk=questao_id, atividade_id=atividade_id)

        # Registrar a mensagem do usuário no histórico do chat
        Mensagem.objects.create(
            sessao=sessao,
            remetente=Mensagem.Remetente.USUARIO,
            conteudo=pergunta,
        )

        # 2. Etapa 1: Consulta Local (dica_conceitual)
        resposta_text = None
        origem = "PLN_LOCAL"

        if questao.dica_conceitual and questao.dica_conceitual.strip():
            resposta_text = questao.dica_conceitual.strip()

        # 3. Etapa 2: Fallback para IA Externa se não houver dica local
        if not resposta_text:
            origem = "IA_EXTERNA"
            resposta_text = cls._call_external_ai(questao, pergunta)

        # 4. Etapa 3: Resiliência em caso de falha da IA
        if not resposta_text:
            origem = "CONTINGENCIA"
            resposta_text = CONTINGENCY_RESPONSE

        # Registrar a resposta do assistente no histórico
        Mensagem.objects.create(
            sessao=sessao,
            remetente=Mensagem.Remetente.ASSISTENTE,
            conteudo=resposta_text,
        )

        return HintResult(
            resposta_coach=resposta_text,
            origem_resposta=origem,
            questao_id=str(questao.id),
        )

"""
Geração de trilhas com IA generativa: quando o estudante pede para aprender um tema que nenhuma
trilha ativa cobre (ex.: "Quero aprender culinária, por onde começo?"), o Coach pede à IA externa
uma trilha introdutória e a persiste no mesmo formato do catálogo (seed_catalogo_completo.py):
cada módulo tem uma lição teórica (CONTEUDO) e um exercício de múltipla escolha.

A IA também recebe o catálogo atual e pode indicar uma trilha existente que já cubra o tema
(ex.: "programação" -> "Python: Fundamentos"), evitando trilhas duplicadas.
"""
import logging
import os
import unicodedata
from dataclasses import dataclass
from typing import Optional

from django.db import transaction

from activityManagement.models import Atividade, Conteudo
from learning.hint_service import HintService
from questionsManagement.models import Questao, QuestaoOpcao
from trackManagement.models import Modulo, Trilha

logger = logging.getLogger(__name__)

# Gerar uma trilha inteira leva bem mais que uma dica: timeout próprio, configurável no .env.
TIMEOUT_GERACAO_SEGUNDOS = float(os.environ.get("EXTERNAL_AI_TRAIL_TIMEOUT_SECONDS", "60"))

MIN_MODULOS, MAX_MODULOS = 2, 4
MIN_QUESTOES, MAX_QUESTOES = 2, 5
QUESTOES_PEDIDAS = 3
OPCOES_POR_QUESTAO = 4
NIVEIS_MODULO = ("INICIANTE", "INTERMEDIARIO", "AVANCADO")
XP_LICAO = 50
XP_EXERCICIO = 100
# Cada estudante pode originar poucas trilhas: elas ficam visíveis para todos assim que criadas.
LIMITE_TRILHAS_GERADAS_POR_USUARIO = 2

RESULTADO_NOVA_TRILHA = "NOVA_TRILHA"
RESULTADO_TRILHA_EXISTENTE = "TRILHA_EXISTENTE"
RESULTADO_FORA_DE_ESCOPO = "FORA_DE_ESCOPO"

PROMPT_GERACAO = (
    "Você é o designer instrucional da plataforma de ensino VariSkill. O estudante quer aprender um tema. "
    "Responda em português do Brasil, preenchendo o campo resultado:\n"
    f"- {RESULTADO_FORA_DE_ESCOPO}: o pedido não é um tema educacional apropriado (ofensivo, perigoso, "
    "ilegal, sem sentido ou sem tema);\n"
    f"- {RESULTADO_TRILHA_EXISTENTE}: alguma trilha do catálogo abaixo já cobre o tema ou é um bom ponto de "
    "partida para ele (ex.: programação -> uma trilha de fundamentos de programação); informe o título exato "
    "dela em trilha_existente;\n"
    f"- {RESULTADO_NOVA_TRILHA}: crie em trilha uma trilha introdutória sobre o tema.\n"
    "Na trilha nova: titulo no formato \"Tema: Subtítulo\" (até 100 caracteres), descricao em 1 a 2 frases, "
    f"habilidade com o nome curto do tema (até 50 caracteres) e de {MIN_MODULOS} a {MAX_MODULOS} módulos, "
    "do básico ao avançado. Cada módulo tem uma licao em Markdown (150 a 300 palavras, com títulos ### e "
    f"exemplos práticos) e exatamente {QUESTOES_PEDIDAS} questões de múltipla escolha sobre a lição, com "
    f"{OPCOES_POR_QUESTAO} opções, gabarito_idx (índice da opção correta) e uma dica que não entrega a resposta.\n"
    "Catálogo atual:\n"
)


def _objeto(propriedades: dict) -> dict:
    """Objeto do JSON Schema no modo strict: todos os campos obrigatórios e nenhum campo extra."""
    return {
        "type": "object",
        "properties": propriedades,
        "required": list(propriedades),
        "additionalProperties": False,
    }


_TEXTO = {"type": "string"}

# Structured Outputs: a IA externa responde exatamente neste formato (sem aninhar questões na lição etc.).
SCHEMA_GERACAO = _objeto({
    "resultado": {"type": "string", "enum": [RESULTADO_NOVA_TRILHA, RESULTADO_TRILHA_EXISTENTE, RESULTADO_FORA_DE_ESCOPO]},
    "trilha_existente": {"type": ["string", "null"]},
    "trilha": {"anyOf": [
        {"type": "null"},
        _objeto({
            "titulo": _TEXTO,
            "descricao": _TEXTO,
            "habilidade": _TEXTO,
            "modulos": {"type": "array", "minItems": MIN_MODULOS, "maxItems": MAX_MODULOS, "items": _objeto({
                "titulo": _TEXTO,
                "descricao": _TEXTO,
                "nivel": {"type": "string", "enum": list(NIVEIS_MODULO)},
                "licao": _objeto({"titulo": _TEXTO, "texto": _TEXTO}),
                "questoes": {"type": "array", "minItems": QUESTOES_PEDIDAS, "maxItems": QUESTOES_PEDIDAS, "items": _objeto({
                    "enunciado": _TEXTO,
                    "opcoes": {
                        "type": "array", "minItems": OPCOES_POR_QUESTAO, "maxItems": OPCOES_POR_QUESTAO, "items": _TEXTO,
                    },
                    "gabarito_idx": {"type": "integer", "enum": list(range(OPCOES_POR_QUESTAO))},
                    "dica": _TEXTO,
                })},
            })},
        }),
    ]},
})


@dataclass
class ResultadoGeracao:
    trilha: Trilha
    # False quando a IA indicou uma trilha já existente no catálogo.
    criada: bool


def _normalizar(texto: str) -> str:
    decomposto = unicodedata.normalize("NFKD", (texto or "").lower())
    return " ".join("".join(c for c in decomposto if unicodedata.category(c) != "Mn").split())


def _texto(valor, limite: Optional[int] = None) -> str:
    texto = valor.strip() if isinstance(valor, str) else ""
    return texto[:limite].strip() if limite else texto


def _questao_valida(questao) -> bool:
    if not isinstance(questao, dict) or not _texto(questao.get("enunciado")):
        return False
    opcoes = questao.get("opcoes")
    if not isinstance(opcoes, list) or len(opcoes) != OPCOES_POR_QUESTAO or not all(_texto(o) for o in opcoes):
        return False
    gabarito = questao.get("gabarito_idx")
    return isinstance(gabarito, int) and not isinstance(gabarito, bool) and 0 <= gabarito < OPCOES_POR_QUESTAO


def _questoes_do_modulo(modulo: dict) -> list:
    questoes = modulo.get("questoes") if isinstance(modulo.get("questoes"), list) else []
    return [q for q in questoes if _questao_valida(q)][:MAX_QUESTOES]


def _motivo_modulo_invalido(modulo) -> Optional[str]:
    if not isinstance(modulo, dict) or not _texto(modulo.get("titulo")):
        return "módulo sem título"
    licao = modulo.get("licao")
    if not isinstance(licao, dict) or not _texto(licao.get("texto")):
        return "módulo sem texto da lição"
    if len(_questoes_do_modulo(modulo)) < MIN_QUESTOES:
        return f"módulo com menos de {MIN_QUESTOES} questões válidas"
    return None


def _validar_trilha(dados) -> tuple[Optional[dict], Optional[str]]:
    """
    Confere a estrutura gerada pela IA e retorna (trilha normalizada, motivo da rejeição). Módulos e
    questões malformados são descartados; a trilha só é rejeitada se sobrar menos que o mínimo.
    """
    if not isinstance(dados, dict):
        return None, "resposta sem o objeto trilha"
    if not _texto(dados.get("titulo")) or not _texto(dados.get("habilidade")):
        return None, "trilha sem título ou habilidade"
    modulos_gerados = dados.get("modulos") if isinstance(dados.get("modulos"), list) else []
    motivos = [_motivo_modulo_invalido(m) for m in modulos_gerados]
    modulos = [
        {**m, "questoes": _questoes_do_modulo(m)} for m, motivo in zip(modulos_gerados, motivos) if motivo is None
    ][:MAX_MODULOS]
    if len(modulos) < MIN_MODULOS:
        descartados = "; ".join(m for m in motivos if m) or f"a IA gerou só {len(modulos_gerados)}"
        return None, f"{len(modulos)} módulo(s) válido(s), mínimo {MIN_MODULOS} ({descartados})"
    return {**dados, "modulos": modulos}, None


def _trilha_existente(titulo: str, trilhas: list) -> Optional[Trilha]:
    alvo = _normalizar(titulo)
    return next((t for t in trilhas if _normalizar(t.titulo) == alvo), None) if alvo else None


def _trilha_com_mesmo_tema(dados: dict) -> Optional[Trilha]:
    """Trilha ativa com o mesmo título ou habilidade (ex.: gerada em paralelo por outro estudante)."""
    titulo, habilidade = _normalizar(dados["titulo"]), _normalizar(dados["habilidade"])
    return next(
        (t for t in Trilha.objects.filter(ativo=True)
         if _normalizar(t.titulo) == titulo or _normalizar(t.habilidade) == habilidade),
        None,
    )


def _criar_questao(atividade: Atividade, dados: dict, ordem: int, peso: int):
    opcoes = [_texto(o) for o in dados["opcoes"]]
    gabarito_idx = dados["gabarito_idx"]
    questao = Questao.objects.create(
        atividade=atividade,
        tipo_exercicio="MULTIPLA_ESCOLHA",
        enunciado=_texto(dados["enunciado"]),
        gabarito_esperado="",
        explicacao=f"A resposta correta é: {opcoes[gabarito_idx]}",
        dica_conceitual=_texto(dados.get("dica")),
        ordem_questao=ordem,
        peso_pontuacao=peso,
    )
    # Como no catálogo, o gabarito de múltipla escolha é o id da opção correta.
    ids = [
        QuestaoOpcao.objects.create(questao=questao, texto_opcao=texto, ordem=idx).id
        for idx, texto in enumerate(opcoes, start=1)
    ]
    questao.gabarito_esperado = str(ids[gabarito_idx])
    questao.save(update_fields=["gabarito_esperado"])


def _distribuir_pontuacao(xp_total: int, quantidade: int) -> list:
    """Divide o XP da atividade entre as questões; a soma dos pesos é sempre igual ao XP."""
    base, resto = divmod(xp_total, quantidade)
    return [base + (1 if i < resto else 0) for i in range(quantidade)]


def limite_de_trilhas_geradas_atingido(usuario) -> bool:
    return Trilha.objects.filter(criada_por=usuario, gerada_por_ia=True).count() >= LIMITE_TRILHAS_GERADAS_POR_USUARIO


@transaction.atomic
def _persistir_trilha(dados: dict, usuario) -> Trilha:
    trilha = Trilha.objects.create(
        titulo=_texto(dados["titulo"], 100),
        descricao=_texto(dados.get("descricao")),
        habilidade=_texto(dados["habilidade"], 50),
        ativo=True,
        gerada_por_ia=True,
        criada_por=usuario,
    )
    for ordem_modulo, dados_modulo in enumerate(dados["modulos"], start=1):
        nivel = _texto(dados_modulo.get("nivel")).upper()
        modulo = Modulo.objects.create(
            trilha=trilha,
            titulo=_texto(dados_modulo["titulo"], 100),
            descricao=_texto(dados_modulo.get("descricao")),
            nivel=nivel if nivel in NIVEIS_MODULO else "INICIANTE",
            ordem_modulo=ordem_modulo,
        )

        licao = dados_modulo["licao"]
        titulo_licao = _texto(licao.get("titulo"), 255) or modulo.titulo
        conteudo = Conteudo.objects.create(
            titulo=titulo_licao, texto_explicativo=_texto(licao["texto"]), tempo_estimado_minutos=5,
        )
        Atividade.objects.create(
            modulo=modulo, conteudo=conteudo, titulo=titulo_licao, descricao=modulo.descricao,
            contexto_avaliacao="FORMATIVA", xp_recompensa=XP_LICAO, ordem=1,
        )

        questoes = dados_modulo["questoes"]
        exercicio = Atividade.objects.create(
            modulo=modulo, titulo=f"Exercício: {modulo.titulo}"[:255],
            descricao=f"Teste o que você aprendeu em {modulo.titulo}.",
            contexto_avaliacao="FORMATIVA", xp_recompensa=XP_EXERCICIO, ordem=2,
        )
        pesos = _distribuir_pontuacao(XP_EXERCICIO, len(questoes))
        for ordem, (dados_questao, peso) in enumerate(zip(questoes, pesos), start=1):
            _criar_questao(exercicio, dados_questao, ordem, peso)

    return trilha


def gerar_trilha_por_tema(pedido: str, trilhas_ativas: list, usuario) -> Optional[ResultadoGeracao]:
    """
    Pede à IA externa uma trilha para o tema do pedido do estudante. Retorna a trilha criada, a trilha
    do catálogo que a IA indicou para o tema ou None (IA indisponível, tema fora de escopo, resposta
    inválida ou limite de trilhas do estudante atingido), caso em que o Coach segue com a recomendação
    por interesses.
    """
    catalogo = "\n".join(f"- {t.titulo} ({t.habilidade})" for t in trilhas_ativas) or "(vazio)"
    resposta = HintService.call_external_ai_json(
        PROMPT_GERACAO + catalogo, pedido, timeout=TIMEOUT_GERACAO_SEGUNDOS,
        schema=SCHEMA_GERACAO, nome_schema="trilha_gerada",
    )
    if not resposta or resposta.get("resultado") == RESULTADO_FORA_DE_ESCOPO:
        return None

    if resposta.get("resultado") == RESULTADO_TRILHA_EXISTENTE:
        existente = _trilha_existente(_texto(resposta.get("trilha_existente")), trilhas_ativas)
        if existente:
            return ResultadoGeracao(existente, criada=False)
        logger.warning("IA externa indicou uma trilha que não está no catálogo; geração descartada.")
        return None

    dados, motivo = _validar_trilha(resposta.get("trilha"))
    if dados is None:
        logger.warning(f"IA externa respondeu uma trilha fora do formato esperado ({motivo}); geração descartada.")
        return None

    mesmo_tema = _trilha_com_mesmo_tema(dados)
    if mesmo_tema:
        return ResultadoGeracao(mesmo_tema, criada=False)
    # Confere de novo: outro pedido do mesmo estudante pode ter criado uma trilha durante a geração.
    if limite_de_trilhas_geradas_atingido(usuario):
        return None
    return ResultadoGeracao(_persistir_trilha(dados, usuario), criada=True)

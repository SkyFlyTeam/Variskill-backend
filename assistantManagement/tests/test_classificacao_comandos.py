"""
Precisão da classificação dos comandos do chat com o modelo real (spaCy + MiniLM + pgvector).

Cada comando tem variações de frase, incluindo os Quick Chips gerados pelo backend, e deve
acertar a intenção esperada em pelo menos 90% delas. Os chips em si devem acertar sempre:
são o caminho principal do estudante no frontend.
"""
import pytest
from django.core.management import call_command

from activityManagement.models import Atividade
from assistantManagement.services import (
    MODELO_SUGESTAO_REFORCO,
    MODELO_SUGESTAO_RETOMADA,
    SUGESTOES_AJUDA,
    SUGESTOES_FALLBACK,
    SUGESTOES_INICIAIS,
    SUGESTOES_JORNADA,
    SUGESTOES_NIVELAMENTO,
    _preencher,
    classificar_mensagem,
)
from intents.models import Intention
from trackManagement.models import Modulo, Trilha

pytestmark = [pytest.mark.integration, pytest.mark.django_db]

TAXA_MINIMA_ACERTO = 0.9

# Trilha -> habilidade e módulos (módulo -> atividade), com os títulos do catálogo real.
CATALOGO = {
    ("Python: Fundamentos", "Python"): {
        "Variaveis, Tipos de Dados e Operadores": "Tipos Primitivos, Mutabilidade e Atribuicao",
        "Controle de Fluxo e Condicionais": "Estruturas Condicionais, Logica Booleana e PEP 8",
        "Estruturas de Repeticao (For e While)": "Lacos de Repeticao, Intervalos e Controle de Fluxo",
        "Colecoes de Dados (Listas, Tuplas e Dicionarios)": "Colecoes de Dados: Listas, Tuplas, Dicionarios e Sets",
        "Funcoes, Parametros e Escopo": "Funcoes, Parametros, *args, **kwargs e Escopo",
    },
    ("Python: Desenvolvimento Web", "Backend"): {
        "Fundamentos da Web, Protocolo HTTP e APIs": "O Protocolo HTTP, Arquitetura RESTful e Status Codes",
        "FastAPI: Rotas, Path e Query Parameters": "FastAPI: Arquitetura ASGI, Rotas e Parametros",
        "Autenticacao Segura com Tokens JWT": "Autenticacao Stateless com JWT, Hashing e Seguranca",
    },
    ("Python: Analise de Dados", "Ciência de Dados"): {
        "Computacao Numerica e Vetorizacao com NumPy": "Computacao Cientifica e Vetorizacao com NumPy",
        "Manipulacao Tabular com Pandas Series e DataFrames": "Estruturas Tabulares: Pandas Series e DataFrames",
        "Limpeza, Filtros e Tratamento de Dados Ausentes": "Limpeza, Dados Ausentes (NaN) e Mascaras Booleanas",
    },
    ("JavaScript: Fundamentos", "JavaScript"): {
        "Variaveis, Tipos e Operadores": "Declaracao de Variaveis com let e const",
        "Funcoes, Arrays e Objetos": "Arrow Functions e Metodos de Array",
    },
    ("Banco de Dados: SQL e Modelagem", "Banco de Dados"): {
        "Consultas SQL Essenciais": "SELECT, WHERE e ORDER BY",
        "Modelagem Relacional e JOINs": "Chaves Estrangeiras e JOINs",
    },
}
TRILHAS = [titulo for titulo, _ in CATALOGO]
MODULOS = [modulo for modulos in CATALOGO.values() for modulo in modulos]
ATIVIDADES = [atividade for modulos in CATALOGO.values() for atividade in modulos.values()]

# Quick Chips da saudação (VAR-119): "Continuar <atividade>" e "Quero revisar <módulo>".
CHIPS_RETOMADA = [_preencher(MODELO_SUGESTAO_RETOMADA, nome_atividade=a) for a in ATIVIDADES]
CHIPS_REFORCO = [_preencher(MODELO_SUGESTAO_REFORCO, topico_dificuldade=m) for m in MODULOS]

# Intenção esperada de cada chip fixo do backend (SUGESTOES_* e chips dos handlers).
CHIPS_FIXOS = {
    "Me recomende uma trilha": "RECOMENDAR_TRILHA",
    "Ver trilhas disponíveis": "LISTAR_TRILHAS",
    "Quais trilhas estão disponíveis?": "LISTAR_TRILHAS",
    "Como funciona a plataforma?": "AJUDA_COMANDOS",
    "Como funciona o Coach?": "AJUDA_COMANDOS",
    "Quero me matricular em uma trilha": "MATRICULAR_TRILHA",
    "Quero fazer o teste de nivelamento": "INICIAR_DIAGNOSTICO",
    "Quero começar do zero": "INICIAR_DO_ZERO",
    "Pode me dar uma dica?": "PEDIR_DICA",
    "Como definir uma variável em Python?": "DUVIDA_CONTEUDO",
    "Qual meu nível?": "CONSULTAR_NIVEL",
    "O que estudar agora?": "PROXIMA_ATIVIDADE",
    "Tirar uma dúvida": "DUVIDA_CONTEUDO",
    "Ver meu progresso": "CONSULTAR_NIVEL",
}
# Chips com o nome da trilha (_pedir_escolha_de_trilha, matrícula e recomendação por tema).
CHIPS_COM_TRILHA = {
    "Quero me matricular na trilha {titulo}": "MATRICULAR_TRILHA",
    "Confirmo minha matrícula na trilha {titulo}": "MATRICULAR_TRILHA",
    "Quero fazer o teste de nivelamento da trilha {titulo}": "INICIAR_DIAGNOSTICO",
    "Quero começar do zero na trilha {titulo}": "INICIAR_DO_ZERO",
    "Quero aprender {titulo}": "RECOMENDAR_TRILHA",
}

# Variações livres (o estudante digitando) de cada comando.
VARIACOES = {
    "PROXIMA_ATIVIDADE": [
        "Continuar uma trilha",
        "Continuar a trilha",
        "Continuar minha trilha",
        "Quero continuar minha trilha",
        "Continuar de onde parei",
        "Posso continuar de onde parei?",
        "Quero continuar de onde eu parei",
        "Continuar estudando",
        "Continuar a atividade",
        "Continuar a lição",
        "Continuar o curso",
        "Seguir com a minha trilha",
        "Retomar minha trilha",
        "Voltar para a minha trilha",
        "Qual a próxima atividade?",
        "Qual minha próxima lição?",
        "O que eu faço agora na trilha?",
        "Me leva para o próximo exercício",
        "Continuar",
        "Quero continuar",
        "Continuar a atividade Estruturas Condicionais, Logica Booleana e PEP 8",
        "Continuar minha trilha de Python",
    ],
    "DUVIDA_CONTEUDO": [
        "Revisar conteúdo",
        "Quero revisar o conteúdo",
        "Quero revisar esse conteúdo",
        "Quero revisar esse assunto",
        "Quero revisar esse conceito",
        "Preciso revisar a matéria",
        "Me ajuda a revisar",
        "Revisar Funcoes, Parametros e Escopo",
        "Preciso revisar Controle de Fluxo e Condicionais",
        "Quero revisar listas e dicionários",
        "Me ajuda a revisar laços de repetição",
        "Quero reforçar Consultas SQL Essenciais",
        "Revisão de variáveis e tipos de dados",
        "Quero revisar Funcoes, Parametros e Escopo. Me dá uma dica de estudo?",
        "Quero revisar Modelagem Relacional e JOINs. Me dá uma dica de estudo?",
        "Tenho dificuldade com variáveis em Python",
        "Como funciona o laço for?",
        "O que é uma lista em Python?",
        "Qual a diferença entre lista e tupla?",
        "Quero tirar uma dúvida",
    ],
    "RECOMENDAR_TRILHA": [
        "Qual trilha você me recomenda?",
        "Me recomende uma trilha",
        "Qual trilha devo estudar?",
        "Me sugira uma trilha",
        "Quero aprender programação, por onde começo?",
        "Não sei por onde começar",
        "Quero aprender pandas, qual trilha faço?",
        "Quero aprender SQL, por onde começo?",
        "Quero estudar banco de dados",
        "Qual curso combina comigo?",
    ],
    "LISTAR_TRILHAS": [
        "Quais trilhas estão disponíveis?",
        "Ver trilhas disponíveis",
        "Quero ver as trilhas",
        "Me mostre as trilhas",
        "Listar trilhas",
        "Que trilhas posso fazer?",
        "Quais cursos vocês têm?",
    ],
    "CONSULTAR_NIVEL": [
        "Qual meu nível?",
        "Ver meu progresso",
        "Quanto XP eu tenho?",
        "Quanto falta para o próximo nível?",
        "Em que nível estou?",
        "Quero ver meu XP",
        "Como está meu progresso?",
    ],
    "PEDIR_DICA": [
        "Pode me dar uma dica?",
        "Me dá uma dica",
        "Preciso de uma dica para essa questão",
        "Tem alguma pista para esta atividade?",
        "Me ajuda sem dar a resposta",
        "Não sei resolver essa questão, me dá uma dica",
        "Estou travado nessa questão",
    ],
    "INICIAR_DIAGNOSTICO": [
        "Quero fazer o teste de nivelamento",
        "Fazer o teste de nivelamento",
        "Quero testar meu nível",
        "Quero fazer a avaliação diagnóstica",
        "Já sei programar, quero fazer o nivelamento",
    ],
    "INICIAR_DO_ZERO": [
        "Quero começar do zero",
        "Começar do zero",
        "Sou iniciante, quero começar pelo básico",
        "Prefiro começar do zero",
        "Não quero fazer o teste, quero começar do zero",
    ],
    "MATRICULAR_TRILHA": [
        "Quero me matricular em uma trilha",
        "Quero me inscrever na trilha",
        "Como faço minha matrícula?",
        "Me matricula na trilha",
        "Quero me matricular",
    ],
    "AJUDA_COMANDOS": [
        "Como funciona a plataforma?",
        "Como funciona o Coach?",
        "O que você pode fazer?",
        "Quais comandos estão disponíveis?",
        "Como você pode me ajudar?",
    ],
    "SAUDACAO": [
        "Olá",
        "Oi, tudo bem?",
        "Bom dia",
        "Boa noite, Coach",
        "Voltei",
    ],
}


@pytest.fixture(scope="module")
def trilhas(django_db_setup, django_db_blocker):
    """Catálogo e intenções semeados uma vez para o módulo (o seed gera embeddings com o modelo real)."""
    with django_db_blocker.unblock():
        criadas = []
        for (titulo, habilidade), modulos in CATALOGO.items():
            trilha = Trilha.objects.create(titulo=titulo, habilidade=habilidade, ativo=True)
            for ordem, (modulo_titulo, atividade_titulo) in enumerate(modulos.items(), start=1):
                modulo = Modulo.objects.create(
                    trilha=trilha, titulo=modulo_titulo, nivel="Iniciante", ordem_modulo=ordem,
                )
                Atividade.objects.create(
                    modulo=modulo, titulo=atividade_titulo, contexto_avaliacao="FORMATIVA", ordem=1, ativo=True,
                )
            criadas.append(trilha)
        call_command("seed_intencoes", verbosity=0)
        yield criadas
        Trilha.objects.filter(id__in=[t.id for t in criadas]).delete()
        Intention.objects.all().delete()


def _intencao(mensagem, trilhas):
    classificacao, _, _ = classificar_mensagem(mensagem, trilhas)
    return classificacao["intencao"]


def _erros(mensagens, esperada, trilhas):
    return [(m, obtida) for m in mensagens if (obtida := _intencao(m, trilhas)) != esperada]


def test_chip_continuar_atividade_abre_proxima_atividade(trilhas):
    erros = _erros(CHIPS_RETOMADA, "PROXIMA_ATIVIDADE", trilhas)
    assert not erros, erros


def test_chip_quero_revisar_modulo_responde_com_conteudo(trilhas):
    erros = _erros(CHIPS_REFORCO, "DUVIDA_CONTEUDO", trilhas)
    assert not erros, erros


@pytest.mark.parametrize("chip,esperada", CHIPS_FIXOS.items())
def test_chips_fixos_acertam_a_intencao(trilhas, chip, esperada):
    assert _intencao(chip, trilhas) == esperada


@pytest.mark.parametrize("modelo,esperada", CHIPS_COM_TRILHA.items())
def test_chips_com_nome_da_trilha_acertam_a_intencao(trilhas, modelo, esperada):
    erros = _erros([modelo.format(titulo=t) for t in TRILHAS], esperada, trilhas)
    assert not erros, erros


def test_todos_os_chips_fixos_do_backend_tem_intencao_esperada():
    chips = set(SUGESTOES_INICIAIS + SUGESTOES_AJUDA + SUGESTOES_NIVELAMENTO + SUGESTOES_FALLBACK + SUGESTOES_JORNADA)
    assert chips <= CHIPS_FIXOS.keys()


@pytest.mark.parametrize("esperada", VARIACOES.keys())
def test_variacoes_do_comando_acertam_ao_menos_90_por_cento(trilhas, esperada):
    mensagens = VARIACOES[esperada]
    erros = _erros(mensagens, esperada, trilhas)
    taxa = 1 - len(erros) / len(mensagens)
    assert taxa >= TAXA_MINIMA_ACERTO, f"{taxa:.0%} de acerto; erros: {erros}"


# Temas fora do catálogo: o pedido precisa chegar a RECOMENDAR_TRILHA para o Coach gerar a trilha com IA.
TEMAS_FORA_DO_CATALOGO = [
    "Quero aprender culinária, por onde começo?",
    "Quero aprender fotografia, por onde começo?",
    "Quero estudar marketing digital, qual trilha faço?",
    "Quero aprender a tocar piano",
]


def test_tema_fora_do_catalogo_pede_recomendacao_de_trilha(trilhas):
    erros = _erros(TEMAS_FORA_DO_CATALOGO, "RECOMENDAR_TRILHA", trilhas)
    assert not erros, erros


def test_pergunta_fora_do_catalogo_sem_pedido_de_aprender_nao_vira_recomendacao(trilhas):
    assert _intencao("Qual a capital da França?", trilhas) != "RECOMENDAR_TRILHA"


def test_seed_remove_exemplos_que_sairam_do_catalogo(trilhas):
    saudacao = Intention.objects.get(code="SAUDACAO")
    saudacao.examples.create(text="Posso continuar de onde parei?", embedding=[0.0] * 384)

    call_command("seed_intencoes", verbosity=0)

    assert not saudacao.examples.filter(text="Posso continuar de onde parei?").exists()
    assert Intention.objects.get(code="PROXIMA_ATIVIDADE").examples.filter(text="Posso continuar de onde parei?").exists()

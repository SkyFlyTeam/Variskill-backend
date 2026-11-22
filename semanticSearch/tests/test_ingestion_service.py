import pytest
from model_bakery import baker

from activityManagement.models import Atividade
from assistantManagement.semantic_cache_service import SemanticCacheService
from questionsManagement.models import Questao
from semanticSearch.models import DuvidaAssimilada, EntradaCorpus
from semanticSearch.service.ingestion_service import DuvidaAssimiladaIngestionService
from semanticSearch.service.sanitizer import TextSanitizer
from semanticSearch.service.vetorizacao import normalizar_duvida
from trackManagement.models import Modulo

RESPOSTA_TUPLA = "Listas são mutáveis (podem ser alteradas) enquanto tuplas são imutáveis após criadas."


def test_sanitizacao_remove_dados_pessoais():
    pergunta_suja = "Olá, meu nome é Maria! Gostaria de saber como usar list comprehension? Meu email é maria@exemplo.com e meu tel é (11) 98765-4321."
    resposta_suja = "Bom dia! Você pode usar [x for x in lista]. Caso tenha dúvidas contate suporte@escola.com ou telefone 11 3333-4444."

    p_limpa, r_limpa = TextSanitizer.preparar_para_corpus(pergunta_suja, resposta_suja)

    # Não deve conter e-mail
    assert "maria@exemplo.com" not in p_limpa
    assert "[EMAIL_REMOVIDO]" in p_limpa
    assert "suporte@escola.com" not in r_limpa
    assert "[EMAIL_REMOVIDO]" in r_limpa

    # Não deve conter telefone
    assert "98765-4321" not in p_limpa
    assert "[TELEFONE_REMOVIDO]" in p_limpa
    assert "3333-4444" not in r_limpa
    assert "[TELEFONE_REMOVIDO]" in r_limpa

    # Introdução pessoal removida
    assert not p_limpa.startswith("Olá")
    assert "meu nome é Maria" not in p_limpa


def test_sanitizacao_preserva_numeros_em_exemplos_de_codigo():
    pergunta = "Oi Vari, pode me ajudar? Como iterar sobre 10000000 de elementos?"
    resposta = "Para processar 10000000 ou 12345678 itens sem estourar memória, use range(10000000)."

    p_limpa, r_limpa = TextSanitizer.preparar_para_corpus(pergunta, resposta)

    assert p_limpa == "Como iterar sobre 10000000 de elementos?"
    assert "10000000" in r_limpa
    assert "12345678" in r_limpa
    assert "[TELEFONE_REMOVIDO]" not in r_limpa


def test_sanitizacao_trunca_pergunta_muito_longa():
    pergunta_longa = "Como funciona a recursao em python com muitas palavras " * 10
    p_limpa, _ = TextSanitizer.preparar_para_corpus(pergunta_longa, "Resposta de teste adequada.", max_chars_pergunta=60)

    assert len(p_limpa) <= 61
    assert p_limpa.endswith("?")


def _vetor_fixo() -> list[float]:
    vetor = [0.0] * 384
    vetor[0] = 1.0
    return vetor


@pytest.fixture
def vetor_fixo(monkeypatch):
    """Faz toda pergunta gerar o mesmo vetor, simulando paráfrases com similaridade 1.0."""
    monkeypatch.setattr(
        "semanticSearch.service.ingestion_service.vetorizar_duvida",
        lambda texto: ("texto normalizado", _vetor_fixo()),
    )


@pytest.mark.django_db
def test_assimilar_duvida_cria_duvida_assimilada_com_vetor_e_nao_toca_na_apostila():
    pergunta = "Como funciona o operador walrus no Python?"
    resposta = "O operador walrus (:=) permite atribuir valores a variáveis como parte de uma expressão maior."

    duvida = DuvidaAssimiladaIngestionService.assimilar_duvida(pergunta=pergunta, resposta=resposta)

    assert duvida is not None
    assert duvida.pergunta_texto == pergunta
    assert duvida.pergunta_normalizada == normalizar_duvida(pergunta)
    assert duvida.resposta_didatica == resposta
    assert duvida.atividade_id is None
    assert duvida.modulo_id is None
    assert len(duvida.embedding) == 384
    assert not EntradaCorpus.objects.exists()


@pytest.mark.django_db
def test_assimilar_duvida_registra_contexto_de_questao_atividade_e_modulo(vetor_fixo):
    modulo = baker.make(Modulo)
    atividade = baker.make(Atividade, modulo=modulo)
    questao = baker.make(Questao, atividade=atividade)

    duvida = DuvidaAssimiladaIngestionService.assimilar_duvida(
        "Qual comando interrompe o loop?", "Use a instrução break para interromper a iteração.",
        questao_id=questao.id, atividade_id=atividade.id, modulo_id=modulo.id,
    )

    assert duvida.questao_id == questao.id
    assert duvida.atividade_id == atividade.id
    assert duvida.modulo_id == modulo.id


@pytest.mark.django_db
def test_mesma_pergunta_em_questoes_diferentes_gera_dicas_separadas(vetor_fixo):
    """A tela de exercício envia sempre a mesma pergunta; cada questão precisa da própria dica."""
    atividade = baker.make(Atividade)
    questao1 = baker.make(Questao, atividade=atividade)
    questao2 = baker.make(Questao, atividade=atividade)

    dica1 = DuvidaAssimiladaIngestionService.assimilar_duvida(
        "Como resolver este exercício?", "Pense em qual instrução encerra a repetição.",
        questao_id=questao1.id, atividade_id=atividade.id,
    )
    dica2 = DuvidaAssimiladaIngestionService.assimilar_duvida(
        "Como resolver este exercício?", "Lembre que listas começam no índice zero.",
        questao_id=questao2.id, atividade_id=atividade.id,
    )

    assert dica1.id != dica2.id
    assert DuvidaAssimilada.objects.count() == 2


@pytest.mark.django_db
def test_assimilar_duvida_remove_dados_pessoais(vetor_fixo):
    duvida = DuvidaAssimiladaIngestionService.assimilar_duvida(
        "Olá, meu nome é Maria! Como usar list comprehension? Meu email é maria@exemplo.com",
        "Use [x for x in lista]. Dúvidas: suporte@escola.com",
    )

    assert "maria@exemplo.com" not in duvida.pergunta_texto
    assert "Maria" not in duvida.pergunta_texto
    assert "suporte@escola.com" not in duvida.resposta_didatica


@pytest.mark.django_db
def test_anti_duplicacao_semantica_acima_095_no_mesmo_escopo(vetor_fixo):
    duvida1 = DuvidaAssimiladaIngestionService.assimilar_duvida(
        "Qual a diferença entre tupla e lista no Python?", RESPOSTA_TUPLA,
    )
    duvida2 = DuvidaAssimiladaIngestionService.assimilar_duvida(
        "Qual é a diferença entre tupla e lista em Python?", RESPOSTA_TUPLA,
    )

    assert duvida1 is not None
    assert duvida1.id == duvida2.id
    assert DuvidaAssimilada.objects.count() == 1


@pytest.mark.django_db
def test_anti_duplicacao_nao_mistura_dica_de_questao_com_duvida_global(vetor_fixo):
    atividade = baker.make(Atividade)
    questao = baker.make(Questao, atividade=atividade)

    global_ = DuvidaAssimiladaIngestionService.assimilar_duvida(
        "Qual a diferença entre tupla e lista?", RESPOSTA_TUPLA,
    )
    da_atividade = DuvidaAssimiladaIngestionService.assimilar_duvida(
        "Qual a diferença entre tupla e lista?", RESPOSTA_TUPLA, questao_id=questao.id, atividade_id=atividade.id,
    )

    assert global_.id != da_atividade.id
    assert DuvidaAssimilada.objects.count() == 2


@pytest.mark.django_db
def test_duvida_mal_avaliada_nao_impede_nova_assimilacao(vetor_fixo, settings):
    settings.DUVIDA_FEEDBACK_MIN_NEGATIVOS = 3
    mal_avaliada = baker.make(
        DuvidaAssimilada, embedding=_vetor_fixo(), feedbacks_negativos=5, feedbacks_positivos=1,
    )

    nova = DuvidaAssimiladaIngestionService.assimilar_duvida(
        "Qual a diferença entre tupla e lista?", RESPOSTA_TUPLA,
    )

    assert nova.id != mal_avaliada.id
    assert DuvidaAssimilada.objects.count() == 2


@pytest.mark.django_db
def test_ignora_duvidas_curtas_ou_sem_conteudo():
    assert DuvidaAssimiladaIngestionService.assimilar_duvida("oi", "ola tudo bem com voce?") is None
    assert DuvidaAssimiladaIngestionService.assimilar_duvida(
        "Oi Vari, como vai você?", "Vou bem e pronto para ajudar nos estudos!",
    ) is None
    assert DuvidaAssimiladaIngestionService.assimilar_duvida("Como usar decorators?", "sim") is None
    assert not DuvidaAssimilada.objects.exists()


@pytest.mark.django_db(transaction=True)
def test_execucao_assincrona_assimila_em_background():
    pergunta = "O que são generators e yield em Python?"
    resposta = "Generators são funções que usam yield para produzir uma sequência de valores sob demanda, economizando memória."

    thread = DuvidaAssimiladaIngestionService.assimilar_duvida_async(pergunta=pergunta, resposta=resposta)
    thread.join(timeout=10.0)

    assert DuvidaAssimilada.objects.filter(pergunta_texto=pergunta).exists()


@pytest.mark.django_db
def test_busca_encontra_duvida_assimilada_pelo_mesmo_pipeline_de_vetorizacao():
    """Ingestão e busca vetorizam igual: saudação e pontuação extras não derrubam a similaridade."""
    duvida = DuvidaAssimiladaIngestionService.assimilar_duvida(
        "Como funciona o operador walrus no Python?",
        "O operador walrus (:=) permite atribuir valores a variáveis como parte de uma expressão maior.",
    )

    resultado = SemanticCacheService.buscar_duvida_semelhante(
        "Olá! Como funciona o operador walrus no Python???", somente_globais=True,
    )

    assert resultado is not None
    assert resultado["duvida_id"] == str(duvida.id)
    assert resultado["similaridade"] == pytest.approx(1.0, abs=1e-4)

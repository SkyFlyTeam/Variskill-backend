import pytest
import time
from semanticSearch.models import EntradaCorpus, PerguntaCorpus
from semanticSearch.service.sanitizer import TextSanitizer
from semanticSearch.service.ingestion_service import CorpusIngestionService


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


@pytest.mark.django_db
def test_assimilar_duvida_cria_entrada_e_pergunta_corpus_com_vetor():
    pergunta = "Como funciona o operador walrus no Python?"
    resposta = "O operador walrus (:=) permite atribuir valores a variáveis como parte de uma expressão maior."
    topico = "Sintaxe Python"

    entrada = CorpusIngestionService.assimilar_duvida(
        pergunta=pergunta,
        resposta=resposta,
        topico=topico,
    )

    assert entrada is not None
    assert entrada.topico == "Sintaxe Python"
    assert entrada.pergunta == pergunta
    assert entrada.resposta == resposta
    assert entrada.ativo is True

    # Verifica se PerguntaCorpus foi criada com vetor
    pergunta_corpus = PerguntaCorpus.objects.filter(entrada=entrada).first()
    assert pergunta_corpus is not None
    assert pergunta_corpus.texto == pergunta
    assert len(pergunta_corpus.embedding) == 384


@pytest.mark.django_db
def test_idempotencia_nao_duplica_pergunta_identica():
    pergunta = "Qual a diferença entre tupla e lista em Python?"
    resposta = "Listas são mutáveis (podem ser alteradas) enquanto tuplas são imutáveis após criadas."

    entrada1 = CorpusIngestionService.assimilar_duvida(pergunta, resposta, "Tipos de Dados")
    entrada2 = CorpusIngestionService.assimilar_duvida(pergunta, resposta, "Tipos de Dados")

    assert entrada1 is not None
    assert entrada2 is not None
    assert entrada1.id == entrada2.id

    # Garante que não criou registros duplicados
    assert EntradaCorpus.objects.filter(pergunta=pergunta).count() == 1
    assert PerguntaCorpus.objects.filter(entrada=entrada1).count() == 1


@pytest.mark.django_db
def test_anti_duplicacao_semantica_acima_095_nao_duplica_registro(monkeypatch):
    vetor_fixo = [0.0] * 384
    vetor_fixo[0] = 1.0
    monkeypatch.setattr(
        "semanticSearch.service.ingestion_service.TextEmbeddingService.gerar_embedding",
        lambda self, texto: vetor_fixo,
    )

    resposta = "Listas são mutáveis (podem ser alteradas) enquanto tuplas são imutáveis após criadas."
    entrada1 = CorpusIngestionService.assimilar_duvida(
        "Qual a diferença entre tupla e lista no Python?", resposta, "Tipos de Dados"
    )
    entrada2 = CorpusIngestionService.assimilar_duvida(
        "Qual é a diferença entre tupla e lista em Python?", resposta, "Tipos de Dados"
    )

    assert entrada1 is not None
    assert entrada2 is not None
    assert entrada1.id == entrada2.id
    assert EntradaCorpus.objects.filter(topico="Tipos de Dados").count() == 1


@pytest.mark.django_db
def test_ignora_duvidas_curtas_ou_sem_conteudo():
    entrada_curta = CorpusIngestionService.assimilar_duvida("oi", "ola tudo bem com voce?")
    assert entrada_curta is None

    entrada_operacional = CorpusIngestionService.assimilar_duvida("Oi Vari, como vai você?", "Vou bem e pronto para ajudar nos estudos!")
    assert entrada_operacional is None

    entrada_resposta_curta = CorpusIngestionService.assimilar_duvida("Como usar decorators?", "sim")
    assert entrada_resposta_curta is None


@pytest.mark.django_db(transaction=True)
def test_execucao_assincrona_assimila_em_background():
    pergunta = "O que são generators e yield em Python?"
    resposta = "Generators são funções que usam yield para produzir uma sequência de valores sob demanda, economizando memória."

    thread = CorpusIngestionService.assimilar_duvida_async(
        pergunta=pergunta,
        resposta=resposta,
        topico="Funções Avançadas",
    )

    thread.join(timeout=10.0)

    # Verifica persistência no banco
    entrada = EntradaCorpus.objects.filter(pergunta=pergunta).first()
    assert entrada is not None
    assert entrada.topico == "Funções Avançadas"
    assert PerguntaCorpus.objects.filter(entrada=entrada).exists()

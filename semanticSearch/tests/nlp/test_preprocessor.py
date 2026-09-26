import pytest
import re

from semanticSearch.service.nlp import preprocessor


class FakeToken:
    def __init__(self, text, lemma=None, *, punct=False, space=False, digit=False):
        self.text = text
        self.lower_ = text.lower()
        self.lemma_ = lemma or text
        self.is_punct = punct
        self.is_space = space
        self.is_digit = digit


class FakeNlp:
    lemmas = {
        "quais": "qual",
        "trilhas": "trilha",
        "estao": "estar",
        "disponiveis": "disponivel",
        "quero": "querer",
        "ajuda": "ajuda",
        "nao": "nao",
    }

    def __call__(self, text):
        values = re.findall(r"\w+|[^\w\s]", text)
        return [
            FakeToken(
                value,
                self.lemmas.get(value, value),
                punct=value in {"?", "!", "."},
                digit=value.isdigit(),
            )
            for value in values
        ]


@pytest.fixture
def preprocessor_instance(monkeypatch):
    fake_nlp = FakeNlp()
    monkeypatch.setattr(preprocessor.spacy, "load", lambda *args, **kwargs: fake_nlp)
    monkeypatch.setattr(preprocessor, "stopwords", type("FakeStopwords", (), {"words": staticmethod(lambda language: ["a", "de", "estao", "pra", "mim", "eu"])})())
    return preprocessor.TextPreprocessor()


@pytest.mark.unit
def test_processar_frase_comum(preprocessor_instance):
    result = preprocessor_instance.processar("Quais trilhas estão disponíveis pra mim?")

    assert result == "qual trilha disponivel"


@pytest.mark.unit
def test_processar_preserva_negacao(preprocessor_instance):
    result = preprocessor_instance.processar("Eu não quero ajuda")

    assert result == "nao querer ajuda"


@pytest.mark.unit
@pytest.mark.parametrize("texto", [None, "", "   ", "?!."])
def test_processar_entradas_sem_conteudo_retorna_string_vazia(preprocessor_instance, texto):
    assert preprocessor_instance.processar(texto) == ""


@pytest.mark.unit
def test_processar_frase_apenas_com_stopwords(preprocessor_instance):
    assert preprocessor_instance.processar("a de pra mim") == ""

@pytest.mark.unit
def test_tokenizar_separa_palavras_e_pontuacao(preprocessor_instance):
    tokens = preprocessor_instance._tokenizar("Quais trilhas?")
    assert [token.text for token in tokens] == ["Quais", "trilhas", "?"]


@pytest.mark.unit
def test_lematizar_retorna_formas_canonicas(preprocessor_instance):
    tokens = ["quais", "trilhas", "disponiveis", "quero"]
    assert preprocessor_instance._lematizar(tokens) == ["qual", "trilha", "disponivel", "querer"]

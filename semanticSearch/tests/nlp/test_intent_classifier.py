import pytest
from model_bakery import baker

from intents.models import Intention, IntentionExample, Response
from semanticSearch.service.nlp.intent_classifier import FALLBACK_TEXT, IntentClassifier


pytestmark = pytest.mark.django_db


def test_classifies_intention_and_interpolates_response():
    intention = baker.make(Intention, code="LISTAR_TRILHAS")
    baker.make(IntentionExample, intention=intention, embedding=[1.0] + [0.0] * 383)
    baker.make(Response, intention=intention, text="Olá, {nome}! Aqui estão suas trilhas.")

    result = IntentClassifier().classificar([1.0] + [0.0] * 383, {"nome": "Ana"})

    assert result["intencao"] == "LISTAR_TRILHAS"
    assert result["similaridade"] == pytest.approx(1.0)
    assert result["resposta_texto"] == "Olá, Ana! Aqui estão suas trilhas."


def test_returns_fallback_for_low_similarity():
    intention = baker.make(Intention)
    baker.make(IntentionExample, intention=intention, embedding=[1.0] + [0.0] * 383)

    result = IntentClassifier(similarity_threshold=0.70).classificar([0.0, 1.0] + [0.0] * 382)

    assert result["intencao"] == "FALLBACK"
    assert result["resposta_texto"] == FALLBACK_TEXT
    assert result["similaridade"] < 0.70


def test_returns_fallback_when_database_has_no_intentions():
    result = IntentClassifier().classificar([1.0] + [0.0] * 383)

    assert result == {
        "intencao": "FALLBACK",
        "similaridade": 0.0,
        "resposta_texto": FALLBACK_TEXT,
        "dados_extras": {},
    }

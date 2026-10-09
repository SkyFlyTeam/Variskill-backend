import os
import urllib.error
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from learning import hint_service
from learning.hint_service import HintService

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def reset_breaker():
    hint_service.AI_CIRCUIT_BREAKER.reset()
    yield
    hint_service.AI_CIRCUIT_BREAKER.reset()


def _questao_fake():
    return SimpleNamespace(enunciado="Enunciado", codigo_snippet="")


def test_timeout_em_no_maximo_3_segundos():
    assert hint_service.TIMEOUT_SECONDS <= 3


@patch.dict(os.environ, {"OPENAI_API_KEY": "fake-key"})
def test_http_429_retorna_none():
    erro = urllib.error.HTTPError("http://x", 429, "Too Many Requests", {}, None)
    with patch("urllib.request.urlopen", side_effect=erro):
        assert HintService._call_external_ai(_questao_fake(), "duvida") is None


@patch.dict(os.environ, {"OPENAI_API_KEY": "fake-key"})
def test_falha_de_rede_retorna_none():
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("sem rede")):
        assert HintService._call_external_ai(_questao_fake(), "duvida") is None


@patch.dict(os.environ, {"OPENAI_API_KEY": "fake-key"})
def test_timeout_retorna_none():
    with patch("urllib.request.urlopen", side_effect=TimeoutError("timeout")):
        assert HintService._call_external_ai(_questao_fake(), "duvida") is None


@patch.dict(os.environ, {"OPENAI_API_KEY": "fake-key"})
def test_breaker_aberto_nao_chama_a_rede():
    for _ in range(3):
        hint_service.AI_CIRCUIT_BREAKER.record_failure()
    with patch("urllib.request.urlopen") as mock_urlopen:
        assert HintService._call_external_ai(_questao_fake(), "duvida") is None
    mock_urlopen.assert_not_called()

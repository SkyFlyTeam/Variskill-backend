import json
import os
import urllib.error
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

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


def _resposta_http(conteudo: str):
    resposta = MagicMock(status=200)
    resposta.read.return_value = json.dumps({"choices": [{"message": {"content": conteudo}}]}).encode("utf-8")
    resposta.__enter__.return_value = resposta
    return resposta


@patch.dict(os.environ, {"OPENAI_API_KEY": "fake-key"})
def test_json_usa_structured_outputs_e_timeout_proprio():
    schema = {"type": "object", "properties": {}, "required": [], "additionalProperties": False}
    with patch("urllib.request.urlopen", return_value=_resposta_http('{"tema": "culinaria"}')) as mock_urlopen:
        resposta = HintService.call_external_ai_json("prompt", "pedido", timeout=60, schema=schema, nome_schema="teste")
    assert resposta == {"tema": "culinaria"}
    requisicao = mock_urlopen.call_args.args[0]
    assert json.loads(requisicao.data)["response_format"] == {
        "type": "json_schema", "json_schema": {"name": "teste", "strict": True, "schema": schema},
    }
    assert mock_urlopen.call_args.kwargs["timeout"] == 60


@patch.dict(os.environ, {"OPENAI_API_KEY": "fake-key"})
def test_json_invalido_retorna_none():
    with patch("urllib.request.urlopen", return_value=_resposta_http("não é json")):
        assert HintService.call_external_ai_json("prompt", "pedido", timeout=60, schema={}, nome_schema="teste") is None

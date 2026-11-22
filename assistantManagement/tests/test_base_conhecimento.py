import math
from unittest.mock import patch

import pytest
from model_bakery import baker

from activityManagement.models import Atividade
from questionsManagement.models import Questao
from assistantManagement.base_conhecimento import (
    ORIGEM_APOSTILA,
    ORIGEM_CACHE_SEMANTICO,
    BaseConhecimento,
)
from semanticSearch.models import DuvidaAssimilada, EntradaCorpus, PerguntaCorpus

pytestmark = [pytest.mark.integration, pytest.mark.django_db]

DIMENSOES = 384


def _vetor_base() -> list[float]:
    vetor = [0.0] * DIMENSOES
    vetor[0] = 1.0
    return vetor


def _vetor_com_similaridade(similaridade: float) -> list[float]:
    vetor = [0.0] * DIMENSOES
    vetor[0] = similaridade
    vetor[1] = math.sqrt(max(0.0, 1.0 - similaridade ** 2))
    return vetor


def _criar_entrada_apostila(similaridade: float, resposta: str = "Resposta da apostila.") -> EntradaCorpus:
    entrada = EntradaCorpus.objects.create(topico="Python", pergunta=f"Pergunta {similaridade}", resposta=resposta)
    PerguntaCorpus.objects.create(entrada=entrada, texto=entrada.pergunta, embedding=_vetor_com_similaridade(similaridade))
    return entrada


def test_apostila_tem_prioridade_sobre_o_caderno():
    entrada = _criar_entrada_apostila(0.9)
    duvida = baker.make(DuvidaAssimilada, embedding=_vetor_com_similaridade(1.0), contador_utilizacoes=1)

    resultado = BaseConhecimento.buscar(_vetor_base())

    assert resultado.resposta.origem == ORIGEM_APOSTILA
    assert resultado.resposta.entrada_corpus == entrada
    assert resultado.resposta.duvida_assimilada_id is None
    duvida.refresh_from_db()
    assert duvida.contador_utilizacoes == 1


def test_consulta_o_caderno_quando_a_apostila_nao_responde():
    _criar_entrada_apostila(0.5)
    duvida = baker.make(
        DuvidaAssimilada, embedding=_vetor_com_similaridade(0.95), resposta_didatica="Resposta assimilada.",
    )

    resultado = BaseConhecimento.buscar(_vetor_base())

    assert resultado.resposta.origem == ORIGEM_CACHE_SEMANTICO
    assert resultado.resposta.texto == "Resposta assimilada."
    assert resultado.resposta.duvida_assimilada_id == str(duvida.pk)
    assert resultado.resposta.entrada_corpus is None


def test_sem_resposta_local_retorna_relacionadas_da_apostila():
    relacionada = _criar_entrada_apostila(0.7)

    resultado = BaseConhecimento.buscar(_vetor_base())

    assert resultado.resposta is None
    assert resultado.relacionadas == [relacionada]


def test_duvida_conceitual_nao_recebe_dica_de_atividade():
    atividade = baker.make(Atividade)
    baker.make(DuvidaAssimilada, atividade=atividade, embedding=_vetor_com_similaridade(1.0))

    assert BaseConhecimento.buscar(_vetor_base()).resposta is None


def test_dica_so_usa_dicas_da_propria_questao():
    atividade = baker.make(Atividade)
    questao = baker.make(Questao, atividade=atividade)
    outra_questao_mesma_atividade = baker.make(Questao, atividade=atividade)
    baker.make(
        DuvidaAssimilada, questao=outra_questao_mesma_atividade, atividade=atividade,
        embedding=_vetor_com_similaridade(1.0),
    )
    baker.make(DuvidaAssimilada, atividade=None, embedding=_vetor_com_similaridade(1.0))
    da_questao = baker.make(
        DuvidaAssimilada, questao=questao, atividade=atividade, embedding=_vetor_com_similaridade(0.9),
    )

    resultado = BaseConhecimento.buscar(_vetor_base(), questao_id=questao.id)

    assert resultado.resposta.duvida_assimilada_id == str(da_questao.pk)


def test_buscar_por_texto_nao_vetoriza_quando_a_base_esta_vazia():
    with patch("assistantManagement.base_conhecimento.vetorizar_duvida") as mock_vetorizar:
        resultado = BaseConhecimento.buscar_por_texto("como funciona o for?")

    assert resultado.resposta is None
    mock_vetorizar.assert_not_called()


def test_buscar_por_texto_vetoriza_e_consulta_o_caderno():
    duvida = baker.make(DuvidaAssimilada, embedding=_vetor_com_similaridade(1.0))

    with patch(
        "assistantManagement.base_conhecimento.vetorizar_duvida",
        return_value=("como funcionar for", _vetor_base()),
    ):
        resultado = BaseConhecimento.buscar_por_texto("como funciona o for?")

    assert resultado.resposta.duvida_assimilada_id == str(duvida.pk)


def test_assimilar_async_delega_para_ingestao_do_caderno():
    with patch(
        "assistantManagement.base_conhecimento.DuvidaAssimiladaIngestionService.assimilar_duvida_async",
    ) as mock_ingestao:
        BaseConhecimento.assimilar_async("pergunta", "resposta", questao_id="q", atividade_id="a", modulo_id="m")

    mock_ingestao.assert_called_once_with(
        pergunta="pergunta", resposta="resposta", questao_id="q", atividade_id="a", modulo_id="m",
    )

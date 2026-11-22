import time
from unittest.mock import MagicMock, patch

import pytest
from model_bakery import baker

from activityManagement.models import Atividade
from assistantManagement.semantic_cache_service import SemanticCacheService
from questionsManagement.models import Questao
from semanticSearch.models import DuvidaAssimilada
from trackManagement.models import Modulo

pytestmark = [pytest.mark.integration, pytest.mark.django_db]

DIMENSOES = 384


def _vetor_base() -> list[float]:
    """Vetor unitário usado como embedding "canônico" da pergunta nos testes."""
    vetor = [0.0] * DIMENSOES
    vetor[0] = 1.0
    return vetor


def _vetor_com_similaridade(similaridade: float) -> list[float]:
    """Vetor unitário cuja similaridade de cosseno com `_vetor_base()` é exatamente `similaridade`."""
    import math

    vetor = [0.0] * DIMENSOES
    vetor[0] = similaridade
    vetor[1] = math.sqrt(max(0.0, 1.0 - similaridade ** 2))
    return vetor


@pytest.fixture(autouse=True)
def embedding_service_mock():
    mock_service = MagicMock()
    mock_service.gerar_embedding.return_value = _vetor_base()
    mock_preprocessor = MagicMock()
    mock_preprocessor.processar.side_effect = lambda texto: texto.lower()
    with patch(
        'assistantManagement.semantic_cache_service.EmbeddingService.get_instance',
        return_value=mock_service,
    ), patch(
        'semanticSearch.service.vetorizacao.TextPreprocessor.get_instance',
        return_value=mock_preprocessor,
    ):
        yield mock_service


def test_retorna_none_quando_pergunta_normalizada_fica_vazia():
    assert SemanticCacheService.buscar_duvida_semelhante('???') is None
    assert SemanticCacheService.buscar_duvida_semelhante('') is None
    assert SemanticCacheService.buscar_duvida_semelhante(None) is None


def test_retorna_none_quando_nao_ha_duvidas_assimiladas():
    assert SemanticCacheService.buscar_duvida_semelhante('como funciona o GIL?') is None


def test_encontra_duvida_identica_e_incrementa_contador():
    duvida = baker.make(
        DuvidaAssimilada,
        resposta_didatica='O GIL é um mutex que protege o interpretador CPython.',
        embedding=_vetor_com_similaridade(1.0),
        contador_utilizacoes=1,
    )

    resultado = SemanticCacheService.buscar_duvida_semelhante('como funciona o GIL?')

    assert resultado == {
        'duvida_id': str(duvida.pk),
        'resposta_didatica': 'O GIL é um mutex que protege o interpretador CPython.',
        'similaridade': pytest.approx(1.0),
    }
    duvida.refresh_from_db()
    assert duvida.contador_utilizacoes == 2


def test_retorna_resposta_correta_para_parafrase_da_mesma_duvida():
    # Paráfrase: embedding próximo (0.9), mas não idêntico, ao da pergunta original.
    duvida = baker.make(
        DuvidaAssimilada,
        resposta_didatica='Explicação sobre o GIL.',
        embedding=_vetor_com_similaridade(0.9),
    )

    resultado = SemanticCacheService.buscar_duvida_semelhante('e esse tal de GIL, como que é?')

    assert resultado['duvida_id'] == str(duvida.pk)
    assert resultado['similaridade'] == pytest.approx(0.9)


def test_ignora_resultado_com_similaridade_abaixo_do_threshold_padrao():
    baker.make(DuvidaAssimilada, embedding=_vetor_com_similaridade(0.80))

    resultado = SemanticCacheService.buscar_duvida_semelhante('pergunta qualquer')

    assert resultado is None


def test_respeita_piso_minimo_de_similaridade_mesmo_com_threshold_menor_informado():
    # similaridade 0.65 < SIMILARITY_FLOOR (0.70): nunca deve ser considerado match,
    # mesmo que o chamador peça um threshold mais permissivo.
    baker.make(DuvidaAssimilada, embedding=_vetor_com_similaridade(0.65))

    resultado = SemanticCacheService.buscar_duvida_semelhante('pergunta qualquer', threshold=0.5)

    assert resultado is None


def test_aceita_threshold_customizado_acima_do_piso():
    duvida = baker.make(DuvidaAssimilada, embedding=_vetor_com_similaridade(0.75))

    resultado = SemanticCacheService.buscar_duvida_semelhante('pergunta qualquer', threshold=0.70)

    assert resultado is not None
    assert resultado['duvida_id'] == str(duvida.pk)


def test_filtra_por_atividade_id_quando_informado():
    atividade_certa = baker.make(Atividade)
    atividade_errada = baker.make(Atividade)
    baker.make(
        DuvidaAssimilada, atividade=atividade_errada, embedding=_vetor_com_similaridade(1.0),
        resposta_didatica='resposta da atividade errada',
    )
    duvida_certa = baker.make(
        DuvidaAssimilada, atividade=atividade_certa, embedding=_vetor_com_similaridade(0.95),
        resposta_didatica='resposta da atividade certa',
    )

    resultado = SemanticCacheService.buscar_duvida_semelhante(
        'pergunta qualquer', atividade_id=atividade_certa.pk,
    )

    assert resultado['duvida_id'] == str(duvida_certa.pk)
    assert resultado['resposta_didatica'] == 'resposta da atividade certa'


def test_filtra_por_modulo_id_quando_atividade_id_nao_informado():
    modulo_certo = baker.make(Modulo)
    modulo_errado = baker.make(Modulo)
    baker.make(
        DuvidaAssimilada, modulo=modulo_errado, embedding=_vetor_com_similaridade(1.0),
    )
    duvida_certa = baker.make(
        DuvidaAssimilada, modulo=modulo_certo, embedding=_vetor_com_similaridade(0.95),
    )

    resultado = SemanticCacheService.buscar_duvida_semelhante(
        'pergunta qualquer', modulo_id=modulo_certo.pk,
    )

    assert resultado['duvida_id'] == str(duvida_certa.pk)


def test_busca_vetorial_responde_em_menos_de_100ms():
    for _ in range(20):
        baker.make(DuvidaAssimilada, embedding=_vetor_com_similaridade(0.5))
    baker.make(DuvidaAssimilada, embedding=_vetor_com_similaridade(0.99))

    inicio = time.perf_counter()
    resultado = SemanticCacheService.buscar_duvida_semelhante('pergunta qualquer')
    duracao_ms = (time.perf_counter() - inicio) * 1000

    assert resultado is not None
    assert duracao_ms < 100


def test_usa_vetor_informado_sem_gerar_embedding(embedding_service_mock):
    duvida = baker.make(DuvidaAssimilada, embedding=_vetor_com_similaridade(1.0))

    resultado = SemanticCacheService.buscar_duvida_semelhante(vetor=_vetor_base())

    assert resultado['duvida_id'] == str(duvida.pk)
    embedding_service_mock.gerar_embedding.assert_not_called()


def test_somente_globais_ignora_dicas_de_atividades():
    atividade = baker.make(Atividade)
    baker.make(DuvidaAssimilada, atividade=atividade, embedding=_vetor_com_similaridade(1.0))
    global_ = baker.make(DuvidaAssimilada, atividade=None, embedding=_vetor_com_similaridade(0.9))

    resultado = SemanticCacheService.buscar_duvida_semelhante(vetor=_vetor_base(), somente_globais=True)

    assert resultado['duvida_id'] == str(global_.pk)


def test_threshold_padrao_vem_das_settings(settings):
    settings.SEMANTIC_CACHE_THRESHOLD = 0.95
    baker.make(DuvidaAssimilada, embedding=_vetor_com_similaridade(0.9))

    assert SemanticCacheService.buscar_duvida_semelhante(vetor=_vetor_base()) is None


def test_ignora_duvida_mal_avaliada_e_serve_a_proxima(settings):
    settings.DUVIDA_FEEDBACK_MIN_NEGATIVOS = 3
    mal_avaliada = baker.make(
        DuvidaAssimilada, embedding=_vetor_com_similaridade(1.0),
        feedbacks_negativos=3, feedbacks_positivos=1, contador_utilizacoes=1,
    )
    boa = baker.make(DuvidaAssimilada, embedding=_vetor_com_similaridade(0.9))

    resultado = SemanticCacheService.buscar_duvida_semelhante(vetor=_vetor_base())

    assert resultado['duvida_id'] == str(boa.pk)
    mal_avaliada.refresh_from_db()
    assert mal_avaliada.contador_utilizacoes == 1


@pytest.mark.parametrize('negativos, positivos', [(2, 0), (3, 3), (4, 10)])
def test_mantem_duvida_com_poucos_negativos_ou_maioria_positiva(settings, negativos, positivos):
    settings.DUVIDA_FEEDBACK_MIN_NEGATIVOS = 3
    duvida = baker.make(
        DuvidaAssimilada, embedding=_vetor_com_similaridade(1.0),
        feedbacks_negativos=negativos, feedbacks_positivos=positivos,
    )

    resultado = SemanticCacheService.buscar_duvida_semelhante(vetor=_vetor_base())

    assert resultado['duvida_id'] == str(duvida.pk)


def test_filtra_por_questao_id_antes_da_atividade():
    atividade = baker.make(Atividade)
    questao = baker.make(Questao, atividade=atividade)
    outra_questao = baker.make(Questao, atividade=atividade)
    baker.make(DuvidaAssimilada, questao=outra_questao, atividade=atividade, embedding=_vetor_com_similaridade(1.0))
    da_questao = baker.make(
        DuvidaAssimilada, questao=questao, atividade=atividade, embedding=_vetor_com_similaridade(0.9),
    )

    resultado = SemanticCacheService.buscar_duvida_semelhante(
        vetor=_vetor_base(), questao_id=questao.id, atividade_id=atividade.id,
    )

    assert resultado['duvida_id'] == str(da_questao.pk)

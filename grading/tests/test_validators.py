from types import SimpleNamespace

import pytest

from grading.validators import (
    BlockOrderValidator,
    FillBlankValidator,
    MultipleChoiceValidator,
    ResponseValidatorContext,
)


pytestmark = pytest.mark.unit


def questao(**kwargs):
    return SimpleNamespace(**kwargs)


class TestMultipleChoiceValidator:
    def test_valida_alternativa_correta(self):
        q = questao(gabarito_esperado='A')

        assert MultipleChoiceValidator().validar(q, {'opcao_selecionada': 'A'}) is True

    def test_reprova_alternativa_incorreta(self):
        q = questao(gabarito_esperado='A')

        assert MultipleChoiceValidator().validar(q, {'opcao_selecionada': 'B'}) is False

    def test_reprova_payload_sem_opcao_selecionada(self):
        q = questao(gabarito_esperado='A')

        assert MultipleChoiceValidator().validar(q, {}) is False


class TestFillBlankValidator:
    def test_valida_resposta_exata(self):
        q = questao(gabarito_esperado='int')

        assert FillBlankValidator().validar(q, {'valor_preenchido': 'int'}) is True

    @pytest.mark.parametrize('valor_preenchido', ['int', ' int ', 'INT', ' InT'])
    def test_sanitiza_espacos_e_caixa_antes_de_comparar(self, valor_preenchido):
        q = questao(gabarito_esperado='int')

        assert FillBlankValidator().validar(q, {'valor_preenchido': valor_preenchido}) is True

    def test_aceita_qualquer_valor_da_lista_de_gabarito(self):
        q = questao(gabarito_esperado='int, integer')

        assert FillBlankValidator().validar(q, {'valor_preenchido': 'integer'}) is True

    def test_reprova_valor_fora_do_gabarito(self):
        q = questao(gabarito_esperado='int')

        assert FillBlankValidator().validar(q, {'valor_preenchido': 'string'}) is False

    def test_reprova_payload_sem_valor_preenchido(self):
        q = questao(gabarito_esperado='int')

        assert FillBlankValidator().validar(q, {}) is False


class TestBlockOrderValidator:
    def test_valida_ordem_correta(self):
        q = questao(gabarito_esperado='id1,id2,id3')

        assert BlockOrderValidator().validar(q, {'ordem_enviada': ['id1', 'id2', 'id3']}) is True

    def test_reprova_ordem_incorreta(self):
        q = questao(gabarito_esperado='id1,id2,id3')

        assert BlockOrderValidator().validar(q, {'ordem_enviada': ['id2', 'id1', 'id3']}) is False

    def test_reprova_quantidade_diferente_de_blocos(self):
        q = questao(gabarito_esperado='id1,id2,id3')

        assert BlockOrderValidator().validar(q, {'ordem_enviada': ['id1', 'id2']}) is False

    def test_reprova_payload_sem_ordem_enviada(self):
        q = questao(gabarito_esperado='id1,id2,id3')

        assert BlockOrderValidator().validar(q, {}) is False


class TestResponseValidatorContext:
    @pytest.mark.parametrize('tipo_exercicio, strategy_class', [
        ('MULTIPLA_ESCOLHA', MultipleChoiceValidator),
        ('COMPLETE_CODIGO', FillBlankValidator),
        ('ORDENAR_BLOCOS', BlockOrderValidator),
    ])
    def test_seleciona_strategy_pelo_tipo_de_exercicio(self, tipo_exercicio, strategy_class):
        context = ResponseValidatorContext.for_questao(questao(tipo_exercicio=tipo_exercicio))

        assert isinstance(context.estrategia, strategy_class)

    def test_rejeita_tipo_de_exercicio_desconhecido(self):
        with pytest.raises(ValueError):
            ResponseValidatorContext.for_questao(questao(tipo_exercicio='INEXISTENTE'))

    def test_delega_validacao_para_a_strategy_escolhida(self):
        q = questao(tipo_exercicio='MULTIPLA_ESCOLHA', gabarito_esperado='A')
        context = ResponseValidatorContext.for_questao(q)

        assert context.validar(q, {'opcao_selecionada': 'A'}) is True
        assert context.validar(q, {'opcao_selecionada': 'B'}) is False

    def test_aceita_strategy_injetada_diretamente(self):
        q = questao(gabarito_esperado='A')
        context = ResponseValidatorContext(MultipleChoiceValidator())

        assert context.validar(q, {'opcao_selecionada': 'A'}) is True

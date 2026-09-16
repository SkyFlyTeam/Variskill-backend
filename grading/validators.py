from abc import ABC, abstractmethod
from typing import Protocol


class RespondableQuestion(Protocol):
    """Qualquer objeto com esses dois atributos serve — sem depender do model Question."""

    tipo_exercicio: str
    gabarito_esperado: str


class ResponseValidator(ABC):
    @abstractmethod
    def validar(self, questao: RespondableQuestion, resposta: dict) -> bool:
        """Valida a resposta submetida contra o gabarito da questão.

        - Entrada: `resposta` no formato do payload do Front-End
          (ex: {"opcao_selecionada": "A"} | {"valor_preenchido": "int"} | {"ordem_enviada": [...]})
        - Saída: bool determinístico (True = correta)
        """


class MultipleChoiceValidator(ResponseValidator):
    def validar(self, questao: RespondableQuestion, resposta: dict) -> bool:
        return resposta.get('opcao_selecionada') == questao.gabarito_esperado


class FillBlankValidator(ResponseValidator):
    def validar(self, questao: RespondableQuestion, resposta: dict) -> bool:
        valor_preenchido = resposta.get('valor_preenchido') or ''
        respostas_aceitas = {
            valor.strip().lower()
            for valor in questao.gabarito_esperado.split(',')
        }
        return valor_preenchido.strip().lower() in respostas_aceitas


class BlockOrderValidator(ResponseValidator):
    def validar(self, questao: RespondableQuestion, resposta: dict) -> bool:
        ordem_enviada = [str(bloco_id).strip() for bloco_id in resposta.get('ordem_enviada') or []]
        ordem_correta = [bloco_id.strip() for bloco_id in questao.gabarito_esperado.split(',')]
        return ordem_enviada == ordem_correta


class ResponseValidatorContext:
    _STRATEGIES_POR_TIPO_EXERCICIO: dict[str, type[ResponseValidator]] = {
        'MULTIPLA_ESCOLHA': MultipleChoiceValidator,
        'COMPLETE_CODIGO': FillBlankValidator,
        'ORDENAR_BLOCOS': BlockOrderValidator,
    }

    def __init__(self, estrategia: ResponseValidator):
        self.estrategia = estrategia

    @classmethod
    def for_questao(cls, questao: RespondableQuestion) -> 'ResponseValidatorContext':
        """Seleciona a estratégia adequada a partir de questao.tipo_exercicio."""
        try:
            strategy_class = cls._STRATEGIES_POR_TIPO_EXERCICIO[questao.tipo_exercicio]
        except KeyError:
            raise ValueError(f'Tipo de exercício sem strategy de validação: {questao.tipo_exercicio!r}')
        return cls(strategy_class())

    def validar(self, questao: RespondableQuestion, resposta: dict) -> bool:
        return self.estrategia.validar(questao, resposta)

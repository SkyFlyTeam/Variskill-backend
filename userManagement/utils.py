"""Utilitários de dados pessoais usados nos fluxos de LGPD.

Centraliza a normalização/validação de CPF e a mensagem única de bloqueio de
menores, para que backend e frontend usem o mesmo comportamento.
"""

import re

# Mensagem única usada pelo backend e pelo frontend quando um menor tenta se
# cadastrar sem os dados do responsável legal.
MENSAGEM_MENOR_SEM_RESPONSAVEL = (
    'Menores de idade precisam de permissão do responsável para utilizar '
    'nossos serviços.'
)


def apenas_digitos(valor: str) -> str:
    """Remove tudo que não for dígito (máscaras de CPF, espaços etc.)."""
    return re.sub(r'\D', '', valor or '')


def validar_cpf(cpf: str) -> bool:
    """Valida um CPF pelos dígitos verificadores (aceita com ou sem máscara)."""
    digitos = apenas_digitos(cpf)

    if len(digitos) != 11:
        return False

    # Sequências repetidas (000.000.000-00, 111...) passam no cálculo, mas não
    # são CPFs válidos.
    if digitos == digitos[0] * 11:
        return False

    for tamanho in (9, 10):
        soma = sum(
            int(digitos[indice]) * (tamanho + 1 - indice)
            for indice in range(tamanho)
        )
        resto = (soma * 10) % 11
        if resto == 10:
            resto = 0
        if resto != int(digitos[tamanho]):
            return False

    return True


def formatar_cpf(cpf: str) -> str:
    """Devolve o CPF no formato 000.000.000-00; texto inválido volta como veio."""
    digitos = apenas_digitos(cpf)
    if len(digitos) != 11:
        return cpf or ''
    return f'{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}'


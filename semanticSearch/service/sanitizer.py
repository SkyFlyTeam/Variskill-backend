import re
from typing import Tuple


class TextSanitizer:
    """
    Higienizador de texto para conformidade com LGPD antes de persistir dúvidas no corpora.
    Remove identificadores pessoais (PII) como e-mails, números de telefone, CPFs e padrões nominais.
    """

    # Regex para e-mails comuns
    _EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

    # Regex para telefones (com ou sem DDD, fixo ou celular no padrão BR)
    _PHONE_REGEX = re.compile(
        r"(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?(?:9\d{4}|\d{4})[-\s]?\d{4}"
    )

    # Regex para CPF (comum com pontuação ou sequência de 11 dígitos)
    _CPF_REGEX = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")

    # Regex para saudações e apresentações pessoais iniciais (ex.: "Olá, meu nome é João e...")
    _INTRO_REGEX = re.compile(
        r"^(?:ol[aá]|oi|bom dia|boa tarde|boa noite|meu nome [eé]|eu sou o|eu sou a)\b[^.?!,;]*[,.:;!\s]*",
        re.IGNORECASE,
    )

    @classmethod
    def sanitizar(cls, texto: str) -> str:
        """
        Higieniza o texto removendo PII e normalizando espaçamentos.
        """
        if not texto or not isinstance(texto, str):
            return ""

        texto_limpo = texto.strip()

        # 1. Remover introduções e saudações pessoais
        texto_limpo = cls._INTRO_REGEX.sub("", texto_limpo).strip()

        # 2. Mascarar/Remover e-mails
        texto_limpo = cls._EMAIL_REGEX.sub("[EMAIL_REMOVIDO]", texto_limpo)

        # 3. Mascarar CPFs
        texto_limpo = cls._CPF_REGEX.sub("[CPF_REMOVIDO]", texto_limpo)

        # 4. Mascarar números de telefone
        texto_limpo = cls._PHONE_REGEX.sub("[TELEFONE_REMOVIDO]", texto_limpo)

        # 5. Normalizar múltiplos espaços
        texto_limpo = re.sub(r"\s+", " ", texto_limpo).strip()

        return texto_limpo

    @classmethod
    def preparar_para_corpus(cls, pergunta: str, resposta: str, max_chars_pergunta: int = 255) -> Tuple[str, str]:
        """
        Higieniza e formata a pergunta e resposta para persistência no banco.
        Trunca a pergunta para caber na coluna se necessário de forma legível.
        """
        pergunta_limpa = cls.sanitizar(pergunta)
        resposta_limpa = cls.sanitizar(resposta)

        if len(pergunta_limpa) > max_chars_pergunta:
            # Trunca no último espaço antes do limite para não quebrar palavras
            pergunta_limpa = pergunta_limpa[:max_chars_pergunta].rsplit(" ", 1)[0]
            if not pergunta_limpa.endswith("?"):
                pergunta_limpa += "?"

        return pergunta_limpa, resposta_limpa

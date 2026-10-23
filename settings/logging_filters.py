import logging
import re

_EMAIL_RE = re.compile(
    r"(?<![\w.+-])([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Za-z]{2,})"
)
_IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")


def mask_pii(value: object) -> str:
    """Mascara e-mail e IPv4 em mensagens de log.

    O filtro é uma proteção adicional. O código não deve registrar conteúdo de
    mensagens, respostas, senhas ou tokens.
    """
    text = str(value)

    text = _EMAIL_RE.sub(lambda match: f"***@{match.group(2)}", text)
    text = _IPV4_RE.sub("***.***.***.***", text)
    return text


class PIIMaskingFilter(logging.Filter):
    """Aplica ``mask_pii`` na mensagem formatada do registro."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            message = record.getMessage()
            masked = mask_pii(message)
            if masked != message:
                record.msg = masked
                record.args = ()
            if getattr(record, "exc_text", None):
                record.exc_text = mask_pii(record.exc_text)
        except Exception:
            # Nunca deixe uma falha de mascaramento impedir o log operacional.
            pass
        return True

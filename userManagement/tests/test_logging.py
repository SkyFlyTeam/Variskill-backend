import logging

from settings.logging_filters import PIIMaskingFilter, mask_pii


def test_mask_pii_masks_email_and_ipv4():
    texto = "Contato ana@example.com falhou no IP 192.168.10.25"
    mascarado = mask_pii(texto)

    assert "ana@example.com" not in mascarado
    assert "***@example.com" in mascarado
    assert "192.168.10.25" not in mascarado
    assert "***.***.***.***" in mascarado


def test_pii_filter_masks_formatted_log_record():
    record = logging.LogRecord(
        name="teste",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="usuario=%s ip=%s",
        args=("ana@example.com", "10.0.0.8"),
        exc_info=None,
    )

    PIIMaskingFilter().filter(record)

    assert record.getMessage() == "usuario=***@example.com ip=***.***.***.***"

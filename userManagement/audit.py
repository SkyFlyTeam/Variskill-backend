import hashlib
import logging

from django.conf import settings

from .models import EventoAuditoria

logger = logging.getLogger(__name__)


def _client_ip(request):
    if request is None:
        return ''
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def hash_ip(ip):
    """Nunca armazena o IP cru; usa hash com segredo do projeto."""
    if not ip:
        return ''
    salt = getattr(settings, 'LGPD_AUDIT_IP_SALT', settings.SECRET_KEY)
    return hashlib.sha256(f'{salt}:{ip}'.encode('utf-8')).hexdigest()


def registrar_evento(
    *,
    usuario=None,
    acao,
    request=None,
    resultado='SUCESSO',
    status_code=None,
    recurso='',
    recurso_id=None,
    metadata=None,
    ator_email='',
):
    """Grava um evento de auditoria sem nunca persistir conteúdo sensível.

    Falhas de auditoria não devem derrubar a requisição do usuário.
    """
    try:
        autenticado = bool(getattr(usuario, 'is_authenticated', False))
        email = ator_email or (getattr(usuario, 'email', '') if autenticado else '')
        EventoAuditoria.objects.create(
            usuario=usuario if autenticado else None,
            ator_email=(email or '')[:254],
            ator_is_staff=bool(getattr(usuario, 'is_staff', False)) if autenticado else False,
            acao=acao,
            metodo=(getattr(request, 'method', '') if request is not None else '')[:10],
            rota=(getattr(request, 'path', '') if request is not None else '')[:500],
            status_code=status_code,
            resultado=resultado,
            recurso=(recurso or '')[:40],
            recurso_id=recurso_id,
            ip_hash=hash_ip(_client_ip(request)),
            user_agent=(
                request.META.get('HTTP_USER_AGENT', '') if request is not None else ''
            )[:1000],
            metadata=metadata or {},
        )
    except Exception:
        logger.exception('Falha ao registrar evento de auditoria.')

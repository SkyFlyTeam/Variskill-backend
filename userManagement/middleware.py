import logging

from .audit import registrar_evento

logger = logging.getLogger(__name__)

SKIP_PREFIXES = (
    '/static/',
    '/media/',
    '/healthz',
)


class AuditRequestMiddleware:
    """Registra requisições de API/admin para auditoria.

    O foco é rastrear login, navegação e ações de usuários e administradores.
    Nunca grava corpo de requisição, senha, token ou conteúdo de mensagem.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        path = request.path or ''
        if path.startswith(SKIP_PREFIXES):
            return response

        if not (path.startswith('/api/') or path.startswith('/admin/')):
            return response

        try:
            user = getattr(request, 'user', None)
            registrar_evento(
                usuario=user,
                acao='REQUISICAO',
                request=request,
                status_code=response.status_code,
                resultado='SUCESSO' if response.status_code < 400 else 'FALHA',
                metadata={
                    'status_code': response.status_code,
                    'is_staff': bool(getattr(user, 'is_staff', False)),
                },
            )
        except Exception:
            logger.exception('Falha ao auditar requisição.')

        return response

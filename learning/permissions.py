from rest_framework import permissions


class IsAdminForUnsafeMethods(permissions.BasePermission):
    """Leitura liberada a qualquer usuário autenticado; escrita exige perfil administrador."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)

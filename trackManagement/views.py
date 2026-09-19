from rest_framework import permissions, viewsets

from .models import Modulo
from .serializers import ModuloSerializer


class ModuloViewSet(viewsets.ModelViewSet):
    """CRUD de módulos pedagógicos (RFN03).

    - Listagem e detalhe públicos, filtráveis por `trilha_id` e ordenados por `ordem_modulo`.
    - Criação, atualização e exclusão restritas a administradores.
    """

    serializer_class = ModuloSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get_queryset(self):
        queryset = Modulo.objects.select_related('trilha').order_by('ordem_modulo')
        trilha_id = self.request.query_params.get('trilha_id')
        if trilha_id:
            queryset = queryset.filter(trilha_id=trilha_id)
        return queryset

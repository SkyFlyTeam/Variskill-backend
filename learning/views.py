from django.db import transaction
from rest_framework import permissions, status, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response

from activityManagement.models import Atividade, Conteudo

from .models import Module

from .permissions import IsAdminForUnsafeMethods
from .serializers import ActivityCreateSerializer, ActivitySerializer, ContentSerializer, ModuleSerializer


class ModuleViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminForUnsafeMethods)
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer


class ActivityViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminForUnsafeMethods)
    queryset = Atividade.objects.select_related('modulo', 'conteudo').prefetch_related('questoes__opcoes')

    def get_serializer_class(self):
        if self.action == 'create':
            return ActivityCreateSerializer
        return ActivitySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in ('list', 'retrieve') and not self.request.user.is_staff:
            queryset = queryset.filter(ativo=True)
        return queryset

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=many)
        serializer.is_valid(raise_exception=True)
        atividades = serializer.save()
        atividades = atividades if many else [atividades]
        output = ActivitySerializer(
            atividades, many=True, context=self.get_serializer_context()
        )
        return Response(output.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        activity = self.get_object()
        activity.ativo = False
        activity.save(update_fields=['ativo'])
        return Response({'mensagem': 'Atividade desativada com sucesso.'})


class ContentViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminForUnsafeMethods)
    queryset = Conteudo.objects.all()
    serializer_class = ContentSerializer

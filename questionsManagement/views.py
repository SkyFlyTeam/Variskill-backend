from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication

from .models import Questao
from .serializers import QuestaoCreateSerializer, QuestaoSerializer


class QuestaoViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAdminUser,)
    queryset = Questao.objects.prefetch_related('opcoes').select_related('atividade')

    def get_serializer_class(self):
        if self.action == 'create':
            return QuestaoCreateSerializer
        return QuestaoSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        questao = serializer.save()
        output = QuestaoSerializer(questao, context=self.get_serializer_context())
        return Response(output.data, status=status.HTTP_201_CREATED)

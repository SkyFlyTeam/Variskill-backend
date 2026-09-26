from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from assistantManagement.serializers import DecisaoNivelSerializer
from assistantManagement.services import decidir_nivel_trilha


class DecidirNivelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, sessao_id):
        serializer = DecisaoNivelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = decidir_nivel_trilha(
            usuario=request.user,
            sessao_id=sessao_id,
            trilha_id=serializer.validated_data['trilha_id'],
            opcao=serializer.validated_data['opcao'],
        )

        return Response(result, status=status.HTTP_200_OK)

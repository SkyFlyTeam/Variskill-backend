from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from assistantManagement.serializers import (
    DecisaoNivelSerializer,
    EnviarMensagemInputSerializer,
    EnviarMensagemResponseSerializer,
    HistoricoSessaoResponseSerializer,
    IniciarSessaoResponseSerializer,
)
from assistantManagement.services import (
    decidir_nivel_trilha,
    enviar_mensagem_chat,
    iniciar_sessao_chat,
    obter_historico_chat,
)


class IniciarSessaoView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Iniciar sessão de conversa do estudante com o Coach no onboarding",
        description="Cria uma nova sessão de chat ativa para o estudante e retorna a mensagem inicial de boas-vindas do assistente com sugestões rápidas de diálogo.",
        responses={
            201: OpenApiResponse(
                response=IniciarSessaoResponseSerializer,
                description="Sessão criada com sucesso.",
            )
        },
    )
    def post(self, request):
        result = iniciar_sessao_chat(usuario=request.user)
        serializer = IniciarSessaoResponseSerializer(result)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EnviarMensagemView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Enviar mensagem do estudante para o assistente",
        description="Recebe a mensagem do estudante, executa pré-processamento de texto e embedding via pipeline local de PLN, classifica a intenção via pgvector e salva ambas as mensagens na sessão.",
        request=EnviarMensagemInputSerializer,
        responses={
            200: OpenApiResponse(
                response=EnviarMensagemResponseSerializer,
                description="Mensagem processada e resposta emitida.",
            )
        },
    )
    def post(self, request, sessao_id):
        serializer = EnviarMensagemInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = enviar_mensagem_chat(
            usuario=request.user,
            sessao_id=sessao_id,
            conteudo=serializer.validated_data["conteudo"],
        )
        response_serializer = EnviarMensagemResponseSerializer(result)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class HistoricoSessaoView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Obter histórico de mensagens da sessão",
        description="Retorna a lista sequencial de balões de mensagens trocados na sessão entre estudante e assistente.",
        responses={
            200: OpenApiResponse(
                response=HistoricoSessaoResponseSerializer,
                description="Histórico de mensagens recuperado com sucesso.",
            )
        },
    )
    def get(self, request, sessao_id):
        result = obter_historico_chat(usuario=request.user, sessao_id=sessao_id)
        serializer = HistoricoSessaoResponseSerializer(result)
        return Response(serializer.data, status=status.HTTP_200_OK)


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


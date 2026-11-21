from django.db import transaction
from django.db.models import F
from django.http import Http404
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from assistantManagement.serializers import (
    DecisaoNivelSerializer,
    EnviarMensagemInputSerializer,
    EnviarMensagemResponseSerializer,
    FeedbackDuvidaInputSerializer,
    FeedbackDuvidaResponseSerializer,
    HistoricoSessaoResponseSerializer,
    IniciarSessaoResponseSerializer,
)
from assistantManagement.services import (
    decidir_nivel_trilha,
    enviar_mensagem_chat,
    iniciar_sessao_chat,
    obter_historico_chat,
)
from semanticSearch.models import DuvidaAssimilada


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
        description="Recebe a mensagem do estudante, executa pré-processamento de texto e embedding via pipeline local de PLN, classifica a intenção via pgvector, executa a ação de sistema da intenção (listar trilhas, matrícula, diagnóstico, nível básico ou dica) e salva ambas as mensagens na sessão. Os campos opcionais trilha_id, atividade_id e questao_id fornecem contexto à ação.",
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
            trilha_id=serializer.validated_data.get("trilha_id"),
            atividade_id=serializer.validated_data.get("atividade_id"),
            questao_id=serializer.validated_data.get("questao_id"),
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


class FeedbackDuvidaView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Registrar feedback do estudante sobre uma dúvida assimilada",
        description="Incrementa atomicamente feedbacks_positivos (util=true) ou feedbacks_negativos (util=false) da DuvidaAssimilada informada e retorna os contadores atualizados.",
        request=FeedbackDuvidaInputSerializer,
        responses={
            200: OpenApiResponse(
                response=FeedbackDuvidaResponseSerializer,
                description="Feedback registrado com sucesso.",
            ),
            404: OpenApiResponse(description="Dúvida assimilada não encontrada."),
        },
    )
    def post(self, request, duvida_id):
        serializer = FeedbackDuvidaInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        campo = "feedbacks_positivos" if serializer.validated_data["util"] else "feedbacks_negativos"

        with transaction.atomic():
            atualizados = DuvidaAssimilada.objects.filter(pk=duvida_id).update(**{campo: F(campo) + 1})
            if not atualizados:
                raise Http404("Dúvida assimilada não encontrada.")
            contadores = DuvidaAssimilada.objects.filter(pk=duvida_id).values(
                "feedbacks_positivos", "feedbacks_negativos"
            ).get()

        response_serializer = FeedbackDuvidaResponseSerializer({"sucesso": True, **contadores})
        return Response(response_serializer.data, status=status.HTTP_200_OK)

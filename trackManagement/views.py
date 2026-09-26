import uuid
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from activityManagement.models import Atividade
from .models import Matricula, ProgressoModulo, Trilha
from .serializers import (
    MatriculaCriarSerializer,
    MatriculaSaidaSerializer,
    PosicionarNivelInputSerializer,
    PosicionarNivelOutputSerializer,
    TrilhaListaSerializer,
)
from .services import efetivar_matricula, posicionar_nivel_pos_diagnostico


class RoadmapView(APIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, trilha_id):
        trilha = get_object_or_404(Trilha, pk=trilha_id, ativo=True)
        matricula = Matricula.objects.filter(usuario=request.user, trilha=trilha, status='EM_ANDAMENTO').first()
        progress = {p.modulo_id: p.status for p in ProgressoModulo.objects.filter(matricula=matricula)} if matricula else {}
        modules = list(trilha.modulos.all().order_by('ordem_modulo'))
        activities = Atividade.objects.filter(modulo_id__in=[m.pk for m in modules], ativo=True).select_related('conteudo').order_by('ordem')
        by_module = {}
        for a in activities:
            by_module.setdefault(a.modulo_id, []).append(a)
        done = set(Atividade.objects.filter(execucoes__usuario=request.user, execucoes__aprovado=True, modulo_id__in=by_module).values_list('pk', flat=True)) if matricula else set()
        result, recommended, completed, total = [], None, 0, 0
        for module in modules:
            module_status = progress.get(module.pk, 'BLOQUEADO') if matricula else 'BLOQUEADO'
            unlocked, output = module_status != 'BLOQUEADO' and matricula is not None, []
            for a in by_module.get(module.pk, []):
                total += 1
                if a.pk in done:
                    status_activity = 'CONCLUIDO'
                    completed += 1
                elif unlocked:
                    status_activity, unlocked = 'EM_ANDAMENTO', False
                    if recommended is None:
                        recommended = {'id': a.pk, 'titulo': a.titulo, 'modulo_id': module.pk}
                else:
                    status_activity = 'BLOQUEADO'
                output.append({
                    'id': a.pk,
                    'titulo': a.titulo,
                    'contexto_avaliacao': a.contexto_avaliacao,
                    'status': status_activity,
                    'xp_recompensa': a.xp_recompensa,
                    'conteudo_teorico': ({'id': a.conteudo.pk, 'titulo': a.conteudo.titulo} if a.conteudo else None)
                })
            if module_status == 'CONCLUIDO' or (output and all(a['status'] == 'CONCLUIDO' for a in output)):
                module_status = 'CONCLUIDO'
            result.append({'id': module.pk, 'titulo': module.titulo, 'nivel': module.nivel, 'status': module_status, 'atividades': output})
        return Response({
            'trilha': {'id': trilha.pk, 'titulo': trilha.titulo, 'habilidade': trilha.habilidade},
            'percentual_conclusao': round(completed * 100 / total, 1) if total else 0.0,
            'modulos': result,
            'proxima_atividade_recomendada': recommended
        })


class PosicionarNivelView(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(
        request=PosicionarNivelInputSerializer,
        responses={200: PosicionarNivelOutputSerializer},
        summary="Posiciona o nível do estudante na trilha após teste diagnóstico",
        description=(
            "Calcula a taxa de acerto da atividade diagnóstica, posiciona o estudante no "
            "nível correspondente (INICIANTE, INTERMEDIARIO ou AVANCADO) e atualiza atomicamente "
            "o PROGRESSO_MODULO da matrícula."
        ),
    )
    def post(self, request, atividade_id: uuid.UUID):
        serializer = PosicionarNivelInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        matricula_id = serializer.validated_data['matricula_id']

        result = posicionar_nivel_pos_diagnostico(
            user=request.user,
            atividade_id=atividade_id,
            matricula_id=matricula_id,
        )

        response_data = {
            'nivel_posicionado': result.nivel_posicionado,
            'taxa_acerto': result.taxa_acerto,
            'modulos_liberados': result.modulos_liberados,
            'mensagem_assistente': result.mensagem_assistente,
        }

        output_serializer = PosicionarNivelOutputSerializer(data=response_data)
        output_serializer.is_valid(raise_exception=True)

        return Response(output_serializer.data, status=status.HTTP_200_OK)


class TrilhaViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TrilhaListaSerializer
    queryset = (
        Trilha.objects.filter(ativo=True)
        .annotate(
            total_modulos=Count('modulos', distinct=True),
            total_atividades=Count(
                'modulos__atividades',
                filter=Q(modulos__atividades__ativo=True),
                distinct=True,
            ),
        )
        .order_by('titulo')
    )


class MatriculaViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = MatriculaSaidaSerializer

    def get_queryset(self):
        return Matricula.objects.filter(
            usuario=self.request.user,
        ).select_related('trilha')

    def create(self, request, *args, **kwargs):
        serializer = MatriculaCriarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        trilha = get_object_or_404(
            Trilha,
            pk=serializer.validated_data['trilha_id'],
            ativo=True,
        )
        matricula = efetivar_matricula(request.user, trilha)

        return Response(
            {
                'mensagem': 'Matrícula realizada com sucesso',
                'matricula': MatriculaSaidaSerializer(matricula).data,
            },
            status=status.HTTP_201_CREATED,
        )

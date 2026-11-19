from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import decorators, generics, permissions, status, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.response import Response

from assistantManagement.models import MemoriaPedagogicaUsuario

from .audit import registrar_evento
from .models import (
    Conquista,
    EventoAuditoria,
    Interesse,
    SolicitacaoRevisao,
    User,
    UsuarioConquista,
    UsuarioInventario,
)
from .serializers import (
    AuthSerializer,
    ChangePasswordSerializer,
    ConquistaUsuarioSerializer,
    DiagnosticoPedagogicoSerializer,
    EventoAuditoriaSerializer,
    InteresseSerializer,
    ItemInventarioSerializer,
    SolicitacaoRevisaoAdminSerializer,
    SolicitacaoRevisaoCreateSerializer,
    SolicitacaoRevisaoSerializer,
    UserSerializer,
)
from .services import anonimizar_usuario, exportar_dados_usuario

PROFILE_AUDIT_FIELDS = ('nome', 'apelido', 'email', 'sexo', 'idade')


def _profile_snapshot(user):
    return {field: getattr(user, field) for field in PROFILE_AUDIT_FIELDS}


def _registrar_alteracao_perfil(request, usuario, antes):
    depois = _profile_snapshot(usuario)
    campos = [field for field in PROFILE_AUDIT_FIELDS if antes.get(field) != depois.get(field)]
    if not campos:
        return
    registrar_evento(
        usuario=request.user,
        acao='ALTERACAO_PERFIL',
        request=request,
        ator_email=getattr(request.user, 'email', ''),
        recurso='USER',
        recurso_id=usuario.pk,
        metadata={
            'campos': campos,
            'email_alterado': 'email' in campos,
        },
    )


class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = User.objects.all().order_by('id')
        if getattr(settings, 'LGPD_RESTRINGIR_USERS', True) and not self.request.user.is_staff:
            return queryset.filter(pk=self.request.user.pk)
        return queryset

    def get_permissions(self):
        if self.action in ('hard_delete', 'admin_export'):
            return [permissions.IsAdminUser()]
        if self.action == 'create' and getattr(settings, 'LGPD_RESTRINGIR_USERS', True):
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def destroy(self, request, *args, **kwargs):
        if getattr(settings, 'LGPD_RESTRINGIR_USERS', True) and not request.user.is_staff:
            raise PermissionDenied(
                'Use DELETE /api/users/me/ para excluir a própria conta.'
            )
        return super().destroy(request, *args, **kwargs)

    @decorators.action(detail=False, methods=['get', 'patch', 'delete'], url_path='me')
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)

        if request.method == 'DELETE':
            email_original = request.user.email
            registrar_evento(
                usuario=request.user,
                acao='ANONIMIZACAO_CONTA',
                request=request,
                ator_email=email_original,
            )
            registrar_evento(
                usuario=request.user,
                acao='CONSENTIMENTO_REVOGADO',
                request=request,
                ator_email=email_original,
                metadata={'motivo': 'exclusao_conta'},
            )
            anonimizar_usuario(request.user)
            logout(request)
            return Response(status=status.HTTP_204_NO_CONTENT)

        antes = _profile_snapshot(request.user)
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        _registrar_alteracao_perfil(request, request.user, antes)
        return Response(serializer.data)

    def perform_update(self, serializer):
        instance = serializer.instance
        antes = _profile_snapshot(instance)
        serializer.save()
        _registrar_alteracao_perfil(self.request, instance, antes)

    @decorators.action(detail=False, methods=['get'], url_path='admin-export')
    def admin_export(self, request):
        email = (request.query_params.get('email') or '').strip()
        if not email:
            raise ValidationError({'email': 'Informe o e-mail do titular.'})

        target = User.objects.filter(email__iexact=email).first()
        if target is None:
            raise NotFound('Usuário não encontrado para o e-mail informado.')

        response = Response(exportar_dados_usuario(target))
        response['Content-Disposition'] = 'attachment; filename="variskill-dados-titular.json"'
        registrar_evento(
            usuario=request.user,
            acao='EXPORTACAO_DADOS',
            request=request,
            recurso='USER',
            recurso_id=target.pk,
            metadata={'email_alvo': target.email, 'canal': 'admin_email'},
        )
        return response

    @decorators.action(detail=False, methods=['post'], url_path='me/alterar-senha')
    def change_password(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={'user': request.user}
        )
        serializer.is_valid(raise_exception=True)

        if not request.user.check_password(serializer.validated_data['senha_atual']):
            raise ValidationError({'senha_atual': 'Senha atual incorreta.'})

        request.user.set_password(serializer.validated_data['nova_senha'])
        request.user.save(update_fields=['password'])
        registrar_evento(
            usuario=request.user,
            acao='TROCA_SENHA',
            request=request,
        )
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(
        detail=False,
        methods=['delete'],
        url_path='hard-delete',
        permission_classes=(permissions.IsAdminUser,),
    )
    def hard_delete(self, request):
        email = (
            request.query_params.get('email')
            or (request.data.get('email') if isinstance(request.data, dict) else '')
            or ''
        ).strip()
        if not email:
            raise ValidationError({'email': 'Informe o e-mail do titular.'})

        target = User.objects.filter(email__iexact=email).first()
        if target is None:
            raise NotFound('Usuário não encontrado para o e-mail informado.')

        target_id = target.pk
        target_email = target.email

        with transaction.atomic():
            registrar_evento(
                usuario=request.user,
                acao='HARD_DELETE',
                request=request,
                recurso='USER',
                recurso_id=target_id,
                metadata={'email_alvo': target_email},
            )
            registrar_evento(
                usuario=request.user,
                acao='CONSENTIMENTO_REVOGADO',
                request=request,
                ator_email=target_email,
                recurso='USER',
                recurso_id=target_id,
                metadata={'email_alvo': target_email, 'motivo': 'hard_delete'},
            )
            # CASCADE remove sessões, mensagens, matrículas, progresso,
            # execuções, respostas, consentimento, interesses e revisões.
            target.delete()

        return Response(
            {'email': target_email, 'id': str(target_id), 'deleted': True},
            status=status.HTTP_200_OK,
        )


class RegisterView(generics.GenericAPIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not serializer.validated_data.get('aceite_termos'):
            raise ValidationError({
                'aceite_termos': 'Você precisa aceitar os Termos de Uso para se cadastrar.'
            })

        user = serializer.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        registrar_evento(
            usuario=user,
            acao='CADASTRO',
            request=request,
            recurso='USER',
            recurso_id=user.pk,
        )
        registrar_evento(
            usuario=user,
            acao='CONSENTIMENTO_CONCEDIDO',
            request=request,
            recurso='USER',
            recurso_id=user.pk,
            metadata={'versao': user.aceite_privacidade_versao},
        )

        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )


class LoginView(generics.GenericAPIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)
    serializer_class = AuthSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data.get(
            'apelido'
        ) or serializer.validated_data.get('email')

        user = authenticate(
            request,
            username=identifier,
            password=serializer.validated_data['password'],
        )
        if user is None:
            registrar_evento(
                usuario=None,
                acao='LOGIN_FALHA',
                request=request,
                resultado='FALHA',
                ator_email=identifier if '@' in (identifier or '') else '',
                metadata={'identificador': (identifier or '')[:150]},
            )
            return Response(
                {'detail': 'Invalid credentials.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        login(request, user)
        registrar_evento(usuario=user, acao='LOGIN', request=request)
        return Response(UserSerializer(user).data)


class LogoutView(generics.GenericAPIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        user = request.user if getattr(request.user, 'is_authenticated', False) else None
        registrar_evento(usuario=user, acao='LOGOUT', request=request)
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class InteresseListView(generics.ListAPIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = InteresseSerializer
    queryset = Interesse.objects.filter(ativo=True)


class DiagnosticoPedagogicoView(generics.GenericAPIView):
    """Raio-X de aprendizado do usuário logado (VAR-126).

    Só lê a MemoriaPedagogicaUsuario já consolidada (uma consulta), sem recalcular:
    a consolidação roda em segundo plano a cada submissão de atividade (VAR-118).
    """

    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = DiagnosticoPedagogicoSerializer

    @extend_schema(
        summary='Diagnóstico pedagógico do estudante logado',
        description=(
            'Retorna os pontos fortes, os tópicos com dificuldade, a taxa de acerto geral, '
            'o total de atividades avaliadas e a data da última consolidação da memória '
            'pedagógica do usuário autenticado. Usuários sem memória consolidada recebem '
            '200 com listas vazias, taxa 0 e ultima_atualizacao nula.'
        ),
        responses={
            200: OpenApiResponse(
                response=DiagnosticoPedagogicoSerializer,
                description='Diagnóstico do usuário (ou payload padrão sem histórico).',
            ),
        },
        tags=['users'],
    )
    def get(self, request):
        memoria = (
            MemoriaPedagogicaUsuario.objects.filter(usuario=request.user)
            .only(
                'pontos_fortes', 'topicos_dificuldade', 'taxa_acerto_geral',
                'total_atividades_avaliadas', 'atualizado_em',
            )
            .first()
        )
        if memoria is None:
            dados = {
                'pontos_fortes': [],
                'topicos_dificuldade': [],
                'taxa_acerto_geral': 0.0,
                'total_atividades_avaliadas': 0,
                'ultima_atualizacao': None,
            }
        else:
            dados = {
                'pontos_fortes': memoria.pontos_fortes or [],
                'topicos_dificuldade': memoria.topicos_dificuldade or [],
                'taxa_acerto_geral': memoria.taxa_acerto_geral,
                'total_atividades_avaliadas': memoria.total_atividades_avaliadas,
                'ultima_atualizacao': memoria.atualizado_em,
            }
        return Response(self.get_serializer(dados).data)


class SolicitacaoRevisaoViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_queryset(self):
        if self.request.user.is_staff:
            return SolicitacaoRevisao.objects.all()
        return SolicitacaoRevisao.objects.filter(usuario=self.request.user)

    def get_permissions(self):
        if self.action in ('partial_update', 'update'):
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return SolicitacaoRevisaoCreateSerializer
        if self.action in ('partial_update', 'update'):
            return SolicitacaoRevisaoAdminSerializer
        return SolicitacaoRevisaoSerializer

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        registrar_evento(
            usuario=request.user,
            acao='REVISAO_SOLICITADA',
            request=request,
            recurso='SOLICITACAO_REVISAO',
            recurso_id=serializer.instance.pk,
            metadata={'tipo': serializer.instance.tipo},
        )
        return Response(
            SolicitacaoRevisaoSerializer(serializer.instance).data,
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = SolicitacaoRevisaoAdminSerializer(
            instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        registrar_evento(
            usuario=request.user,
            acao='REVISAO_RESPONDIDA',
            request=request,
            recurso='SOLICITACAO_REVISAO',
            recurso_id=instance.pk,
            metadata={'tipo': instance.tipo, 'status': instance.status},
        )
        return Response(SolicitacaoRevisaoSerializer(instance).data)

    def perform_update(self, serializer):
        serializer.save(respondido_em=timezone.now())


class EventoAuditoriaListView(generics.ListAPIView):
    """Consulta administrativa de auditoria, sem tela no frontend."""

    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = EventoAuditoriaSerializer

    def get_queryset(self):
        queryset = EventoAuditoria.objects.select_related('usuario').all()
        acao = self.request.query_params.get('acao')
        email = self.request.query_params.get('email')
        inicio = self.request.query_params.get('inicio')
        fim = self.request.query_params.get('fim')

        if acao:
            queryset = queryset.filter(acao=acao)
        if email:
            queryset = queryset.filter(ator_email__iexact=email)
        if inicio:
            data_inicio = parse_datetime(inicio)
            if data_inicio:
                queryset = queryset.filter(criado_em__gte=data_inicio)
        if fim:
            data_fim = parse_datetime(fim)
            if data_fim:
                queryset = queryset.filter(criado_em__lte=data_fim)

        try:
            limite = int(self.request.query_params.get('limit', 100))
        except (TypeError, ValueError):
            limite = 100
        limite = min(max(limite, 1), 500)
        return queryset[:limite]


# Mapeia o tipo do item cosmético para a chave do agrupamento no inventário
# e para a FK correspondente em User.
CATEGORIAS_INVENTARIO = {
    'AVATAR': ('avatares', 'avatar_equipado'),
    'TITULO': ('titulos', 'titulo_equipado'),
    'BORDA': ('bordas', 'borda_equipada'),
}


class ConquistaListView(generics.GenericAPIView):
    """Catálogo de conquistas com o status de desbloqueio do usuário logado."""

    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ConquistaUsuarioSerializer

    def get(self, request):
        desbloqueios = dict(
            UsuarioConquista.objects.filter(usuario=request.user)
            .values_list('conquista_id', 'desbloqueado_em')
        )
        conquistas = Conquista.objects.order_by('ordem', 'titulo')
        serializer = self.get_serializer(
            conquistas, many=True, context={'desbloqueios': desbloqueios}
        )
        return Response(serializer.data)


class InventarioView(generics.GenericAPIView):
    """Inventário do usuário logado agrupado por categoria de item."""

    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ItemInventarioSerializer

    def get(self, request):
        itens = (
            UsuarioInventario.objects.filter(usuario=request.user)
            .select_related('item')
            .order_by('item__nome')
        )
        agrupado = {chave: [] for chave, _ in CATEGORIAS_INVENTARIO.values()}
        for dado, registro in zip(self.get_serializer(itens, many=True).data, itens):
            chave, _ = CATEGORIAS_INVENTARIO[registro.item.tipo]
            agrupado[chave].append(dado)
        return Response(agrupado)


class EquiparItemView(generics.GenericAPIView):
    """Equipa um item do inventário, desequipando o anterior do mesmo tipo.

    ``inventario_id`` é o id do registro em UsuarioInventario. Registros de
    outros usuários retornam 404, sem revelar que existem.
    """

    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = None

    def post(self, request, inventario_id):
        with transaction.atomic():
            # Trava a linha do usuário para serializar equipamentos concorrentes.
            usuario = User.objects.select_for_update().get(pk=request.user.pk)
            registro = (
                UsuarioInventario.objects.select_related('item')
                .filter(usuario=usuario, pk=inventario_id)
                .first()
            )
            if registro is None:
                raise NotFound('Item não encontrado no inventário do usuário.')

            tipo = registro.item.tipo
            if tipo not in CATEGORIAS_INVENTARIO:
                raise ValidationError({'tipo': f'Tipo de item não equipável: {tipo}'})
            _, campo_user = CATEGORIAS_INVENTARIO[tipo]

            UsuarioInventario.objects.filter(
                usuario=usuario, item__tipo=tipo, equipado=True
            ).exclude(pk=registro.pk).update(equipado=False)

            if not registro.equipado:
                registro.equipado = True
                registro.save(update_fields=['equipado'])

            setattr(usuario, campo_user, registro.item)
            usuario.save(update_fields=[campo_user])

        return Response(
            {'sucesso': True, 'item_equipado_id': str(registro.pk), 'tipo': tipo},
            status=status.HTTP_200_OK,
        )

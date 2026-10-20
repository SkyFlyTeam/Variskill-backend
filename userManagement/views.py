from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from rest_framework import decorators, generics, permissions, status, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from .models import Consentimento, Interesse, SolicitacaoRevisao, User
from .serializers import (
    AuthSerializer,
    ChangePasswordSerializer,
    ConsentimentoSerializer,
    InteresseSerializer,
    SolicitacaoRevisaoAdminSerializer,
    SolicitacaoRevisaoCreateSerializer,
    SolicitacaoRevisaoSerializer,
    UserSerializer,
)
from .services import anonimizar_usuario, exportar_dados_usuario


class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = User.objects.all().order_by('id')
        # Fix de segurança/LGPD: usuário comum só enxerga a própria conta.
        # A flag permite reverter para o comportamento antigo em clientes legados.
        if getattr(settings, 'LGPD_RESTRINGIR_USERS', True) and not self.request.user.is_staff:
            return queryset.filter(pk=self.request.user.pk)
        return queryset

    def get_permissions(self):
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
            anonimizar_usuario(request.user)
            logout(request)
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @decorators.action(detail=False, methods=['get'], url_path='export')
    def export(self, request):
        response = Response(exportar_dados_usuario(request.user))
        response['Content-Disposition'] = 'attachment; filename="variskill-meus-dados.json"'
        return response

    @decorators.action(detail=False, methods=['post'], url_path='alterar-senha')
    def change_password(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={'user': request.user}
        )
        serializer.is_valid(raise_exception=True)

        if not request.user.check_password(serializer.validated_data['senha_atual']):
            raise ValidationError({'senha_atual': 'Senha atual incorreta.'})

        request.user.set_password(serializer.validated_data['nova_senha'])
        request.user.save(update_fields=['password'])
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RegisterView(generics.GenericAPIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

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
            return Response(
                {'detail': 'Invalid credentials.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        login(request, user)
        return Response(UserSerializer(user).data)


class LogoutView(generics.GenericAPIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class InteresseListView(generics.ListAPIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = InteresseSerializer
    queryset = Interesse.objects.filter(ativo=True)


class ConsentimentoListView(generics.ListCreateAPIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ConsentimentoSerializer

    def get_queryset(self):
        return Consentimento.objects.filter(usuario=self.request.user).order_by('tipo')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tipo = serializer.validated_data['tipo']
        versao = serializer.validated_data.get('versao_documento', '')

        consentimento, _ = Consentimento.objects.get_or_create(
            usuario=request.user,
            tipo=tipo,
            defaults={'versao_documento': versao},
        )
        # Reexecuta o consentimento revogado; atualiza timestamp sem perder o registro.
        Consentimento.objects.filter(pk=consentimento.pk).update(
            concedido_em=timezone.now(),
            revogado_em=None,
            versao_documento=versao,
        )
        consentimento.refresh_from_db()

        return Response(
            ConsentimentoSerializer(consentimento).data,
            status=status.HTTP_201_CREATED,
        )


class ConsentimentoDetailView(generics.DestroyAPIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ConsentimentoSerializer
    lookup_field = 'tipo'

    def get_queryset(self):
        return Consentimento.objects.filter(usuario=self.request.user)

    def perform_destroy(self, instance):
        instance.revogado_em = timezone.now()
        instance.save(update_fields=['revogado_em'])

        if (
            getattr(settings, 'LGPD_LIMPAR_AO_REVOGAR', False)
            and instance.tipo == 'DADOS_OPCIONAIS'
        ):
            request_user = self.request.user
            request_user.sexo = None
            request_user.idade = None
            request_user.save(update_fields=['sexo', 'idade'])


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
        return Response(SolicitacaoRevisaoSerializer(instance).data)

    def perform_update(self, serializer):
        serializer.save(respondido_em=timezone.now())

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from .models import Consentimento, EventoAuditoria, Interesse, SolicitacaoRevisao, UsuarioInteresse
from .services import GamificationService

User = get_user_model()


class InteresseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interesse
        fields = ('id', 'nome')


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    interesses = serializers.SerializerMethodField(read_only=True)
    interesses_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )
    nivel = serializers.SerializerMethodField()
    progresso_nivel = serializers.SerializerMethodField()
    aceite_versao = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = (
            'id', 'apelido', 'nome', 'email', 'password',
            'xp_total', 'streak_dias', 'is_primeiro_acesso',
            'sexo', 'idade', 'interesses', 'interesses_ids',
            'nivel', 'progresso_nivel',
            'aceite_privacidade_versao', 'aceite_privacidade_em', 'anonimizado_em',
            'aceite_versao',
        )
        read_only_fields = (
            'id', 'criado_em', 'nivel', 'progresso_nivel',
            'aceite_privacidade_versao', 'aceite_privacidade_em', 'anonimizado_em',
        )
        extra_kwargs = {
            'apelido': {'required': True},
            'nome': {'required': True},
            'email': {'required': True},
        }

    def get_fields(self):
        fields = super().get_fields()
        # Retrocompatibilidade: clientes legados podem desligar a restrição via env.
        # Com o default seguro (LGPD_CAMPOS_READONLY=True), gamificação não é gravável.
        if getattr(settings, 'LGPD_CAMPOS_READONLY', True):
            for name in ('xp_total', 'streak_dias'):
                if name in fields:
                    fields[name].read_only = True
        return fields

    def get_nivel(self, obj) -> int:
        return GamificationService.calcular_nivel(obj.xp_total)

    def get_progresso_nivel(self, obj) -> dict:
        return GamificationService.obter_progresso_nivel(obj.xp_total)

    def get_interesses(self, obj):
        interesses = Interesse.objects.filter(usuarios_interessados__usuario=obj)
        return InteresseSerializer(interesses, many=True).data

    def validate(self, attrs):
        if self.instance is None and not attrs.get('password'):
            raise serializers.ValidationError({'password': 'This field is required.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('interesses_ids', None)
        aceite_versao = validated_data.pop('aceite_versao', None)
        password = validated_data.pop('password')
        versao_termos = aceite_versao or getattr(settings, 'TERMOS_DE_USO_VERSAO', '1.0')

        with transaction.atomic():
            user = User(**validated_data)
            user.aceite_privacidade_versao = versao_termos
            user.aceite_privacidade_em = timezone.now()
            user.set_password(password)
            user.save()

            # Consentimento automático do cadastro (Termos de Uso).
            Consentimento.objects.create(
                usuario=user,
                tipo='TERMOS_DE_USO',
                email_assinante=user.email,
                versao_documento=versao_termos,
            )
        return user

    def update(self, instance, validated_data):
        interesses_ids = validated_data.pop('interesses_ids', None)
        aceite_versao = validated_data.pop('aceite_versao', None)
        password = validated_data.pop('password', None)

        with transaction.atomic():
            for field, value in validated_data.items():
                setattr(instance, field, value)

            if aceite_versao:
                instance.aceite_privacidade_versao = aceite_versao
                instance.aceite_privacidade_em = timezone.now()

            if password is not None:
                instance.set_password(password)

            instance.save()

            if interesses_ids is not None:
                UsuarioInteresse.objects.filter(usuario=instance).delete()
                interesses = Interesse.objects.filter(id__in=interesses_ids)
                found_ids = {str(i.id) for i in interesses}
                missing = [str(i) for i in interesses_ids if str(i) not in found_ids]
                if missing:
                    raise serializers.ValidationError(
                        {'interesses_ids': f'Interesses não encontrados: {missing}'}
                    )
                UsuarioInteresse.objects.bulk_create([
                    UsuarioInteresse(usuario=instance, interesse=interesse)
                    for interesse in interesses
                ])

        return instance


class AuthSerializer(serializers.Serializer):
    apelido = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if not attrs.get('apelido') and not attrs.get('email'):
            raise serializers.ValidationError('Informe o apelido ou o email.')
        return attrs


class ConsentimentoSerializer(serializers.ModelSerializer):
    ativo = serializers.BooleanField(read_only=True)

    class Meta:
        model = Consentimento
        fields = (
            'id', 'tipo', 'email_assinante', 'concedido_em', 'revogado_em',
            'versao_documento', 'ativo',
        )
        read_only_fields = ('id', 'email_assinante', 'concedido_em', 'revogado_em', 'ativo')


class SolicitacaoRevisaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitacaoRevisao
        fields = (
            'id', 'tipo', 'referencia_id', 'status',
            'criado_em', 'respondido_em', 'resposta',
        )
        read_only_fields = ('id', 'criado_em', 'respondido_em', 'resposta')


class SolicitacaoRevisaoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitacaoRevisao
        fields = ('tipo', 'referencia_id')


class SolicitacaoRevisaoAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitacaoRevisao
        fields = ('status', 'resposta')


class ChangePasswordSerializer(serializers.Serializer):
    senha_atual = serializers.CharField(write_only=True)
    nova_senha = serializers.CharField(write_only=True)

    def validate_nova_senha(self, value):
        from django.contrib.auth.password_validation import validate_password
        validate_password(value, self.context.get('user'))
        return value


class EventoAuditoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventoAuditoria
        fields = (
            'id', 'usuario', 'ator_email', 'ator_is_staff', 'acao',
            'metodo', 'rota', 'status_code', 'resultado', 'recurso',
            'recurso_id', 'ip_hash', 'user_agent', 'metadata', 'criado_em',
        )
        read_only_fields = fields

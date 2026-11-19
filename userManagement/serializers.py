from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from .models import (
    AceiteResponsavel,
    Conquista,
    EventoAuditoria,
    Interesse,
    ItemCosmetico,
    SolicitacaoRevisao,
    UsuarioInteresse,
)
from .services import GamificationService
from .utils import (
    MENSAGEM_MENOR_SEM_RESPONSAVEL,
    apenas_digitos,
    formatar_cpf,
    validar_cpf,
)

User = get_user_model()


class InteresseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interesse
        fields = ('id', 'nome')


class ItemEquipadoSerializer(serializers.ModelSerializer):
    """Resumo de um item cosmético equipado no perfil."""

    class Meta:
        model = ItemCosmetico
        fields = (
            'id', 'nome', 'descricao', 'tipo', 'raridade',
            'recurso_visual', 'asset_url',
        )
        read_only_fields = fields


class ResponsavelSerializer(serializers.ModelSerializer):
    """Dados do responsável legal (somente para titulares menores de 18)."""

    cpf = serializers.CharField(max_length=14)

    class Meta:
        model = AceiteResponsavel
        fields = ('nome', 'cpf', 'email', 'criado_em')
        read_only_fields = ('criado_em',)

    def validate_cpf(self, value):
        if not validar_cpf(value):
            raise serializers.ValidationError('Informe um CPF válido.')
        return apenas_digitos(value)

    def to_representation(self, instance):
        dados = super().to_representation(instance)
        # Devolve o CPF formatado apenas para o próprio titular/admin.
        dados['cpf'] = formatar_cpf(instance.cpf)
        return dados


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    # Somente leitura: para trocar, use POST /gamificacao/inventario/<id>/equipar/.
    avatar_equipado = ItemEquipadoSerializer(read_only=True)
    titulo_equipado = ItemEquipadoSerializer(read_only=True)
    borda_equipada = ItemEquipadoSerializer(read_only=True)
    conquistas_desbloqueadas = serializers.SerializerMethodField()
    interesses = serializers.SerializerMethodField(read_only=True)
    interesses_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )
    nivel = serializers.SerializerMethodField()
    progresso_nivel = serializers.SerializerMethodField()
    streak = serializers.SerializerMethodField()
    aceite_versao = serializers.CharField(write_only=True, required=False, allow_blank=True)
    aceite_termos = serializers.BooleanField(write_only=True, required=False)
    idade = serializers.IntegerField(
        min_value=1, max_value=120, required=False, allow_null=True
    )
    responsavel = ResponsavelSerializer(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            'id', 'apelido', 'nome', 'email', 'password',
            'xp_total', 'streak_dias', 'is_primeiro_acesso',
            'sexo', 'idade', 'interesses', 'interesses_ids',
            'nivel', 'progresso_nivel', 'streak',
            'avatar_equipado', 'titulo_equipado', 'borda_equipada',
            'conquistas_desbloqueadas',
            'aceite_privacidade_versao', 'aceite_privacidade_em',
            'consentimento_revogado_em', 'anonimizado_em',
            'responsavel',
            'aceite_versao', 'aceite_termos',
        )
        read_only_fields = (
            'id', 'criado_em', 'nivel', 'progresso_nivel', 'streak',
            'aceite_privacidade_versao', 'aceite_privacidade_em',
            'consentimento_revogado_em', 'anonimizado_em',
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

    def get_streak(self, obj) -> dict:
        return {
            'atual': obj.streak_dias,
            'recorde': obj.maior_streak,
            'concluiu_hoje': obj.ultimo_dia_estudo == timezone.localdate(),
            'ultimo_dia': obj.ultimo_dia_estudo,
        }

    def get_conquistas_desbloqueadas(self, obj) -> int:
        return obj.conquistas_usuario.count()

    def get_interesses(self, obj):
        interesses = Interesse.objects.filter(usuarios_interessados__usuario=obj)
        return InteresseSerializer(interesses, many=True).data

    def validate(self, attrs):
        if self.instance is None and not attrs.get('password'):
            raise serializers.ValidationError({'password': 'This field is required.'})

        idade = attrs.get('idade', self.instance.idade if self.instance else None)

        if self.instance is None and idade is None:
            raise serializers.ValidationError({'idade': 'Informe a idade.'})

        if self.instance is not None and 'idade' in attrs and idade is None:
            raise serializers.ValidationError({'idade': 'Informe a idade.'})

        responsavel = attrs.get('responsavel', serializers.empty)
        tem_aceite = (
            self.instance is not None
            and getattr(self.instance, 'aceite_responsavel', None) is not None
        )

        if idade is not None and idade < 18:
            if responsavel is serializers.empty and not tem_aceite:
                raise serializers.ValidationError(
                    {'responsavel': MENSAGEM_MENOR_SEM_RESPONSAVEL}
                )
        elif responsavel not in (serializers.empty, None):
            raise serializers.ValidationError({
                'responsavel': (
                    'Dados do responsável só são necessários para menores de 18 anos.'
                )
            })

        return attrs

    def create(self, validated_data):
        validated_data.pop('interesses_ids', None)
        aceite_termos = validated_data.pop('aceite_termos', False)
        aceite_versao = validated_data.pop('aceite_versao', None)
        responsavel = validated_data.pop('responsavel', None)
        password = validated_data.pop('password')
        versao_termos = aceite_versao or getattr(settings, 'TERMOS_DE_USO_VERSAO', '1.1')

        with transaction.atomic():
            user = User(**validated_data)
            if aceite_termos:
                user.aceite_privacidade_versao = versao_termos
                user.aceite_privacidade_em = timezone.now()
                user.consentimento_revogado_em = None
            user.set_password(password)
            user.save()
            if responsavel:
                AceiteResponsavel.objects.create(usuario=user, **responsavel)
        return user

    def update(self, instance, validated_data):
        interesses_ids = validated_data.pop('interesses_ids', None)
        validated_data.pop('aceite_termos', None)
        aceite_versao = validated_data.pop('aceite_versao', None)
        responsavel = validated_data.pop('responsavel', None)
        password = validated_data.pop('password', None)
        if password is not None:
            raise serializers.ValidationError({
                'password': 'Use POST /api/users/me/alterar-senha/ para alterar a senha.'
            })

        with transaction.atomic():
            for field, value in validated_data.items():
                setattr(instance, field, value)

            if aceite_versao:
                instance.aceite_privacidade_versao = aceite_versao
                instance.aceite_privacidade_em = timezone.now()
                instance.consentimento_revogado_em = None

            instance.save()

            if responsavel:
                AceiteResponsavel.objects.update_or_create(
                    usuario=instance,
                    defaults=responsavel,
                )

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


class SolicitacaoRevisaoSerializer(serializers.ModelSerializer):
    prazo_resposta = serializers.SerializerMethodField()

    class Meta:
        model = SolicitacaoRevisao
        fields = (
            'id', 'tipo', 'referencia_id', 'status',
            'criado_em', 'respondido_em', 'resposta', 'prazo_resposta',
        )
        read_only_fields = ('id', 'criado_em', 'respondido_em', 'resposta')

    def get_prazo_resposta(self, obj):
        dias = getattr(settings, 'LGPD_SLA_REVISAO_DIAS', 15)
        return obj.criado_em + timedelta(days=dias)


class SolicitacaoRevisaoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitacaoRevisao
        fields = ('tipo', 'referencia_id')


class SolicitacaoRevisaoAdminSerializer(serializers.ModelSerializer):
    prazo_resposta = serializers.SerializerMethodField()

    class Meta:
        model = SolicitacaoRevisao
        fields = ('status', 'resposta', 'prazo_resposta')

    def get_prazo_resposta(self, obj):
        dias = getattr(settings, 'LGPD_SLA_REVISAO_DIAS', 15)
        return obj.criado_em + timedelta(days=dias)


class ChangePasswordSerializer(serializers.Serializer):
    senha_atual = serializers.CharField(write_only=True)
    nova_senha = serializers.CharField(write_only=True)

    def validate_nova_senha(self, value):
        from django.contrib.auth.password_validation import validate_password
        validate_password(value, self.context.get('user'))
        return value


class DiagnosticoPedagogicoSerializer(serializers.Serializer):
    """Raio-X de aprendizado do estudante (VAR-126), lido da memória pedagógica (VAR-118)."""

    pontos_fortes = serializers.ListField(
        child=serializers.CharField(),
        help_text='Tópicos (módulos) em que o estudante demonstra domínio.',
    )
    topicos_dificuldade = serializers.ListField(
        child=serializers.CharField(),
        help_text='Tópicos (módulos) com erros recorrentes, a praticar.',
    )
    taxa_acerto_geral = serializers.FloatField(
        help_text='Percentual de acerto em todas as questões avaliadas (0 a 100).',
    )
    total_atividades_avaliadas = serializers.IntegerField(
        help_text='Quantidade de atividades com questões consideradas no diagnóstico.',
    )
    ultima_atualizacao = serializers.DateTimeField(
        allow_null=True,
        help_text='Data da última consolidação da memória; null se ainda não houver.',
    )


class EventoAuditoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventoAuditoria
        fields = (
            'id', 'usuario', 'ator_email', 'ator_is_staff', 'acao',
            'metodo', 'rota', 'status_code', 'resultado', 'recurso',
            'recurso_id', 'ip_hash', 'user_agent', 'metadata', 'criado_em',
        )
        read_only_fields = fields


class ConquistaUsuarioSerializer(serializers.ModelSerializer):
    """Conquista do catálogo com o status de desbloqueio do usuário autenticado.

    Espera no contexto ``desbloqueios``: dict {conquista_id: datetime}.
    """

    desbloqueada = serializers.SerializerMethodField()
    desbloqueada_em = serializers.SerializerMethodField()

    class Meta:
        model = Conquista
        fields = (
            'id', 'codigo', 'titulo', 'descricao', 'categoria', 'icone',
            'xp_recompensa', 'ordem', 'desbloqueada', 'desbloqueada_em',
        )
        read_only_fields = fields

    def _data_desbloqueio(self, obj):
        return self.context.get('desbloqueios', {}).get(obj.pk)

    def get_desbloqueada(self, obj) -> bool:
        return self._data_desbloqueio(obj) is not None

    def get_desbloqueada_em(self, obj):
        data = self._data_desbloqueio(obj)
        return serializers.DateTimeField().to_representation(data) if data else None


class ItemInventarioSerializer(serializers.ModelSerializer):
    """Item cosmético do catálogo com o status de posse do usuário autenticado.

    Espera no contexto ``registros``: dict {item_id: UsuarioInventario}.
    ``id`` é o id do registro de inventário (usado para equipar) e é ``None``
    quando o item ainda não foi desbloqueado.
    """

    id = serializers.SerializerMethodField()
    item_id = serializers.UUIDField(source='pk', read_only=True)
    desbloqueado = serializers.SerializerMethodField()
    equipado = serializers.SerializerMethodField()
    desbloqueado_em = serializers.SerializerMethodField()

    class Meta:
        model = ItemCosmetico
        fields = (
            'id', 'item_id', 'nome', 'descricao', 'tipo', 'raridade',
            'recurso_visual', 'asset_url', 'desbloqueado', 'equipado',
            'desbloqueado_em',
        )
        read_only_fields = fields

    def _registro(self, obj):
        return self.context.get('registros', {}).get(obj.pk)

    def get_id(self, obj):
        registro = self._registro(obj)
        return str(registro.pk) if registro else None

    def get_desbloqueado(self, obj) -> bool:
        return self._registro(obj) is not None

    def get_equipado(self, obj) -> bool:
        registro = self._registro(obj)
        return bool(registro and registro.equipado)

    def get_desbloqueado_em(self, obj):
        registro = self._registro(obj)
        if registro is None:
            return None
        return serializers.DateTimeField().to_representation(registro.desbloqueado_em)

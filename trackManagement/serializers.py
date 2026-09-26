from rest_framework import serializers

from .models import Trilha, Modulo, Matricula, ProgressoModulo


class TrilhaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trilha
        fields = ('id', 'titulo', 'descricao', 'habilidade', 'ativo')
        read_only_fields = ('id',)


class TrilhaPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """PrimaryKeyRelatedField que serializa o UUID como string."""

    def to_representation(self, value):
        return str(super().to_representation(value))


class ModuloSerializer(serializers.ModelSerializer):
    trilha_id = TrilhaPrimaryKeyRelatedField(
        source='trilha', queryset=Trilha.objects.all(),
    )

    class Meta:
        model = Modulo
        fields = ('id', 'trilha_id', 'titulo', 'descricao', 'nivel', 'ordem_modulo')
        read_only_fields = ('id',)


class MatriculaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Matricula
        fields = ('id', 'usuario', 'trilha', 'status', 'criado_em', 'concluido_em')
        read_only_fields = ('id', 'criado_em')

    def validate(self, attrs):
        # Prevent duplicate matricula per usuario+trilha
        usuario = attrs.get('usuario')
        trilha = attrs.get('trilha')
        if self.instance is None and usuario and trilha:
            exists = Matricula.objects.filter(usuario=usuario, trilha=trilha).exists()
            if exists:
                raise serializers.ValidationError('Usuário já matriculado nesta trilha.')
        return attrs


class ProgressoModuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressoModulo
        fields = ('id', 'matricula', 'modulo', 'status', 'concluido_em')
        read_only_fields = ('id',)


class PosicionarNivelInputSerializer(serializers.Serializer):
    matricula_id = serializers.UUIDField(required=True)


class ModuloLiberadoSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    titulo = serializers.CharField()
    nivel = serializers.CharField()
    status = serializers.CharField()


class PosicionarNivelOutputSerializer(serializers.Serializer):
    nivel_posicionado = serializers.CharField()
    taxa_acerto = serializers.FloatField()
    modulos_liberados = ModuloLiberadoSerializer(many=True)
    mensagem_assistente = serializers.CharField()


class TrilhaListaSerializer(serializers.ModelSerializer):
    total_modulos = serializers.IntegerField(read_only=True)
    total_atividades = serializers.IntegerField(read_only=True)

    class Meta:
        model = Trilha
        fields = (
            'id', 'titulo', 'descricao', 'habilidade', 'ativo',
            'total_modulos', 'total_atividades',
        )


class MatriculaCriarSerializer(serializers.Serializer):
    trilha_id = serializers.UUIDField(required=True)


class MatriculaSaidaSerializer(serializers.ModelSerializer):
    trilha_id = serializers.UUIDField(source='trilha.id', read_only=True)
    trilha_titulo = serializers.CharField(source='trilha.titulo', read_only=True)
    modulo_atual = serializers.SerializerMethodField()

    class Meta:
        model = Matricula
        fields = (
            'id', 'trilha_id', 'trilha_titulo', 'status', 'criado_em',
            'modulo_atual',
        )

    def get_modulo_atual(self, obj):
        progresso = (
            obj.progresso_modulos.select_related('modulo')
            .filter(status='EM_ANDAMENTO')
            .order_by('modulo__ordem_modulo')
            .first()
        )
        if progresso is None:
            return None
        return {
            'id': progresso.modulo.id,
            'titulo': progresso.modulo.titulo,
            'status': progresso.status,
        }


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

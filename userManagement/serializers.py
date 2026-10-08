from django.contrib.auth import get_user_model
from rest_framework import serializers

from .services import GamificationService

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    nivel = serializers.SerializerMethodField()
    progresso_nivel = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'apelido', 'nome', 'email', 'password',
            'xp_total', 'streak_dias', 'is_primeiro_acesso',
            'nivel', 'progresso_nivel',
        )
        read_only_fields = ('id', 'criado_em', 'nivel', 'progresso_nivel')

    def get_nivel(self, obj) -> int:
        return GamificationService.calcular_nivel(obj.xp_total)

    def get_progresso_nivel(self, obj) -> dict:
        return GamificationService.obter_progresso_nivel(obj.xp_total)
        extra_kwargs = {
            'apelido': {'required': True},
            'nome': {'required': True},
            'email': {'required': True},
        }

    def validate(self, attrs):
        if self.instance is None and not attrs.get('password'):
            raise serializers.ValidationError({'password': 'This field is required.'})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
    
        for field, value in validated_data.items():
            setattr(instance, field, value)
    
        if password is not None:
            instance.set_password(password)
    
        instance.save()
        return instance


class AuthSerializer(serializers.Serializer):
    apelido = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if not attrs.get('apelido') and not attrs.get('email'):
            raise serializers.ValidationError('Informe o apelido ou o email.')
        return attrs

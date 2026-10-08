from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from .models import Interesse, UsuarioInteresse

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

    class Meta:
        model = User
        fields = (
            'id', 'apelido', 'nome', 'email', 'password',
            'xp_total', 'streak_dias', 'is_primeiro_acesso',
            'sexo', 'idade', 'interesses', 'interesses_ids',
        )
        read_only_fields = ('id', 'criado_em')
        extra_kwargs = {
            'apelido': {'required': True},
            'nome': {'required': True},
            'email': {'required': True},
        }

    def get_interesses(self, obj):
        interesses = Interesse.objects.filter(usuarios_interessados__usuario=obj)
        return InteresseSerializer(interesses, many=True).data

    def validate(self, attrs):
        if self.instance is None and not attrs.get('password'):
            raise serializers.ValidationError({'password': 'This field is required.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('interesses_ids', None)
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        interesses_ids = validated_data.pop('interesses_ids', None)
        password = validated_data.pop('password', None)

        with transaction.atomic():
            for field, value in validated_data.items():
                setattr(instance, field, value)

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

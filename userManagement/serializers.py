from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'nickName', 'password')
        read_only_fields = ('id',)
        extra_kwargs = {
            'nickName': {'required': True},
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
        instance.nickName = validated_data.get('nickName', instance.nickName)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class AuthSerializer(serializers.Serializer):
    nickName = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)

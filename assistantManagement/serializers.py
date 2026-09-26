from rest_framework import serializers


class DecisaoNivelSerializer(serializers.Serializer):
    trilha_id = serializers.UUIDField(required=True)
    opcao = serializers.ChoiceField(
        choices=['TESTE_DIAGNOSTICO', 'INICIO', 'INICIAR_DO_INICIO', 'INICIAR_DO_ZERO'],
        required=True
    )


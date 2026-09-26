from rest_framework import serializers


class DecisaoNivelSerializer(serializers.Serializer):
    trilha_id = serializers.UUIDField(required=True)
    opcao = serializers.ChoiceField(
        choices=['TESTE_DIAGNOSTICO', 'INICIO', 'INICIAR_DO_INICIO', 'INICIAR_DO_ZERO'],
        required=True
    )


class EnviarMensagemInputSerializer(serializers.Serializer):
    conteudo = serializers.CharField(required=True, allow_blank=False, trim_whitespace=True)


class OpcaoTrilhaSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    titulo = serializers.CharField()
    habilidade = serializers.CharField()


class MensagemInicialSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    remetente = serializers.CharField()
    conteudo = serializers.CharField()
    sugestoes_rapidas = serializers.ListField(child=serializers.CharField())
    criada_em = serializers.DateTimeField(required=False)


class IniciarSessaoResponseSerializer(serializers.Serializer):
    sessao_id = serializers.UUIDField()
    mensagem_inicial = MensagemInicialSerializer()


class RespostaAssistenteSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    remetente = serializers.CharField()
    conteudo = serializers.CharField()
    intencao_detectada = serializers.CharField(allow_null=True)
    opcoes_trilhas = OpcaoTrilhaSerializer(many=True, required=False)
    criada_em = serializers.DateTimeField(required=False)


class EnviarMensagemResponseSerializer(serializers.Serializer):
    resposta_assistente = RespostaAssistenteSerializer()


class MensagemHistoricoSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    remetente = serializers.CharField()
    conteudo = serializers.CharField()
    intencao_detectada = serializers.CharField(allow_null=True)
    opcoes_trilhas = OpcaoTrilhaSerializer(many=True, required=False)
    criada_em = serializers.DateTimeField()


class HistoricoSessaoResponseSerializer(serializers.Serializer):
    sessao_id = serializers.UUIDField()
    total_mensagens = serializers.IntegerField()
    mensagens = MensagemHistoricoSerializer(many=True)



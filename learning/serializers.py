from django.db import transaction
from rest_framework import serializers

from activityManagement.models import Atividade, Conteudo
from questionsManagement.models import Questao, QuestaoOpcao
from trackManagement.models import Modulo


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestaoOpcao
        fields = ('id', 'texto_opcao', 'ordem')
        read_only_fields = ('id',)


class QuestionPublicSerializer(serializers.ModelSerializer):
    opcoes = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = Questao
        fields = ('id', 'tipo_exercicio', 'enunciado', 'codigo_snippet', 'ordem_questao', 'opcoes')
        read_only_fields = ('id',)


class QuestionCreateSerializer(serializers.ModelSerializer):
    opcoes = OptionSerializer(many=True, required=False)

    class Meta:
        model = Questao
        fields = (
            'id', 'tipo_exercicio', 'enunciado', 'codigo_snippet',
            'gabarito_esperado', 'explicacao', 'dica_conceitual',
            'ordem_questao', 'peso_pontuacao', 'opcoes',
        )
        read_only_fields = ('id',)


class ContentSerializer(serializers.ModelSerializer):
    titulo = serializers.CharField(required=True)
    texto_explicativo = serializers.CharField(required=True, trim_whitespace=False)
    tempo_estimado_minutos = serializers.IntegerField(required=True)

    class Meta:
        model = Conteudo
        fields = ('id', 'titulo', 'texto_explicativo', 'tempo_estimado_minutos', 'criado_em')
        read_only_fields = ('id', 'criado_em')


class ActivitySerializer(serializers.ModelSerializer):
    conteudo_teorico = ContentSerializer(source='conteudo', read_only=True)
    ordem_atividade = serializers.IntegerField(source='ordem', read_only=True)
    questoes = QuestionPublicSerializer(many=True, read_only=True)

    class Meta:
        model = Atividade
        fields = ('id', 'titulo', 'descricao', 'contexto_avaliacao', 'xp_recompensa', 'ordem_atividade', 'ativo', 'conteudo_teorico', 'questoes')
        read_only_fields = ('id', 'ativo')


class ActivityCreateSerializer(ActivitySerializer):
    modulo_id = serializers.PrimaryKeyRelatedField(source='modulo', queryset=Modulo.objects.all(), write_only=True)
    conteudo_id = serializers.PrimaryKeyRelatedField(source='conteudo', queryset=Conteudo.objects.all(), write_only=True, required=False, allow_null=True)
    ordem_atividade = serializers.IntegerField(source='ordem', write_only=True)
    questoes = QuestionCreateSerializer(many=True, required=False)

    class Meta(ActivitySerializer.Meta):
        fields = ActivitySerializer.Meta.fields + ('modulo_id', 'conteudo_id', 'ordem_atividade')

    def create(self, validated_data):
        questoes = validated_data.pop('questoes', [])
        atividade = Atividade.objects.create(**validated_data)
        for questao_data in questoes:
            opcoes = questao_data.pop('opcoes', [])
            questao = Questao.objects.create(atividade=atividade, **questao_data)
            QuestaoOpcao.objects.bulk_create([
                QuestaoOpcao(questao=questao, **opcao) for opcao in opcoes
            ])
        return atividade


class ActivitySubmissionSerializer(serializers.Serializer):
    respostas = serializers.DictField(
        child=serializers.ListField(child=serializers.CharField(allow_blank=True)),
    )


class QuestionFeedbackSerializer(serializers.Serializer):
    questao_id = serializers.UUIDField()
    correta = serializers.BooleanField()
    explicacao = serializers.CharField(allow_blank=True)


class SubmissionResultSerializer(serializers.Serializer):
    execucao_id = serializers.UUIDField(source='execution.id')
    aprovado = serializers.BooleanField(source='approved')
    taxa_acerto = serializers.FloatField(source='hit_rate')
    pontuacao_obtida = serializers.IntegerField(source='score_obtained')
    xp_concedido = serializers.IntegerField(source='xp_granted')
    novo_xp_total = serializers.IntegerField(source='new_xp_total')
    executado_em = serializers.DateTimeField(source='execution.executado_em')
    questoes_feedback = QuestionFeedbackSerializer(source='feedback', many=True)


class HintRequestSerializer(serializers.Serializer):
    sessao_id = serializers.UUIDField()
    questao_id = serializers.UUIDField()
    pergunta = serializers.CharField()


class HintResponseSerializer(serializers.Serializer):
    resposta_coach = serializers.CharField()
    origem_resposta = serializers.CharField()
    questao_id = serializers.UUIDField()


from rest_framework import serializers

from .models import Activity, Content, Module, Option, Question


class OptionSerializer(serializers.ModelSerializer):
    texto_opcao = serializers.CharField(source='text')
    ordem = serializers.IntegerField(source='order')

    class Meta:
        model = Option
        fields = ('id', 'texto_opcao', 'ordem')
        read_only_fields = ('id',)


class QuestionPublicSerializer(serializers.ModelSerializer):
    """Omits gabarito_esperado, explicacao e dica_conceitual do payload público."""

    tipo_exercicio = serializers.CharField(source='exercise_type')
    enunciado = serializers.CharField(source='statement')
    codigo_snippet = serializers.CharField(source='code_snippet', allow_null=True, required=False)
    ordem_questao = serializers.IntegerField(source='order')
    opcoes = OptionSerializer(source='options', many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'tipo_exercicio', 'enunciado', 'codigo_snippet', 'ordem_questao', 'opcoes')
        read_only_fields = ('id',)


class ContentSerializer(serializers.ModelSerializer):
    titulo = serializers.CharField(source='title')
    texto_explicativo = serializers.CharField(source='explanatory_text')
    tempo_estimado_minutos = serializers.IntegerField(source='estimated_minutes')

    class Meta:
        model = Content
        fields = ('id', 'titulo', 'texto_explicativo', 'tempo_estimado_minutos')
        read_only_fields = ('id',)


class ActivitySerializer(serializers.ModelSerializer):
    """Representação pública de Atividade e also o serializer usado no PUT.

    modulo_id/conteudo_id não aparecem aqui: são write-only e exclusivos do
    create (ver ActivityCreateSerializer), já que o PUT só atualiza os campos
    abaixo, conforme o contrato da task.
    """

    titulo = serializers.CharField(source='title')
    descricao = serializers.CharField(source='description', required=False, allow_blank=True)
    contexto_avaliacao = serializers.CharField(source='evaluation_context')
    xp_recompensa = serializers.IntegerField(source='xp_reward')
    ordem_atividade = serializers.IntegerField(source='order')
    ativo = serializers.BooleanField(source='active', read_only=True)
    conteudo_teorico = ContentSerializer(source='content', read_only=True)
    questoes = QuestionPublicSerializer(source='questions', many=True, read_only=True)

    class Meta:
        model = Activity
        fields = (
            'id',
            'titulo',
            'descricao',
            'contexto_avaliacao',
            'xp_recompensa',
            'ordem_atividade',
            'ativo',
            'conteudo_teorico',
            'questoes',
        )
        read_only_fields = ('id',)


class ActivityCreateSerializer(ActivitySerializer):
    modulo_id = serializers.PrimaryKeyRelatedField(
        source='module', queryset=Module.objects.all(), write_only=True,
    )
    conteudo_id = serializers.PrimaryKeyRelatedField(
        source='content', queryset=Content.objects.all(), write_only=True,
    )

    class Meta(ActivitySerializer.Meta):
        fields = ActivitySerializer.Meta.fields + ('modulo_id', 'conteudo_id')

from django.db import transaction
from rest_framework import serializers

from activityManagement.models import Atividade

from .models import Questao, QuestaoOpcao


TIPOS_EXERCICIO = ('MULTIPLA_ESCOLHA', 'COMPLETE_CODIGO', 'ORDENAR_BLOCOS')


class QuestaoOpcaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestaoOpcao
        fields = ('id', 'texto_opcao', 'ordem')
        read_only_fields = ('id',)


class QuestaoSerializer(serializers.ModelSerializer):
    atividade_id = serializers.UUIDField(read_only=True)
    opcoes = QuestaoOpcaoSerializer(many=True, read_only=True)
    tipo_exercicio = serializers.ChoiceField(choices=TIPOS_EXERCICIO)
    gabarito_esperado = serializers.CharField(read_only=True)

    class Meta:
        model = Questao
        fields = ('id', 'atividade_id', 'tipo_exercicio', 'enunciado', 'codigo_snippet',
                  'gabarito_esperado', 'explicacao', 'dica_conceitual', 'ordem_questao',
                  'peso_pontuacao', 'opcoes')
        read_only_fields = ('id', 'atividade_id', 'gabarito_esperado', 'opcoes')


class QuestaoCreateSerializer(QuestaoSerializer):
    atividade_id = serializers.PrimaryKeyRelatedField(
        source='atividade', queryset=Atividade.objects.all(),
        write_only=True,
    )
    gabarito_esperado = serializers.CharField(write_only=True)
    opcoes = QuestaoOpcaoSerializer(many=True, required=False)

    class Meta(QuestaoSerializer.Meta):
        fields = QuestaoSerializer.Meta.fields
        read_only_fields = ('id',)

    @transaction.atomic
    def create(self, validated_data):
        opcoes = validated_data.pop('opcoes', [])
        questao = Questao.objects.create(**validated_data)
        QuestaoOpcao.objects.bulk_create([
            QuestaoOpcao(questao=questao, **opcao) for opcao in opcoes
        ])
        return questao

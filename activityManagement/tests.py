import pytest
from model_bakery import baker

from .models import Atividade, Conteudo, ExecucaoAtividade
from learning.serializers import ActivityCreateSerializer
from trackManagement.models import Modulo


@pytest.mark.django_db
def test_atividade_pertence_a_modulo():
    modulo = baker.make(Modulo)
    atividade = baker.make(Atividade, modulo=modulo)

    assert atividade.modulo == modulo
    assert list(modulo.atividades.all()) == [atividade]


@pytest.mark.django_db
def test_execucao_atividade_relaciona_com_atividade():
    atividade = baker.make(Atividade)

    execucao = baker.make(
        ExecucaoAtividade,
        atividade=atividade,
        resposta={'resposta': 'ok'},
    )

    assert execucao.atividade == atividade
    assert execucao in atividade.execucoes.all()


@pytest.mark.django_db
def test_excluir_modulo_exclui_atividades_em_cascata():
    modulo = baker.make(Modulo)
    atividade = baker.make(Atividade, modulo=modulo)

    modulo.delete()

    assert not Atividade.objects.filter(pk=atividade.pk).exists()


@pytest.mark.django_db
def test_atividade_respeita_ordem():
    modulo = baker.make(Modulo)
    segunda = baker.make(Atividade, modulo=modulo, ordem=2)
    primeira = baker.make(Atividade, modulo=modulo, ordem=1)

    assert list(modulo.atividades.all()) == [primeira, segunda]


@pytest.mark.django_db
def test_atividade_pode_ser_criada_sem_conteudo():
    modulo = baker.make(Modulo)
    atividade = baker.make(Atividade, modulo=modulo, conteudo=None)
    assert atividade.conteudo is None


@pytest.mark.django_db
def test_excluir_conteudo_preserva_atividade():
    modulo = baker.make(Modulo)
    conteudo = baker.make(Conteudo)
    atividade = baker.make(Atividade, modulo=modulo, conteudo=conteudo)
    conteudo.delete()
    atividade.refresh_from_db()
    assert atividade.conteudo is None


@pytest.mark.django_db
def test_serializer_de_atividade_nao_exige_conteudo_id():
    modulo = baker.make(Modulo)
    serializer = ActivityCreateSerializer(data={
        'modulo_id': modulo.pk,
        'titulo': 'Atividade sem conteudo',
        'descricao': 'Descricao',
        'contexto_avaliacao': 'CODIGO',
        'xp_recompensa': 10,
        'ordem_atividade': 1,
    })
    assert serializer.is_valid(), serializer.errors
    atividade = serializer.save()
    assert atividade.conteudo is None

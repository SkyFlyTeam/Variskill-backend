import pytest
from model_bakery import baker

from .models import Atividade, ExecucaoAtividade, Modulo


@pytest.mark.django_db
def test_atividade_pertence_a_modulo():
    modulo = baker.make(Modulo)
    atividade = baker.make(Atividade, modulo=modulo)

    assert atividade.modulo == modulo
    assert list(modulo.atividades.all()) == [atividade]


@pytest.mark.django_db
def test_execucao_atividade_relaciona_usuario_e_atividade(django_user_model):
    usuario = baker.make(django_user_model)
    atividade = baker.make(Atividade)

    execucao = baker.make(
        ExecucaoAtividade,
        usuario=usuario,
        atividade=atividade,
        resposta={'resposta': 'ok'},
    )

    assert execucao.usuario == usuario
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

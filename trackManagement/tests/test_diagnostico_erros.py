import uuid

import pytest
from model_bakery import baker
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from activityManagement.models import Atividade, ExecucaoAtividade, RespostaQuestao
from questionsManagement.models import Questao
from trackManagement.models import Modulo, Trilha

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_user(django_user_model):
    return baker.make(django_user_model, apelido='estudante_diagnostico')


@pytest.fixture
def outro_usuario(django_user_model):
    return baker.make(django_user_model, apelido='outro_estudante_diagnostico')


@pytest.fixture
def modulo():
    trilha = Trilha.objects.create(titulo='Trilha Python', habilidade='Backend', ativo=True)
    return Modulo.objects.create(
        trilha=trilha, titulo='Módulo 1', nivel='INICIANTE', ordem_modulo=1,
    )


def make_atividade(modulo, ordem=1):
    return baker.make(Atividade, modulo=modulo, ordem=ordem, ativo=True)


def make_questao(atividade, ordem=1, dica='Revise o conceito de tipagem.', explicacao='Explicação padrão.'):
    return baker.make(
        Questao, atividade=atividade, ordem_questao=ordem,
        dica_conceitual=dica, explicacao=explicacao,
    )


def make_execucao(usuario, atividade, respostas, **kwargs):
    """Cria uma ExecucaoAtividade e suas RESPOSTA_QUESTAO (lista de (questao, correta))."""
    execucao = baker.make(
        ExecucaoAtividade, usuario=usuario, atividade=atividade,
        resposta={}, aprovado=kwargs.get('aprovado', False),
        pontuacao_obtida=kwargs.get('pontuacao_obtida', 0),
    )
    if kwargs.get('executado_em'):
        ExecucaoAtividade.objects.filter(pk=execucao.pk).update(executado_em=kwargs['executado_em'])
        execucao.refresh_from_db()
    RespostaQuestao.objects.bulk_create([
        RespostaQuestao(execucao=execucao, questao=questao, resposta_fornecida='[]', correta=correta)
        for questao, correta in respostas
    ])
    return execucao


def chamar_diagnostico(api_client, user, modulo_id):
    api_client.force_authenticate(user=user)
    return api_client.get(reverse('progresso-diagnostico-erros'), {'modulo_id': str(modulo_id)})


def test_requer_autenticacao(api_client, modulo):
    response = api_client.get(reverse('progresso-diagnostico-erros'), {'modulo_id': str(modulo.id)})

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_modulo_id_obrigatorio(api_client, auth_user):
    api_client.force_authenticate(user=auth_user)

    response = api_client.get(reverse('progresso-diagnostico-erros'))

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_modulo_inexistente_retorna_404(api_client, auth_user):
    response = chamar_diagnostico(api_client, auth_user, uuid.uuid4())

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_sem_execucoes_devolve_zerado_com_parecer_proprio(api_client, auth_user, modulo):
    response = chamar_diagnostico(api_client, auth_user, modulo.id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['total_respondidas'] == 0
    assert response.data['total_acertos'] == 0
    assert response.data['taxa_acerto'] == 0.0
    assert response.data['questoes_erradas'] == []
    assert 'ainda não respondeu' in response.data['parecer']


def test_taxa_abaixo_de_70_por_cento_calcula_corretamente_e_gera_parecer_de_revisao(api_client, auth_user, modulo):
    atividade = make_atividade(modulo)
    q1, q2, q3 = (make_questao(atividade, ordem=i) for i in range(1, 4))
    make_execucao(auth_user, atividade, [(q1, True), (q2, True), (q3, False)])

    response = chamar_diagnostico(api_client, auth_user, modulo.id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['total_respondidas'] == 3
    assert response.data['total_acertos'] == 2
    assert response.data['taxa_acerto'] == pytest.approx(66.7)
    assert 'abaixo do esperado' in response.data['parecer']


def test_taxa_igual_ou_acima_de_70_por_cento_com_erro_cita_ponto_de_atencao(api_client, auth_user, modulo):
    atividade = make_atividade(modulo)
    questoes = [make_questao(atividade, ordem=i, dica=f'conceito-{i}') for i in range(1, 11)]
    respostas = [(q, idx < 7) for idx, q in enumerate(questoes)]  # 7 de 10 = 70%
    make_execucao(auth_user, atividade, respostas)

    response = chamar_diagnostico(api_client, auth_user, modulo.id)

    assert response.data['taxa_acerto'] == 70.0
    assert len(response.data['questoes_erradas']) == 3
    assert 'domínio sólido' in response.data['parecer']
    assert 'ponto de atenção' in response.data['parecer']
    assert 'conceito-8' in response.data['parecer']


def test_taxa_abaixo_de_70_por_cento_gera_parecer_de_revisao_com_conceitos_errados(api_client, auth_user, modulo):
    atividade = make_atividade(modulo)
    q1 = make_questao(atividade, ordem=1, dica='Mutabilidade de listas')
    q2 = make_questao(atividade, ordem=2, dica='Escopo de variáveis')
    make_execucao(auth_user, atividade, [(q1, False), (q2, False)])

    response = chamar_diagnostico(api_client, auth_user, modulo.id)

    assert response.data['taxa_acerto'] == 0.0
    assert len(response.data['questoes_erradas']) == 2
    assert 'abaixo do esperado' in response.data['parecer']
    assert 'Mutabilidade de listas' in response.data['parecer']
    assert 'Escopo de variáveis' in response.data['parecer']


def test_questao_errada_usa_explicacao_quando_falta_dica_conceitual(api_client, auth_user, modulo):
    atividade = make_atividade(modulo)
    questao = make_questao(atividade, dica='', explicacao='Use type() para checar o tipo.')
    make_execucao(auth_user, atividade, [(questao, False)])

    response = chamar_diagnostico(api_client, auth_user, modulo.id)

    assert response.data['questoes_erradas'][0]['dica_conceitual'] == ''
    assert 'Use type() para checar o tipo.' in response.data['parecer']


def test_considera_apenas_a_ultima_execucao_de_cada_atividade(api_client, auth_user, modulo):
    atividade = make_atividade(modulo)
    questao = make_questao(atividade)
    from django.utils import timezone
    from datetime import timedelta

    make_execucao(
        auth_user, atividade, [(questao, False)],
        executado_em=timezone.now() - timedelta(hours=1),
    )
    make_execucao(auth_user, atividade, [(questao, True)])

    response = chamar_diagnostico(api_client, auth_user, modulo.id)

    assert response.data['total_respondidas'] == 1
    assert response.data['total_acertos'] == 1
    assert response.data['questoes_erradas'] == []


def test_nao_mistura_execucoes_de_outro_usuario(api_client, auth_user, outro_usuario, modulo):
    atividade = make_atividade(modulo)
    questao = make_questao(atividade)
    make_execucao(outro_usuario, atividade, [(questao, False)])

    response = chamar_diagnostico(api_client, auth_user, modulo.id)

    assert response.data['total_respondidas'] == 0


def test_nao_mistura_execucoes_de_outro_modulo(api_client, auth_user, modulo):
    outra_trilha_modulo = Modulo.objects.create(
        trilha=modulo.trilha, titulo='Módulo 2', nivel='INTERMEDIARIO', ordem_modulo=2,
    )
    atividade_outro_modulo = make_atividade(outra_trilha_modulo)
    questao_outro_modulo = make_questao(atividade_outro_modulo)
    make_execucao(auth_user, atividade_outro_modulo, [(questao_outro_modulo, False)])

    response = chamar_diagnostico(api_client, auth_user, modulo.id)

    assert response.data['total_respondidas'] == 0

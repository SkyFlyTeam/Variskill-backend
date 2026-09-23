import uuid
from model_bakery import baker
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from activityManagement.models import Atividade, ExecucaoAtividade
from learning.models import Module
from questionsManagement.models import Questao
from trackManagement.models import Matricula, Modulo, ProgressoModulo, Trilha

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_user(django_user_model):
    return baker.make(django_user_model, apelido='estudante_teste')


@pytest.fixture
def other_user(django_user_model):
    return baker.make(django_user_model, apelido='outro_estudante')


@pytest.fixture
def learning_module():
    return Module.objects.create(title='Modulo Base')


@pytest.fixture
def trilha_completa():
    trilha = Trilha.objects.create(
        titulo='Trilha de Python',
        descricao='Aprenda Python do zero ao avançado',
        habilidade='Backend',
        ativo=True,
    )
    # Criar módulos em 3 níveis
    m_ini1 = Modulo.objects.create(
        trilha=trilha,
        titulo='Módulo 1 - Fundamentos',
        descricao='Conceitos básicos',
        nivel='INICIANTE',
        ordem_modulo=1,
    )
    m_ini2 = Modulo.objects.create(
        trilha=trilha,
        titulo='Módulo 1.1 - Tipos de Dados',
        descricao='Strings e números',
        nivel='INICIANTE',
        ordem_modulo=2,
    )
    m_inter1 = Modulo.objects.create(
        trilha=trilha,
        titulo='Módulo 2 - Estruturas de Controle',
        descricao='Loops e condicionais',
        nivel='INTERMEDIARIO',
        ordem_modulo=3,
    )
    m_inter2 = Modulo.objects.create(
        trilha=trilha,
        titulo='Módulo 2.1 - Funções e Módulos',
        descricao='Funções avançadas',
        nivel='INTERMEDIARIO',
        ordem_modulo=4,
    )
    m_avanc1 = Modulo.objects.create(
        trilha=trilha,
        titulo='Módulo 3 - Orientação a Objetos Avançada',
        descricao='Classes e metaprogramação',
        nivel='AVANCADO',
        ordem_modulo=5,
    )
    return {
        'trilha': trilha,
        'm_ini1': m_ini1,
        'm_ini2': m_ini2,
        'm_inter1': m_inter1,
        'm_inter2': m_inter2,
        'm_avanc1': m_avanc1,
    }


@pytest.fixture
def atividade_diagnostica(learning_module):
    return Atividade.objects.create(
        modulo=learning_module,
        titulo='Diagnóstico Inicial de Python',
        descricao='Avaliação para nivelamento',
        contexto_avaliacao='DIAGNOSTICO_INICIAL',
        ordem=1,
        ativo=True,
    )


def test_posicionar_nivel_requer_autenticacao(api_client, atividade_diagnostica):
    url = reverse('diagnostico-posicionar-nivel', kwargs={'atividade_id': atividade_diagnostica.id})
    response = api_client.post(url, {'matricula_id': str(uuid.uuid4())}, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_posicionar_nivel_atividade_inexistente(api_client, auth_user):
    api_client.force_login(auth_user)
    url = reverse('diagnostico-posicionar-nivel', kwargs={'atividade_id': uuid.uuid4()})
    response = api_client.post(url, {'matricula_id': str(uuid.uuid4())}, format='json')
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_posicionar_nivel_rejeita_atividade_que_nao_e_diagnostico_inicial(
    api_client, auth_user, learning_module, trilha_completa
):
    api_client.force_login(auth_user)
    atividade_comum = Atividade.objects.create(
        modulo=learning_module,
        titulo='Exercício de Fixação',
        descricao='Atividade normal',
        contexto_avaliacao='FIXACAO',
        ordem=2,
        ativo=True,
    )
    matricula = Matricula.objects.create(usuario=auth_user, trilha=trilha_completa['trilha'])

    url = reverse('diagnostico-posicionar-nivel', kwargs={'atividade_id': atividade_comum.id})
    response = api_client.post(url, {'matricula_id': str(matricula.id)}, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "DIAGNOSTICO_INICIAL" in response.data['detail']


def test_posicionar_nivel_rejeita_matricula_inexistente(
    api_client, auth_user, atividade_diagnostica
):
    api_client.force_login(auth_user)
    url = reverse('diagnostico-posicionar-nivel', kwargs={'atividade_id': atividade_diagnostica.id})
    response = api_client.post(url, {'matricula_id': str(uuid.uuid4())}, format='json')

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_posicionar_nivel_rejeita_matricula_de_outro_usuario(
    api_client, auth_user, other_user, atividade_diagnostica, trilha_completa
):
    matricula_outro = Matricula.objects.create(usuario=other_user, trilha=trilha_completa['trilha'])
    api_client.force_login(auth_user)

    url = reverse('diagnostico-posicionar-nivel', kwargs={'atividade_id': atividade_diagnostica.id})
    response = api_client.post(url, {'matricula_id': str(matricula_outro.id)}, format='json')

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_posicionar_nivel_rejeita_quando_usuario_nao_tem_execucao(
    api_client, auth_user, atividade_diagnostica, trilha_completa
):
    matricula = Matricula.objects.create(usuario=auth_user, trilha=trilha_completa['trilha'])
    api_client.force_login(auth_user)

    url = reverse('diagnostico-posicionar-nivel', kwargs={'atividade_id': atividade_diagnostica.id})
    response = api_client.post(url, {'matricula_id': str(matricula.id)}, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Nenhuma execução diagnóstica' in response.data['detail']


def test_posicionamento_iniciante_taxa_menor_que_70(
    api_client, auth_user, atividade_diagnostica, trilha_completa
):
    matricula = Matricula.objects.create(usuario=auth_user, trilha=trilha_completa['trilha'])
    # Execução com 60% de acerto
    ExecucaoAtividade.objects.create(
        usuario=auth_user,
        atividade=atividade_diagnostica,
        resposta={'q1': ['opt1']},
        pontuacao_obtida=60,
        aprovado=False,
    )
    api_client.force_login(auth_user)

    url = reverse('diagnostico-posicionar-nivel', kwargs={'atividade_id': atividade_diagnostica.id})
    response = api_client.post(url, {'matricula_id': str(matricula.id)}, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['nivel_posicionado'] == 'INICIANTE'
    assert response.data['taxa_acerto'] == 60.0
    assert len(response.data['modulos_liberados']) == 1
    assert response.data['modulos_liberados'][0]['id'] == str(trilha_completa['m_ini1'].id)
    assert response.data['modulos_liberados'][0]['status'] == 'EM_ANDAMENTO'
    assert 'Iniciante' in response.data['mensagem_assistente']

    # Verificar banco: PROGRESSO_MODULO
    p_ini1 = ProgressoModulo.objects.get(matricula=matricula, modulo=trilha_completa['m_ini1'])
    assert p_ini1.status == 'EM_ANDAMENTO'

    p_ini2 = ProgressoModulo.objects.get(matricula=matricula, modulo=trilha_completa['m_ini2'])
    assert p_ini2.status == 'BLOQUEADO'

    p_inter1 = ProgressoModulo.objects.get(matricula=matricula, modulo=trilha_completa['m_inter1'])
    assert p_inter1.status == 'BLOQUEADO'

    p_avanc1 = ProgressoModulo.objects.get(matricula=matricula, modulo=trilha_completa['m_avanc1'])
    assert p_avanc1.status == 'BLOQUEADO'


def test_posicionamento_intermediario_taxa_entre_70_e_85(
    api_client, auth_user, atividade_diagnostica, trilha_completa
):
    matricula = Matricula.objects.create(usuario=auth_user, trilha=trilha_completa['trilha'])
    # Adicionar 10 questões de peso 10 para apuração real (total 100)
    for i in range(10):
        Questao.objects.create(
            atividade=atividade_diagnostica,
            enunciado=f'Questão {i}',
            tipo_exercicio='MULTIPLA_ESCOLHA',
            peso_pontuacao=10,
            ordem_questao=i + 1,
        )

    # Execução com 78.5 pontos aproximado (80 pontos obtidos -> 80.0%)
    ExecucaoAtividade.objects.create(
        usuario=auth_user,
        atividade=atividade_diagnostica,
        resposta={},
        pontuacao_obtida=80,
        aprovado=True,
    )
    api_client.force_login(auth_user)

    url = reverse('diagnostico-posicionar-nivel', kwargs={'atividade_id': atividade_diagnostica.id})
    response = api_client.post(url, {'matricula_id': str(matricula.id)}, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['nivel_posicionado'] == 'INTERMEDIARIO'
    assert response.data['taxa_acerto'] == 80.0
    assert len(response.data['modulos_liberados']) == 1
    assert response.data['modulos_liberados'][0]['id'] == str(trilha_completa['m_inter1'].id)
    assert response.data['modulos_liberados'][0]['status'] == 'EM_ANDAMENTO'
    assert 'Intermediário' in response.data['mensagem_assistente']

    # Módulos de nível anterior (INICIANTE) dispensados como CONCLUIDO
    p_ini1 = ProgressoModulo.objects.get(matricula=matricula, modulo=trilha_completa['m_ini1'])
    assert p_ini1.status == 'CONCLUIDO'
    assert p_ini1.concluido_em is not None

    p_ini2 = ProgressoModulo.objects.get(matricula=matricula, modulo=trilha_completa['m_ini2'])
    assert p_ini2.status == 'CONCLUIDO'

    # Primeiro intermediário liberado
    p_inter1 = ProgressoModulo.objects.get(matricula=matricula, modulo=trilha_completa['m_inter1'])
    assert p_inter1.status == 'EM_ANDAMENTO'

    # Subsequentes intermediários e avançados bloqueados
    p_inter2 = ProgressoModulo.objects.get(matricula=matricula, modulo=trilha_completa['m_inter2'])
    assert p_inter2.status == 'BLOQUEADO'

    p_avanc1 = ProgressoModulo.objects.get(matricula=matricula, modulo=trilha_completa['m_avanc1'])
    assert p_avanc1.status == 'BLOQUEADO'


def test_posicionamento_avancado_taxa_maior_ou_igual_a_85(
    api_client, auth_user, atividade_diagnostica, trilha_completa
):
    matricula = Matricula.objects.create(usuario=auth_user, trilha=trilha_completa['trilha'])
    # Execução com 95% de acerto
    ExecucaoAtividade.objects.create(
        usuario=auth_user,
        atividade=atividade_diagnostica,
        resposta={},
        pontuacao_obtida=95,
        aprovado=True,
    )
    api_client.force_login(auth_user)

    url = reverse('diagnostico-posicionar-nivel', kwargs={'atividade_id': atividade_diagnostica.id})
    response = api_client.post(url, {'matricula_id': str(matricula.id)}, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['nivel_posicionado'] == 'AVANCADO'
    assert response.data['taxa_acerto'] == 95.0
    assert len(response.data['modulos_liberados']) == 1
    assert response.data['modulos_liberados'][0]['id'] == str(trilha_completa['m_avanc1'].id)
    assert response.data['modulos_liberados'][0]['status'] == 'EM_ANDAMENTO'
    assert 'Avançado' in response.data['mensagem_assistente']

    # Módulos iniciantes e intermediários todos concluídos
    for mod_key in ['m_ini1', 'm_ini2', 'm_inter1', 'm_inter2']:
        prog = ProgressoModulo.objects.get(matricula=matricula, modulo=trilha_completa[mod_key])
        assert prog.status == 'CONCLUIDO'

    # Módulo avançado liberado
    p_avanc1 = ProgressoModulo.objects.get(matricula=matricula, modulo=trilha_completa['m_avanc1'])
    assert p_avanc1.status == 'EM_ANDAMENTO'


def test_posicionamento_idempotente_atualiza_registros_pre_existentes(
    api_client, auth_user, atividade_diagnostica, trilha_completa
):
    matricula = Matricula.objects.create(usuario=auth_user, trilha=trilha_completa['trilha'])
    # Criar progresso prévio com status inicial qualquer
    ProgressoModulo.objects.create(matricula=matricula, modulo=trilha_completa['m_ini1'], status='BLOQUEADO')
    ProgressoModulo.objects.create(matricula=matricula, modulo=trilha_completa['m_inter1'], status='BLOQUEADO')

    ExecucaoAtividade.objects.create(
        usuario=auth_user,
        atividade=atividade_diagnostica,
        resposta={},
        pontuacao_obtida=75,
        aprovado=True,
    )
    api_client.force_login(auth_user)

    url = reverse('diagnostico-posicionar-nivel', kwargs={'atividade_id': atividade_diagnostica.id})
    response = api_client.post(url, {'matricula_id': str(matricula.id)}, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['nivel_posicionado'] == 'INTERMEDIARIO'

    p_ini1 = ProgressoModulo.objects.get(matricula=matricula, modulo=trilha_completa['m_ini1'])
    assert p_ini1.status == 'CONCLUIDO'

    p_inter1 = ProgressoModulo.objects.get(matricula=matricula, modulo=trilha_completa['m_inter1'])
    assert p_inter1.status == 'EM_ANDAMENTO'

import pytest
from rest_framework.test import APIClient

from activityManagement.models import Atividade, Conteudo
from trackManagement.models import Matricula, Modulo, ProgressoModulo, Trilha


pytestmark = pytest.mark.django_db


def make_user(django_user_model, apelido='roadmap-user'):
    return django_user_model.objects.create_user(
        apelido=apelido,
        nome='Roadmap User',
        email=f'{apelido}@example.com',
    )


def make_module(trilha, **kwargs):
    return Modulo.objects.create(trilha=trilha, **kwargs)


def make_activity(module, **kwargs):
    return Atividade.objects.create(modulo=module, **kwargs)


def test_roadmap_returns_progress_and_next_activity(django_user_model):
    user = make_user(django_user_model)
    trilha = Trilha.objects.create(titulo='Javascript', habilidade='Frontend')
    modulo = make_module(trilha, titulo='Fundamentos', nivel='INICIANTE', ordem_modulo=1)
    conteudo = Conteudo.objects.create(titulo='Variáveis')
    concluida = make_activity(
        modulo, titulo='Variáveis', contexto_avaliacao='FIXACAO_CONCEITO',
        xp_recompensa=50, ordem=1, conteudo=conteudo,
    )
    proxima = make_activity(
        modulo, titulo='Operadores', contexto_avaliacao='FIXACAO_CONCEITO',
        xp_recompensa=50, ordem=2,
    )
    matricula = Matricula.objects.create(usuario=user, trilha=trilha)
    ProgressoModulo.objects.create(matricula=matricula, modulo=modulo, status='EM_ANDAMENTO')
    concluida.execucoes.create(
        usuario=user, resposta={}, pontuacao_obtida=10, aprovado=True,
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get(f'/api/trilhas/{trilha.pk}/roadmap/')

    assert response.status_code == 200
    body = response.json()
    assert body['percentual_conclusao'] == 50.0
    assert body['modulos'][0]['status'] == 'EM_ANDAMENTO'
    assert body['modulos'][0]['atividades'][0]['status'] == 'CONCLUIDO'
    assert body['modulos'][0]['atividades'][0]['conteudo_teorico'] == {
        'id': str(conteudo.pk), 'titulo': 'Variáveis',
    }
    assert body['modulos'][0]['atividades'][1]['status'] == 'EM_ANDAMENTO'
    assert body['proxima_atividade_recomendada'] == {
        'id': str(proxima.pk), 'titulo': 'Operadores', 'modulo_id': str(modulo.pk),
    }


def test_roadmap_does_not_return_inactive_activities(django_user_model):
    user = make_user(django_user_model, 'roadmap-inactive')
    trilha = Trilha.objects.create(titulo='Python', habilidade='Backend')
    modulo = make_module(trilha, titulo='Base', nivel='INICIANTE')
    make_activity(
        modulo, titulo='Ativa', contexto_avaliacao='CODIGO', ordem=1, ativo=True,
    )
    make_activity(
        modulo, titulo='Inativa', contexto_avaliacao='CODIGO', ordem=2, ativo=False,
    )
    matricula = Matricula.objects.create(usuario=user, trilha=trilha)
    ProgressoModulo.objects.create(matricula=matricula, modulo=modulo, status='EM_ANDAMENTO')

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get(f'/api/trilhas/{trilha.pk}/roadmap/')

    assert response.status_code == 200
    assert [item['titulo'] for item in response.json()['modulos'][0]['atividades']] == ['Ativa']


def test_roadmap_without_active_enrollment_locks_all_nodes(django_user_model):
    user = make_user(django_user_model, 'roadmap-no-enrollment')
    trilha = Trilha.objects.create(titulo='CSS', habilidade='Frontend')
    modulo = make_module(trilha, titulo='Seletores', nivel='INICIANTE')
    make_activity(modulo, titulo='Classes', contexto_avaliacao='CONCEITO', ordem=1)

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get(f'/api/trilhas/{trilha.pk}/roadmap/')

    assert response.status_code == 200
    body = response.json()
    assert body['modulos'][0]['status'] == 'BLOQUEADO'
    assert body['modulos'][0]['atividades'][0]['status'] == 'BLOQUEADO'
    assert body['proxima_atividade_recomendada'] is None

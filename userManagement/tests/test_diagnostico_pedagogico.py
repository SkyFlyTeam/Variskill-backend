import pytest
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from model_bakery import baker

from assistantManagement.models import MemoriaPedagogicaUsuario

pytestmark = [pytest.mark.integration, pytest.mark.django_db]

URL = '/api/users/me/diagnostico-pedagogico/'
TOPICO_PRATICAR = {
    'topico': 'List Comprehension',
    'trilha_id': '8f6c1a2e-3b4d-4c5e-9f60-718293a4b5c6',
    'atividade_id': '1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d',
}


@pytest.fixture
def user(django_user_model):
    return baker.make(
        django_user_model,
        apelido='alice',
        nome='Alice',
        email='alice@example.com',
        password=make_password('test-password-123'),
    )


@pytest.fixture
def memoria(user):
    return MemoriaPedagogicaUsuario.objects.create(
        usuario=user,
        pontos_fortes=['Estruturas Condicionais', 'Operadores Lógicos'],
        topicos_dificuldade=['List Comprehension', 'Funções Lambda'],
        topicos_praticar=[TOPICO_PRATICAR],
        taxa_acerto_geral=78.5,
        total_atividades_avaliadas=14,
    )


def test_rota_registrada_em_users_me():
    assert reverse('diagnostico-pedagogico') == URL


def test_exige_autenticacao(client):
    response = client.get(URL)

    assert response.status_code == 403


def test_usuario_sem_historico_recebe_payload_padrao(client, user):
    client.force_login(user)

    response = client.get(URL)

    assert response.status_code == 200
    assert response.json() == {
        'pontos_fortes': [],
        'topicos_dificuldade': [],
        'topicos_praticar': [],
        'taxa_acerto_geral': 0.0,
        'total_atividades_avaliadas': 0,
        'ultima_atualizacao': None,
    }


def test_retorna_memoria_consolidada_do_usuario(client, user, memoria):
    client.force_login(user)

    response = client.get(URL)

    assert response.status_code == 200
    data = response.json()
    assert data['pontos_fortes'] == ['Estruturas Condicionais', 'Operadores Lógicos']
    assert data['topicos_dificuldade'] == ['List Comprehension', 'Funções Lambda']
    assert data['topicos_praticar'] == [TOPICO_PRATICAR]
    assert data['taxa_acerto_geral'] == 78.5
    assert data['total_atividades_avaliadas'] == 14
    assert data['ultima_atualizacao'] is not None
    assert set(data) == {
        'pontos_fortes', 'topicos_dificuldade', 'topicos_praticar', 'taxa_acerto_geral',
        'total_atividades_avaliadas', 'ultima_atualizacao',
    }


def test_nao_expoe_memoria_de_outro_usuario(client, django_user_model, memoria):
    outro = baker.make(django_user_model, apelido='bob', email='bob@example.com')
    client.force_login(outro)

    response = client.get(URL)

    assert response.status_code == 200
    assert response.json()['pontos_fortes'] == []
    assert response.json()['total_atividades_avaliadas'] == 0


def test_le_a_memoria_sem_recalcular_o_perfil(client, user, memoria, monkeypatch):
    from assistantManagement.memory_service import PedagogicalMemoryService

    def nao_deve_consolidar(*args, **kwargs):
        raise AssertionError('o endpoint não deve consolidar a memória na requisição')

    monkeypatch.setattr(PedagogicalMemoryService, 'consolidar_perfil', nao_deve_consolidar)
    client.force_login(user)

    response = client.get(URL)

    assert response.status_code == 200


def test_uma_unica_consulta_a_memoria(client, user, memoria):
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    client.force_login(user)

    # Sessão, usuário e auditoria (LGPD) rodam em toda requisição; o endpoint
    # em si deve fazer só uma leitura da memória pedagógica.
    with CaptureQueriesContext(connection) as queries:
        response = client.get(URL)

    assert response.status_code == 200
    consultas_memoria = [
        q['sql'] for q in queries.captured_queries if 'MEMORIA_PEDAGOGICA_USUARIO' in q['sql']
    ]
    assert len(consultas_memoria) == 1


def test_documentado_no_schema_openapi(client):
    response = client.get('/api/schema/', HTTP_ACCEPT='application/json')

    assert response.status_code == 200
    schema = response.json() if 'json' in response['Content-Type'] else None
    if schema is None:
        import yaml

        schema = yaml.safe_load(response.content)
    operacao = schema['paths'][URL]['get']
    assert operacao['summary'] == 'Diagnóstico pedagógico do estudante logado'
    assert '200' in operacao['responses']

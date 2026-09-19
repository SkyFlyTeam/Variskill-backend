import pytest
from django.urls import reverse
from model_bakery import baker

from trackManagement.models import Modulo, Trilha


pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def trilha():
    return baker.make(Trilha, titulo='Javascript', habilidade='Frontend')


@pytest.fixture
def admin(django_user_model):
    return baker.make(django_user_model, is_staff=True, is_superuser=True)


@pytest.fixture
def regular_user(django_user_model):
    return baker.make(django_user_model)


def modulo_payload(trilha, **overrides):
    payload = {
        'trilha_id': str(trilha.id),
        'titulo': 'Módulo 1 - Fundamentos',
        'descricao': 'Sintaxe elementar, variáveis e operações básicas.',
        'nivel': 'INICIANTE',
        'ordem_modulo': 1,
    }
    payload.update(overrides)
    return payload


def test_list_is_public(client, trilha):
    baker.make(Modulo, trilha=trilha, titulo='M1', ordem_modulo=1)

    response = client.get(reverse('modulo-list'))

    assert response.status_code == 200
    assert [item['titulo'] for item in response.data] == ['M1']


def test_list_filters_by_trilha_id(client):
    trilha_a = baker.make(Trilha, titulo='Python', habilidade='Backend')
    trilha_b = baker.make(Trilha, titulo='Go', habilidade='Backend')
    baker.make(Modulo, trilha=trilha_a, ordem_modulo=1)
    baker.make(Modulo, trilha=trilha_a, ordem_modulo=2)
    baker.make(Modulo, trilha=trilha_b, ordem_modulo=1)

    response = client.get(reverse('modulo-list'), {'trilha_id': str(trilha_a.id)})

    assert response.status_code == 200
    assert len(response.data) == 2
    assert {item['trilha_id'] for item in response.data} == {str(trilha_a.id)}


def test_list_orders_by_ordem_modulo(client, trilha):
    baker.make(Modulo, trilha=trilha, titulo='Terceiro', ordem_modulo=3)
    baker.make(Modulo, trilha=trilha, titulo='Primeiro', ordem_modulo=1)
    baker.make(Modulo, trilha=trilha, titulo='Segundo', ordem_modulo=2)

    response = client.get(reverse('modulo-list'))

    assert [item['ordem_modulo'] for item in response.data] == [1, 2, 3]


def test_retrieve_is_public(client, trilha):
    modulo = baker.make(Modulo, trilha=trilha, ordem_modulo=1)

    response = client.get(reverse('modulo-detail', args=[modulo.id]))

    assert response.status_code == 200
    assert set(response.data) == {'id', 'trilha_id', 'titulo', 'descricao', 'nivel', 'ordem_modulo'}


def test_anonymous_cannot_create(client, trilha):
    response = client.post(reverse('modulo-list'), modulo_payload(trilha), format='json')

    assert response.status_code == 403
    assert not Modulo.objects.exists()


def test_regular_user_cannot_create(client, regular_user, trilha):
    client.force_login(regular_user)

    response = client.post(reverse('modulo-list'), modulo_payload(trilha), format='json')

    assert response.status_code == 403
    assert not Modulo.objects.exists()


def test_regular_user_cannot_delete(client, regular_user, trilha):
    client.force_login(regular_user)
    modulo = baker.make(Modulo, trilha=trilha, ordem_modulo=1)

    response = client.delete(reverse('modulo-detail', args=[modulo.id]))

    assert response.status_code == 403
    assert Modulo.objects.exists()


def test_admin_can_create_modulo(client, admin, trilha):
    client.force_login(admin)

    response = client.post(reverse('modulo-list'), modulo_payload(trilha), format='json')

    assert response.status_code == 201
    modulo = Modulo.objects.get()
    assert response.data == {
        'id': str(modulo.id),
        'trilha_id': str(trilha.id),
        'titulo': 'Módulo 1 - Fundamentos',
        'descricao': 'Sintaxe elementar, variáveis e operações básicas.',
        'nivel': 'INICIANTE',
        'ordem_modulo': 1,
    }


def test_admin_can_update_modulo(client, admin, trilha):
    client.force_login(admin)
    modulo = baker.make(Modulo, trilha=trilha, titulo='Antigo', ordem_modulo=1)

    response = client.patch(
        reverse('modulo-detail', args=[modulo.id]),
        {'titulo': 'Novo título'},
        format='json',
    )

    assert response.status_code == 200
    modulo.refresh_from_db()
    assert modulo.titulo == 'Novo título'


def test_admin_can_delete_modulo(client, admin, trilha):
    client.force_login(admin)
    modulo = baker.make(Modulo, trilha=trilha, ordem_modulo=1)

    response = client.delete(reverse('modulo-detail', args=[modulo.id]))

    assert response.status_code == 204
    assert not Modulo.objects.exists()

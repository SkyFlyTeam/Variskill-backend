import pytest
from django.urls import reverse
from model_bakery import baker

from activityManagement.models import Conteudo

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def admin_user(django_user_model):
    return baker.make(django_user_model, apelido='admin', is_staff=True)


@pytest.fixture
def regular_user(django_user_model):
    return baker.make(django_user_model, apelido='student', is_staff=False)


@pytest.fixture
def content():
    return baker.make(Conteudo, titulo='Variaveis', texto_explicativo='Texto', tempo_estimado_minutos=4)


def test_content_requires_authentication(client, content):
    assert client.get(reverse('conteudo-detail', args=[content.pk])).status_code == 403


def test_create_content_requires_admin(client, regular_user):
    client.force_login(regular_user)
    response = client.post(reverse('conteudo-list'), {'titulo': 'X', 'texto_explicativo': 'Y', 'tempo_estimado_minutos': 4}, format='json')
    assert response.status_code == 403


def test_admin_can_create_content(client, admin_user):
    client.force_login(admin_user)
    response = client.post(reverse('conteudo-list'), {'titulo': 'X', 'texto_explicativo': 'Y', 'tempo_estimado_minutos': 4}, format='json')
    assert response.status_code == 201
    assert Conteudo.objects.get().titulo == 'X'


def test_retrieve_content_returns_text(client, regular_user, content):
    client.force_login(regular_user)
    response = client.get(reverse('conteudo-detail', args=[content.pk]))
    assert response.status_code == 200
    assert response.data['texto_explicativo'] == 'Texto'


def test_admin_can_update_content(client, admin_user, content):
    client.force_login(admin_user)
    response = client.put(reverse('conteudo-detail', args=[content.pk]), {'titulo': 'Lacos', 'texto_explicativo': 'Novo', 'tempo_estimado_minutos': 7}, format='json')
    assert response.status_code == 200
    content.refresh_from_db()
    assert content.titulo == 'Lacos'
    assert content.tempo_estimado_minutos == 7

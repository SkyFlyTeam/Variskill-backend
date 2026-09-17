import pytest
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from model_bakery import baker


pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def user(django_user_model):
    return baker.make(
        django_user_model,
        apelido='alice',
        password=make_password('test-password-123'),
    )


def test_register_creates_user_and_session(client, django_user_model):
    response = client.post(
        reverse('register'),
        {'apelido': 'alice', 'nome': 'Alice', 'email': 'alice@example.com', 'password': 'test-password-123'},
        format='json',
    )

    assert response.status_code == 201
    user = django_user_model.objects.get(apelido='alice')
    assert user.check_password('test-password-123')
    assert response.data == {'id': str(user.pk), 'apelido': 'alice', 'nome': 'Alice', 'email': 'alice@example.com', 'xp_total': 0, 'streak_dias': 0}
    assert client.session['_auth_user_id'] == str(user.pk)
    assert client.get(reverse('user-list')).status_code == 200


@pytest.mark.parametrize('payload, field', [
    ({'apelido': 'alice', 'nome': 'Alice', 'email': 'alice@example.com'}, 'password'),
    ({'nome': 'Alice', 'email': 'alice@example.com', 'password': 'test-password-123'}, 'apelido'),
    ({'apelido': 'alice', 'nome': 'Alice', 'email': 'alice@example.com', 'password': ''}, 'password'),
])
def test_register_rejects_invalid_data(client, django_user_model, payload, field):
    response = client.post(reverse('register'), payload, format='json')

    assert response.status_code == 400
    assert field in response.data
    assert not django_user_model.objects.exists()
    assert '_auth_user_id' not in client.session


def test_register_rejects_duplicate_apelido(client, user, django_user_model):
    response = client.post(
        reverse('register'),
        {'apelido': user.apelido, 'nome': user.nome, 'email': user.email, 'password': 'another-password'},
        format='json',
    )

    assert response.status_code == 400
    assert 'apelido' in response.data
    assert django_user_model.objects.count() == 1


def test_login_creates_session(client, user):
    response = client.post(
        reverse('login'),
        {'apelido': user.apelido, 'password': 'test-password-123'},
        format='json',
    )

    assert response.status_code == 200
    assert response.data['id'] == str(user.pk)
    assert response.data['apelido'] == user.apelido
    assert client.session['_auth_user_id'] == str(user.pk)
    assert client.get(reverse('user-list')).status_code == 200


@pytest.mark.parametrize('apelido, password', [
    ('alice', 'wrong-password'),
    ('unknown', 'test-password-123'),
])
def test_login_rejects_invalid_credentials(client, user, apelido, password):
    response = client.post(
        reverse('login'),
        {'apelido': apelido, 'password': password},
        format='json',
    )

    assert response.status_code == 400
    assert response.data == {'detail': 'Invalid credentials.'}
    assert '_auth_user_id' not in client.session


@pytest.mark.parametrize('payload, field', [
    ({'apelido': 'alice', 'nome': 'Alice', 'email': 'alice@example.com'}, 'password'),
    ({'nome': 'Alice', 'email': 'alice@example.com', 'password': 'test-password-123'}, 'apelido'),
])
def test_login_requires_credentials(client, payload, field):
    response = client.post(reverse('login'), payload, format='json')

    assert response.status_code == 400
    assert field in response.data
    assert '_auth_user_id' not in client.session


@pytest.mark.parametrize('method, route', [
    ('get', 'user-list'),
    ('post', 'user-list'),
    ('get', 'user-detail'),
    ('put', 'user-detail'),
    ('patch', 'user-detail'),
    ('delete', 'user-detail'),
])
def test_users_require_authentication(client, user, method, route):
    url = reverse(route, args=[user.pk] if route == 'user-detail' else None)

    assert getattr(client, method)(url).status_code == 403


def test_authenticated_user_can_list_and_retrieve_users(client, user, django_user_model):
    second_user = baker.make(django_user_model, apelido='bob')
    client.force_login(user)

    response = client.get(reverse('user-list'))

    assert response.status_code == 200
    assert [item['id'] for item in response.data] == sorted([str(user.pk), str(second_user.pk)])
    assert [item['apelido'] for item in response.data] == [user.apelido if str(user.pk) < str(second_user.pk) else second_user.apelido, second_user.apelido if str(user.pk) < str(second_user.pk) else user.apelido]
    response = client.get(reverse('user-detail', args=[second_user.pk]))
    assert response.status_code == 200
    assert response.data['id'] == str(second_user.pk)
    assert response.data['apelido'] == 'bob'


def test_authenticated_user_can_create_user(client, user, django_user_model):
    client.force_login(user)

    response = client.post(
        reverse('user-list'),
        {'apelido': 'bob', 'nome': 'Bob', 'email': 'bob@example.com', 'password': 'new-password'},
        format='json',
    )

    assert response.status_code == 201
    created = django_user_model.objects.get(apelido='bob')
    assert created.check_password('new-password')
    assert response.data['id'] == str(created.pk)
    assert response.data['apelido'] == 'bob'


@pytest.mark.parametrize('method', ['put', 'patch'])
def test_authenticated_user_can_update_user(client, user, method):
    client.force_login(user)

    response = getattr(client, method)(
        reverse('user-detail', args=[user.pk]),
        {'apelido': 'updated', 'nome': user.nome, 'email': user.email, 'password': 'updated-password'},
        format='json',
    )

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.apelido == 'updated'
    assert user.check_password('updated-password')
    assert response.data['id'] == str(user.pk)
    assert response.data['apelido'] == 'updated'


def test_partial_update_preserves_password(client, user):
    client.force_login(user)

    response = client.patch(
        reverse('user-detail', args=[user.pk]),
        {'apelido': 'updated'},
        format='json',
    )

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.apelido == 'updated'
    assert user.check_password('test-password-123')


def test_authenticated_user_can_delete_user(client, user, django_user_model):
    client.force_login(user)

    response = client.delete(reverse('user-detail', args=[user.pk]))

    assert response.status_code == 204
    assert not django_user_model.objects.filter(pk=user.pk).exists()

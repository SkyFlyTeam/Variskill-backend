import pytest
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from model_bakery import baker


pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def user(django_user_model):
    return baker.make(
        django_user_model,
        nickName='alice',
        password=make_password('test-password-123'),
    )


def test_register_creates_user_and_session(client, django_user_model):
    response = client.post(
        reverse('register'),
        {'nickName': 'alice', 'password': 'test-password-123'},
        format='json',
    )

    assert response.status_code == 201
    user = django_user_model.objects.get(nickName='alice')
    assert user.check_password('test-password-123')
    assert response.data == {'id': user.pk, 'nickName': 'alice'}
    assert client.session['_auth_user_id'] == str(user.pk)
    assert client.get(reverse('user-list')).status_code == 200


@pytest.mark.parametrize('payload, field', [
    ({'nickName': 'alice'}, 'password'),
    ({'password': 'test-password-123'}, 'nickName'),
    ({'nickName': 'alice', 'password': ''}, 'password'),
])
def test_register_rejects_invalid_data(client, django_user_model, payload, field):
    response = client.post(reverse('register'), payload, format='json')

    assert response.status_code == 400
    assert field in response.data
    assert not django_user_model.objects.exists()
    assert '_auth_user_id' not in client.session


def test_register_rejects_duplicate_nickname(client, user, django_user_model):
    response = client.post(
        reverse('register'),
        {'nickName': user.nickName, 'password': 'another-password'},
        format='json',
    )

    assert response.status_code == 400
    assert 'nickName' in response.data
    assert django_user_model.objects.count() == 1


def test_login_creates_session(client, user):
    response = client.post(
        reverse('login'),
        {'nickName': user.nickName, 'password': 'test-password-123'},
        format='json',
    )

    assert response.status_code == 200
    assert response.data == {'id': user.pk, 'nickName': user.nickName}
    assert client.session['_auth_user_id'] == str(user.pk)
    assert client.get(reverse('user-list')).status_code == 200


@pytest.mark.parametrize('nickname, password', [
    ('alice', 'wrong-password'),
    ('unknown', 'test-password-123'),
])
def test_login_rejects_invalid_credentials(client, user, nickname, password):
    response = client.post(
        reverse('login'),
        {'nickName': nickname, 'password': password},
        format='json',
    )

    assert response.status_code == 400
    assert response.data == {'detail': 'Invalid credentials.'}
    assert '_auth_user_id' not in client.session


@pytest.mark.parametrize('payload, field', [
    ({'nickName': 'alice'}, 'password'),
    ({'password': 'test-password-123'}, 'nickName'),
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
    second_user = baker.make(django_user_model, nickName='bob')
    client.force_login(user)

    response = client.get(reverse('user-list'))

    assert response.status_code == 200
    assert response.data == [
        {'id': user.pk, 'nickName': user.nickName},
        {'id': second_user.pk, 'nickName': second_user.nickName},
    ]
    response = client.get(reverse('user-detail', args=[second_user.pk]))
    assert response.status_code == 200
    assert response.data == {'id': second_user.pk, 'nickName': 'bob'}


def test_authenticated_user_can_create_user(client, user, django_user_model):
    client.force_login(user)

    response = client.post(
        reverse('user-list'),
        {'nickName': 'bob', 'password': 'new-password'},
        format='json',
    )

    assert response.status_code == 201
    created = django_user_model.objects.get(nickName='bob')
    assert created.check_password('new-password')
    assert response.data == {'id': created.pk, 'nickName': 'bob'}


@pytest.mark.parametrize('method', ['put', 'patch'])
def test_authenticated_user_can_update_user(client, user, method):
    client.force_login(user)

    response = getattr(client, method)(
        reverse('user-detail', args=[user.pk]),
        {'nickName': 'updated', 'password': 'updated-password'},
        format='json',
    )

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.nickName == 'updated'
    assert user.check_password('updated-password')
    assert response.data == {'id': user.pk, 'nickName': 'updated'}


def test_partial_update_preserves_password(client, user):
    client.force_login(user)

    response = client.patch(
        reverse('user-detail', args=[user.pk]),
        {'nickName': 'updated'},
        format='json',
    )

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.nickName == 'updated'
    assert user.check_password('test-password-123')


def test_authenticated_user_can_delete_user(client, user, django_user_model):
    client.force_login(user)

    response = client.delete(reverse('user-detail', args=[user.pk]))

    assert response.status_code == 204
    assert not django_user_model.objects.filter(pk=user.pk).exists()

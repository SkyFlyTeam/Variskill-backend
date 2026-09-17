import pytest
from django.urls import reverse
from model_bakery import baker

from learning.models import Content


pytestmark = [pytest.mark.integration, pytest.mark.django_db]

MARKDOWN = (
    'Variáveis são usadas para armazenar dados em JavaScript.\n\n'
    '```js\nconst total = 4\nconsole.log(total)\n```\n'
)


@pytest.fixture
def admin_user(django_user_model):
    return baker.make(django_user_model, nickName='admin', is_staff=True)


@pytest.fixture
def regular_user(django_user_model):
    return baker.make(django_user_model, nickName='student', is_staff=False)


@pytest.fixture
def content():
    return baker.make(
        Content,
        title='Variáveis',
        explanatory_text=MARKDOWN,
        estimated_minutes=4,
    )


@pytest.mark.parametrize('method, route', [
    ('get', 'conteudo-list'),
    ('post', 'conteudo-list'),
    ('get', 'conteudo-detail'),
    ('put', 'conteudo-detail'),
    ('patch', 'conteudo-detail'),
    ('delete', 'conteudo-detail'),
])
def test_content_requires_authentication(client, content, method, route):
    url = reverse(route, args=[content.pk] if route == 'conteudo-detail' else None)

    assert getattr(client, method)(url).status_code == 403


def test_create_content_requires_admin(client, regular_user):
    client.force_login(regular_user)

    response = client.post(
        reverse('conteudo-list'),
        {'titulo': 'Variáveis', 'texto_explicativo': MARKDOWN, 'tempo_estimado_minutos': 4},
        format='json',
    )

    assert response.status_code == 403
    assert not Content.objects.exists()


@pytest.mark.parametrize('method', ['put', 'patch', 'delete'])
def test_modify_content_requires_admin(client, regular_user, content, method):
    client.force_login(regular_user)
    url = reverse('conteudo-detail', args=[content.pk])
    data = {'titulo': 'Outro título'} if method in ('put', 'patch') else None

    response = getattr(client, method)(url, data, format='json')

    assert response.status_code == 403
    content.refresh_from_db()
    assert content.title == 'Variáveis'


def test_admin_can_create_content(client, admin_user):
    client.force_login(admin_user)

    response = client.post(
        reverse('conteudo-list'),
        {'titulo': 'Variáveis', 'texto_explicativo': MARKDOWN, 'tempo_estimado_minutos': 4},
        format='json',
    )

    assert response.status_code == 201
    created = Content.objects.get()
    assert response.data['id'] == str(created.pk)
    assert response.data['titulo'] == 'Variáveis'
    assert response.data['texto_explicativo'] == MARKDOWN
    assert response.data['tempo_estimado_minutos'] == 4
    assert response.data['criado_em'].endswith('Z')


def test_retrieve_content_returns_full_markdown(client, regular_user, content):
    client.force_login(regular_user)

    response = client.get(reverse('conteudo-detail', args=[content.pk]))

    assert response.status_code == 200
    assert response.data['id'] == str(content.pk)
    assert response.data['titulo'] == 'Variáveis'
    assert response.data['texto_explicativo'] == MARKDOWN
    assert response.data['tempo_estimado_minutos'] == 4
    assert response.data['criado_em'].endswith('Z')


def test_admin_can_update_content(client, admin_user, content):
    client.force_login(admin_user)

    response = client.put(
        reverse('conteudo-detail', args=[content.pk]),
        {'titulo': 'Laços', 'texto_explicativo': 'Novo texto', 'tempo_estimado_minutos': 7},
        format='json',
    )

    assert response.status_code == 200
    content.refresh_from_db()
    assert content.title == 'Laços'
    assert content.explanatory_text == 'Novo texto'
    assert content.estimated_minutes == 7

import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework_simplejwt.tokens import RefreshToken

from learning.models import Activity, Content, Module, Option, Question


pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def auth_header(user):
    token = RefreshToken.for_user(user).access_token
    return {'HTTP_AUTHORIZATION': f'Bearer {token}'}


@pytest.fixture
def admin_user(django_user_model):
    return baker.make(django_user_model, nickName='admin', is_staff=True)


@pytest.fixture
def regular_user(django_user_model):
    return baker.make(django_user_model, nickName='student', is_staff=False)


@pytest.fixture
def module():
    return baker.make(Module)


@pytest.fixture
def content():
    return baker.make(Content, estimated_minutes=4)


@pytest.fixture
def activity(module, content):
    return baker.make(
        Activity,
        module=module,
        content=content,
        evaluation_context='FIXACAO_CONCEITO',
        xp_reward=50,
        order=1,
        active=True,
    )


@pytest.fixture
def question(activity):
    question = baker.make(
        Question,
        activity=activity,
        exercise_type='ORDENAR_BLOCOS',
        order=1,
        expected_answer='const',
        explanation='...',
        conceptual_hint='...',
    )
    baker.make(Option, question=question, order=1)
    return question


@pytest.mark.parametrize('method, route', [
    ('get', 'atividade-list'),
    ('post', 'atividade-list'),
    ('get', 'atividade-detail'),
    ('put', 'atividade-detail'),
    ('delete', 'atividade-detail'),
])
def test_activities_require_authentication(client, activity, method, route):
    url = reverse(route, args=[activity.pk] if route == 'atividade-detail' else None)

    assert getattr(client, method)(url).status_code == 401


def test_create_activity_requires_admin(client, regular_user, module, content):
    payload = {
        'modulo_id': str(module.pk),
        'conteudo_id': str(content.pk),
        'titulo': 'Variáveis',
        'descricao': 'Aprenda a declarar e usar variáveis.',
        'contexto_avaliacao': 'FIXACAO_CONCEITO',
        'xp_recompensa': 50,
        'ordem_atividade': 1,
    }

    response = client.post(reverse('atividade-list'), payload, format='json', **auth_header(regular_user))

    assert response.status_code == 403
    assert not Activity.objects.exists()


def test_admin_can_create_activity(client, admin_user, module, content):
    payload = {
        'modulo_id': str(module.pk),
        'conteudo_id': str(content.pk),
        'titulo': 'Variáveis',
        'descricao': 'Aprenda a declarar e usar variáveis.',
        'contexto_avaliacao': 'FIXACAO_CONCEITO',
        'xp_recompensa': 50,
        'ordem_atividade': 1,
    }

    response = client.post(reverse('atividade-list'), payload, format='json', **auth_header(admin_user))

    assert response.status_code == 201
    assert response.data['ativo'] is True
    assert response.data['titulo'] == 'Variáveis'
    assert 'modulo_id' not in response.data
    assert 'conteudo_id' not in response.data
    created = Activity.objects.get()
    assert created.module_id == module.pk
    assert created.content_id == content.pk


def test_retrieve_activity_includes_content_and_ordered_questions(client, regular_user, activity, content, question):
    second_question = baker.make(
        Question, activity=activity, exercise_type='ORDENAR_BLOCOS', order=0,
        expected_answer='x', explanation='x', conceptual_hint='x',
    )

    response = client.get(
        reverse('atividade-detail', args=[activity.pk]), **auth_header(regular_user),
    )

    assert response.status_code == 200
    assert response.data['conteudo_teorico']['id'] == str(content.pk)
    assert response.data['conteudo_teorico']['tempo_estimado_minutos'] == 4
    returned_ids = [q['id'] for q in response.data['questoes']]
    assert returned_ids == [str(second_question.pk), str(question.pk)]


def test_retrieve_activity_never_exposes_sensitive_question_fields(client, regular_user, activity, question):
    response = client.get(
        reverse('atividade-detail', args=[activity.pk]), **auth_header(regular_user),
    )

    question_payload = response.data['questoes'][0]
    assert 'gabarito_esperado' not in question_payload
    assert 'explicacao' not in question_payload
    assert 'dica_conceitual' not in question_payload
    assert question_payload['opcoes'][0]['ordem'] == 1


def test_admin_can_update_activity_mutable_fields(client, admin_user, activity):
    response = client.put(
        reverse('atividade-detail', args=[activity.pk]),
        {
            'titulo': 'Novo título',
            'descricao': 'Nova descrição',
            'contexto_avaliacao': 'FIXACAO_CONCEITO',
            'xp_recompensa': 80,
            'ordem_atividade': 2,
        },
        format='json',
        **auth_header(admin_user),
    )

    assert response.status_code == 200
    activity.refresh_from_db()
    assert activity.title == 'Novo título'
    assert activity.xp_reward == 80


def test_update_activity_requires_admin(client, regular_user, activity):
    response = client.put(
        reverse('atividade-detail', args=[activity.pk]),
        {
            'titulo': 'Novo título',
            'contexto_avaliacao': 'FIXACAO_CONCEITO',
            'xp_recompensa': 80,
            'ordem_atividade': 2,
        },
        format='json',
        **auth_header(regular_user),
    )

    assert response.status_code == 403


def test_admin_delete_deactivates_without_removing_record(client, admin_user, activity):
    response = client.delete(
        reverse('atividade-detail', args=[activity.pk]), **auth_header(admin_user),
    )

    assert response.status_code == 200
    assert response.data == {'mensagem': 'Atividade desativada com sucesso.'}
    activity.refresh_from_db()
    assert activity.active is False
    assert Activity.objects.filter(pk=activity.pk).exists()


def test_delete_requires_admin(client, regular_user, activity):
    response = client.delete(
        reverse('atividade-detail', args=[activity.pk]), **auth_header(regular_user),
    )

    assert response.status_code == 403
    activity.refresh_from_db()
    assert activity.active is True


def test_inactive_activities_excluded_from_public_listing(client, regular_user, module, content):
    baker.make(Activity, module=module, content=content, active=True, order=1)
    inactive = baker.make(Activity, module=module, content=content, active=False, order=2)

    response = client.get(reverse('atividade-list'), **auth_header(regular_user))

    assert response.status_code == 200
    returned_ids = [item['id'] for item in response.data]
    assert str(inactive.pk) not in returned_ids


def test_admin_listing_includes_inactive_activities(client, admin_user, module, content):
    inactive = baker.make(Activity, module=module, content=content, active=False, order=1)

    response = client.get(reverse('atividade-list'), **auth_header(admin_user))

    assert response.status_code == 200
    returned_ids = [item['id'] for item in response.data]
    assert str(inactive.pk) in returned_ids


def test_inactive_activity_detail_hidden_from_regular_user(client, regular_user, module, content):
    inactive = baker.make(Activity, module=module, content=content, active=False, order=1)

    response = client.get(reverse('atividade-detail', args=[inactive.pk]), **auth_header(regular_user))

    assert response.status_code == 404


def test_inactive_activity_detail_visible_to_admin(client, admin_user, module, content):
    inactive = baker.make(Activity, module=module, content=content, active=False, order=1)

    response = client.get(reverse('atividade-detail', args=[inactive.pk]), **auth_header(admin_user))

    assert response.status_code == 200
    assert response.data['ativo'] is False


def test_admin_can_partially_update_activity(client, admin_user, activity):
    response = client.patch(
        reverse('atividade-detail', args=[activity.pk]),
        {'titulo': 'Título atualizado via PATCH'},
        format='json',
        **auth_header(admin_user),
    )

    assert response.status_code == 200
    activity.refresh_from_db()
    assert activity.title == 'Título atualizado via PATCH'


def test_partial_update_requires_admin(client, regular_user, activity):
    response = client.patch(
        reverse('atividade-detail', args=[activity.pk]),
        {'titulo': 'Não deveria funcionar'},
        format='json',
        **auth_header(regular_user),
    )

    assert response.status_code == 403

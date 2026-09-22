import pytest
from django.urls import reverse
from model_bakery import baker

from activityManagement.models import Atividade, Conteudo
from learning.models import Module
from questionsManagement.models import Questao, QuestaoOpcao

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def admin_user(django_user_model):
    return baker.make(django_user_model, apelido='admin', is_staff=True)


@pytest.fixture
def regular_user(django_user_model):
    return baker.make(django_user_model, apelido='student', is_staff=False)


@pytest.fixture
def module():
    return baker.make(Module)


@pytest.fixture
def content():
    return baker.make(Conteudo, tempo_estimado_minutos=4)


@pytest.fixture
def activity(module, content):
    return baker.make(Atividade, modulo=module, conteudo=content, ordem=1, ativo=True)


@pytest.fixture
def question(activity):
    question = baker.make(Questao, atividade=activity, tipo_exercicio='ORDENAR_BLOCOS', ordem_questao=1, gabarito_esperado='const', explicacao='x', dica_conceitual='x')
    baker.make(QuestaoOpcao, questao=question, ordem=1)
    return question


def test_create_activity_requires_admin(client, regular_user, module):
    client.force_login(regular_user)
    response = client.post(reverse('atividade-list'), {'modulo_id': str(module.pk), 'titulo': 'X', 'descricao': 'Y', 'contexto_avaliacao': 'CODIGO', 'xp_recompensa': 10, 'ordem_atividade': 1}, format='json')
    assert response.status_code == 403


def test_admin_can_create_activity_without_content(client, admin_user, module):
    client.force_login(admin_user)
    response = client.post(reverse('atividade-list'), {'modulo_id': str(module.pk), 'titulo': 'X', 'descricao': 'Y', 'contexto_avaliacao': 'CODIGO', 'xp_recompensa': 10, 'ordem_atividade': 1}, format='json')
    assert response.status_code == 201
    assert Atividade.objects.get().conteudo is None


def test_retrieve_activity_includes_content_and_questions(client, regular_user, activity, content, question):
    client.force_login(regular_user)
    response = client.get(reverse('atividade-detail', args=[activity.pk]))
    assert response.status_code == 200
    assert response.data['conteudo_teorico']['id'] == str(content.pk)
    assert response.data['questoes'][0]['id'] == str(question.pk)
    assert 'gabarito_esperado' not in response.data['questoes'][0]


def test_admin_can_update_activity(client, admin_user, activity):
    client.force_login(admin_user)
    response = client.patch(reverse('atividade-detail', args=[activity.pk]), {'titulo': 'Atualizada'}, format='json')
    assert response.status_code == 200
    activity.refresh_from_db()
    assert activity.titulo == 'Atualizada'


def test_delete_deactivates_activity(client, admin_user, activity):
    client.force_login(admin_user)
    response = client.delete(reverse('atividade-detail', args=[activity.pk]))
    assert response.status_code == 200
    activity.refresh_from_db()
    assert activity.ativo is False


def test_inactive_activity_hidden_from_regular_user(client, regular_user, module):
    activity = baker.make(Atividade, modulo=module, conteudo=None, ativo=False, ordem=1)
    client.force_login(regular_user)
    assert client.get(reverse('atividade-detail', args=[activity.pk])).status_code == 404

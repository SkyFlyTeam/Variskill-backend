from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker

from activityManagement.models import Atividade, ExecucaoAtividade
from learning.models import Module
from questionsManagement.models import Questao


pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def student(django_user_model):
    return baker.make(django_user_model, apelido='student', is_staff=False, xp_total=150, streak_dias=0)


@pytest.fixture
def atividade():
    return baker.make(
        Atividade,
        modulo=baker.make(Module),
        conteudo=None,
        contexto_avaliacao='FIXACAO_CONCEITO',
        xp_recompensa=50,
        ordem=1,
        ativo=True,
    )


def make_questao(atividade, order=1, weight=1, exercise_type='MULTIPLA_ESCOLHA', expected='A', explanation=''):
    return baker.make(
        Questao,
        atividade=atividade,
        tipo_exercicio=exercise_type,
        ordem_questao=order,
        gabarito_esperado=expected,
        explicacao=explanation,
        peso_pontuacao=weight,
    )


def submit(client, atividade, answers):
    return client.post(
        reverse('atividade-submit', args=[atividade.pk]),
        {'respostas': answers},
        format='json',
    )


def test_submission_requires_authentication(client, atividade):
    make_questao(atividade)

    assert submit(client, atividade, {}).status_code == 403


def test_inactive_activity_cannot_be_submitted_by_regular_user(client, student, atividade):
    make_questao(atividade)
    Atividade.objects.filter(pk=atividade.pk).update(ativo=False)
    client.force_login(student)

    assert submit(client, atividade, {}).status_code == 404


def test_approved_submission_persists_execution_and_credits_xp(client, student, atividade):
    questao = make_questao(atividade, weight=10, explanation='Porque sim.')
    client.force_login(student)

    response = submit(client, atividade, {str(questao.pk): ['A']})

    assert response.status_code == 200
    assert response.data['aprovado'] is True
    assert response.data['taxa_acerto'] == 100.0
    assert response.data['pontuacao_obtida'] == 10
    assert response.data['xp_concedido'] == 50
    assert response.data['novo_xp_total'] == 200
    execution = ExecucaoAtividade.objects.get(pk=response.data['execucao_id'])
    assert execution.usuario == student
    assert execution.atividade == atividade
    assert execution.aprovado is True
    assert execution.pontuacao_obtida == 10
    assert execution.resposta == {str(questao.pk): ['A']}
    student.refresh_from_db()
    assert student.xp_total == 200
    assert student.streak_dias == 1


@pytest.mark.parametrize('correct_count, approved, hit_rate', [
    (7, True, 70.0),
    (6, False, 60.0),
])
def test_cutoff_is_70_percent(client, student, atividade, correct_count, approved, hit_rate):
    questoes = [make_questao(atividade, order=index) for index in range(10)]
    answers = {
        str(questao.pk): ['A' if index < correct_count else 'B']
        for index, questao in enumerate(questoes)
    }
    client.force_login(student)

    response = submit(client, atividade, answers)

    assert response.data['aprovado'] is approved
    assert response.data['taxa_acerto'] == hit_rate
    assert response.data['xp_concedido'] == (50 if approved else 0)


def test_failed_submission_is_recorded_without_xp_or_streak(client, student, atividade):
    heavy = make_questao(atividade, order=1, weight=3)
    light = make_questao(atividade, order=2, weight=7)
    client.force_login(student)

    response = submit(client, atividade, {str(heavy.pk): ['A'], str(light.pk): ['B']})

    assert response.data['aprovado'] is False
    assert response.data['pontuacao_obtida'] == 3
    assert response.data['xp_concedido'] == 0
    assert response.data['novo_xp_total'] == 150
    execution = ExecucaoAtividade.objects.get(pk=response.data['execucao_id'])
    assert execution.aprovado is False
    assert execution.pontuacao_obtida == 3
    student.refresh_from_db()
    assert student.xp_total == 150
    assert student.streak_dias == 0


def test_feedback_lists_explanation_of_every_question_and_unanswered_counts_as_wrong(client, student, atividade):
    answered = make_questao(atividade, order=1, explanation='Explicação 1')
    unanswered = make_questao(atividade, order=2, explanation='Explicação 2')
    client.force_login(student)

    response = submit(client, atividade, {str(answered.pk): ['A']})

    assert response.data['questoes_feedback'] == [
        {'questao_id': str(answered.pk), 'correta': True, 'explicacao': 'Explicação 1'},
        {'questao_id': str(unanswered.pk), 'correta': False, 'explicacao': 'Explicação 2'},
    ]
    assert response.data['taxa_acerto'] == 50.0


def test_unknown_question_id_is_rejected_without_persisting(client, student, atividade):
    make_questao(atividade)
    other_questao = make_questao(baker.make(
        Atividade, modulo=atividade.modulo, conteudo=None, ordem=2,
    ))
    client.force_login(student)

    response = submit(client, atividade, {str(other_questao.pk): ['A']})

    assert response.status_code == 400
    assert 'respostas' in response.data
    assert not ExecucaoAtividade.objects.exists()


def test_activity_without_questions_is_rejected(client, student, atividade):
    client.force_login(student)

    response = submit(client, atividade, {})

    assert response.status_code == 400
    assert not ExecucaoAtividade.objects.exists()


def test_fill_blank_answer_is_sanitized(client, student, atividade):
    questao = make_questao(atividade, exercise_type='COMPLETE_CODIGO', expected='int, integer')
    client.force_login(student)

    response = submit(client, atividade, {str(questao.pk): ['  INT ']})

    assert response.data['questoes_feedback'][0]['correta'] is True


@pytest.mark.parametrize('sent, correct', [
    (['id1', 'id2', 'id3'], True),
    (['id2', 'id1', 'id3'], False),
])
def test_block_order_answer_must_match_expected_sequence(client, student, atividade, sent, correct):
    questao = make_questao(atividade, exercise_type='ORDENAR_BLOCOS', expected='id1,id2,id3')
    client.force_login(student)

    response = submit(client, atividade, {str(questao.pk): sent})

    assert response.data['questoes_feedback'][0]['correta'] is correct


@pytest.mark.parametrize('days_since_last_approval, streak_before, streak_after', [
    (0, 4, 4),
    (1, 4, 5),
    (3, 4, 1),
])
def test_daily_streak(client, student, atividade, days_since_last_approval, streak_before, streak_after):
    questao = make_questao(atividade)
    previous = baker.make(
        ExecucaoAtividade, usuario=student, atividade=atividade, aprovado=True,
        pontuacao_obtida=1, resposta={},
    )
    ExecucaoAtividade.objects.filter(pk=previous.pk).update(
        executado_em=timezone.now() - timedelta(days=days_since_last_approval),
    )
    type(student).objects.filter(pk=student.pk).update(streak_dias=streak_before)
    client.force_login(student)

    submit(client, atividade, {str(questao.pk): ['A']})

    student.refresh_from_db()
    assert student.streak_dias == streak_after

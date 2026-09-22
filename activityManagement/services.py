from dataclasses import dataclass
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from grading.validators import ResponseValidatorContext

from .models import ExecucaoAtividade

APPROVAL_THRESHOLD_PERCENT = 70

# Traduz a resposta do front (lista de strings por questão) para o payload de cada ResponseValidator.
_PAYLOAD_BY_EXERCISE_TYPE = {
    'MULTIPLA_ESCOLHA': lambda answer: {'opcao_selecionada': answer[0] if answer else None},
    'COMPLETE_CODIGO': lambda answer: {'valor_preenchido': answer[0] if answer else ''},
    'ORDENAR_BLOCOS': lambda answer: {'ordem_enviada': answer},
}


@dataclass
class SubmissionResult:
    execution: ExecucaoAtividade
    approved: bool
    hit_rate: float
    score_obtained: int
    xp_granted: int
    new_xp_total: int
    feedback: list


def _is_correct(questao, answer):
    payload = _PAYLOAD_BY_EXERCISE_TYPE[questao.tipo_exercicio](answer)
    return ResponseValidatorContext.for_questao(questao).validar(questao, payload)


def _next_streak(user):
    last_approved_at = (
        ExecucaoAtividade.objects.filter(usuario=user, aprovado=True)
        .order_by('-executado_em')
        .values_list('executado_em', flat=True)
        .first()
    )
    if last_approved_at is None:
        return 1

    today = timezone.localdate()
    last_day = timezone.localtime(last_approved_at).date()
    if last_day == today:
        return user.streak_dias
    if last_day == today - timedelta(days=1):
        return user.streak_dias + 1
    return 1


@transaction.atomic
def submit_activity(user, atividade, answers):
    questoes = list(atividade.questoes.all())
    feedback = []
    correct_count = 0
    score_obtained = 0

    for questao in questoes:
        correct = _is_correct(questao, answers.get(str(questao.pk), []))
        if correct:
            correct_count += 1
            score_obtained += questao.peso_pontuacao
        feedback.append({
            'questao_id': str(questao.pk),
            'correta': correct,
            'explicacao': questao.explicacao,
        })

    approved = correct_count * 100 >= APPROVAL_THRESHOLD_PERCENT * len(questoes)
    hit_rate = round(correct_count * 100 / len(questoes), 1)

    locked_user = get_user_model().objects.select_for_update().get(pk=user.pk)
    xp_granted = atividade.xp_recompensa if approved else 0
    if approved:
        locked_user.streak_dias = _next_streak(locked_user)
        locked_user.xp_total += xp_granted
        locked_user.save(update_fields=['xp_total', 'streak_dias'])

    execution = ExecucaoAtividade.objects.create(
        usuario=locked_user,
        atividade=atividade,
        resposta=answers,
        aprovado=approved,
        pontuacao_obtida=score_obtained,
    )

    return SubmissionResult(
        execution=execution,
        approved=approved,
        hit_rate=hit_rate,
        score_obtained=score_obtained,
        xp_granted=xp_granted,
        new_xp_total=locked_user.xp_total,
        feedback=feedback,
    )

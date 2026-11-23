import json
import logging
from dataclasses import dataclass, field

from django.contrib.auth import get_user_model
from django.db import transaction

from grading.validators import ResponseValidatorContext

from userManagement.gamification_engine import (
    EVENTO_ATIVIDADE_CONCLUIDA,
    EVENTO_MODULO_CONCLUIDO,
    EVENTO_STREAK_ATUALIZADO,
    EVENTO_TRILHA_CONCLUIDA,
    GamificationEngine,
)
from userManagement.services import GamificationService, StreakService
from .models import ExecucaoAtividade, RespostaQuestao

logger = logging.getLogger(__name__)

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
    level_up: bool
    nivel_anterior: int
    novo_nivel: int
    conquistas_desbloqueadas: list = field(default_factory=list)


def _is_correct(questao, answer):
    payload = _PAYLOAD_BY_EXERCISE_TYPE[questao.tipo_exercicio](answer)
    return ResponseValidatorContext.for_questao(questao).validar(questao, payload)


def avaliar_conquistas_conclusao(usuario, atividade, *, taxa_acerto, streak_dias=None) -> list[dict]:
    """Avalia as conquistas disparadas pela conclusão aprovada de uma atividade.

    Deve ser chamada após persistir a ExecucaoAtividade aprovada. Usada tanto na
    submissão de exercícios quanto na conclusão de lições teóricas.
    """
    engine = GamificationEngine()
    conquistas = engine.avaliar_conquistas_usuario(
        usuario, EVENTO_ATIVIDADE_CONCLUIDA, {'aprovado': True, 'taxa_acerto': taxa_acerto},
    )
    if streak_dias is not None:
        conquistas += engine.avaliar_conquistas_usuario(
            usuario, EVENTO_STREAK_ATUALIZADO, {'streak_dias': streak_dias},
        )
    conquistas += engine.avaliar_conquistas_usuario(
        usuario, EVENTO_MODULO_CONCLUIDO, {'modulo_id': atividade.modulo_id},
    )
    conquistas += engine.avaliar_conquistas_usuario(
        usuario, EVENTO_TRILHA_CONCLUIDA, {'trilha_id': atividade.modulo.trilha_id},
    )
    return conquistas


@transaction.atomic
def submit_activity(user, atividade, answers, pratica_reforco=False):
    questoes = list(atividade.questoes.all())
    feedback = []
    respostas_avaliadas = []
    correct_count = 0
    score_obtained = 0

    for questao in questoes:
        answer = answers.get(str(questao.pk), [])
        correct = _is_correct(questao, answer)
        if correct:
            correct_count += 1
            score_obtained += questao.peso_pontuacao
        feedback.append({
            'questao_id': str(questao.pk),
            'correta': correct,
            'explicacao': questao.explicacao,
        })
        respostas_avaliadas.append((questao, answer, correct))

    approved = correct_count * 100 >= APPROVAL_THRESHOLD_PERCENT * len(questoes)
    hit_rate = round(correct_count * 100 / len(questoes), 1)

    locked_user = get_user_model().objects.select_for_update().get(pk=user.pk)
    already_approved = ExecucaoAtividade.objects.filter(
        usuario=locked_user,
        atividade=atividade,
        aprovado=True,
    ).exists()

    gamification = GamificationService()
    nivel_anterior = gamification.calcular_nivel(locked_user.xp_total)

    xp_granted = (atividade.xp_recompensa if approved and not already_approved else 0)
    streak_info = None
    if approved:
        streak_info = StreakService.computar_atividade_diaria(
            locked_user, xp_ganho=xp_granted, nova_conclusao=not already_approved,
        )
        if not already_approved:
            gamification.creditar_xp(locked_user, atividade)

    execution = ExecucaoAtividade.objects.create(
        usuario=locked_user,
        atividade=atividade,
        resposta=answers,
        aprovado=approved,
        pontuacao_obtida=score_obtained,
        pratica_reforco=pratica_reforco,
    )

    RespostaQuestao.objects.bulk_create([
        RespostaQuestao(
            execucao=execution,
            questao=questao,
            resposta_fornecida=json.dumps(answer, ensure_ascii=False),
            correta=correct,
        )
        for questao, answer, correct in respostas_avaliadas
    ])

    # Avaliada após persistir a execução: PRIMEIRO_PASSO e EXPLORADOR_MODULO dependem dela.
    conquistas_desbloqueadas = []
    if approved:
        conquistas_desbloqueadas = avaliar_conquistas_conclusao(
            locked_user,
            atividade,
            taxa_acerto=hit_rate,
            streak_dias=streak_info['streak_dias'] if streak_info is not None else None,
        )

    # Calculado após as conquistas para que o XP bônus conte no level up.
    novo_nivel = gamification.calcular_nivel(locked_user.xp_total)
    level_up = (novo_nivel > nivel_anterior)

    # Consolidação assíncrona da memória pedagógica do estudante (VAR-118) sem travar a thread.
    # Só após o commit: antes dele a thread (outra conexão) não enxerga esta submissão.
    try:
        from assistantManagement.memory_service import PedagogicalMemoryService
        transaction.on_commit(lambda: PedagogicalMemoryService.consolidar_perfil_async(locked_user))
    except Exception as exc:
        logger.warning("Falha ao agendar consolidação de memória pedagógica para usuário %s: %s", locked_user.pk, exc)

    return SubmissionResult(
        execution=execution,
        approved=approved,
        hit_rate=hit_rate,
        score_obtained=score_obtained,
        xp_granted=xp_granted,
        new_xp_total=locked_user.xp_total,
        feedback=feedback,
        level_up=level_up,
        nivel_anterior=nivel_anterior,
        novo_nivel=novo_nivel,
        conquistas_desbloqueadas=conquistas_desbloqueadas,
    )

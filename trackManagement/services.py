from dataclasses import dataclass
from typing import Dict, List
import uuid

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from activityManagement.models import Atividade, ExecucaoAtividade
from trackManagement.models import Matricula, Modulo, ProgressoModulo, Trilha

LEVEL_INICIANTE = 'INICIANTE'
LEVEL_INTERMEDIARIO = 'INTERMEDIARIO'
LEVEL_AVANCADO = 'AVANCADO'

LEVEL_RANK = {
    LEVEL_INICIANTE: 1,
    LEVEL_INTERMEDIARIO: 2,
    LEVEL_AVANCADO: 3,
}

ASSISTANT_MESSAGES = {
    LEVEL_INICIANTE: (
        'Ótimo começo! Seu desempenho indicou o nível Iniciante. '
        'Liberei os módulos correspondentes para você.'
    ),
    LEVEL_INTERMEDIARIO: (
        'Excelente! Seu desempenho indicou o nível Intermediário. '
        'Liberei os módulos correspondentes para você.'
    ),
    LEVEL_AVANCADO: (
        'Sensacional! Seu desempenho indicou o nível Avançado. '
        'Liberei os módulos correspondentes para você.'
    ),
}


@dataclass
class PosicionamentoResult:
    nivel_posicionado: str
    taxa_acerto: float
    modulos_liberados: List[Dict]
    mensagem_assistente: str


def calcular_taxa_acerto(atividade: Atividade, execucao: ExecucaoAtividade) -> float:
    total_pontos = sum(q.peso_pontuacao for q in atividade.questoes.all())
    if total_pontos > 0:
        return round((execucao.pontuacao_obtida * 100.0) / total_pontos, 1)
    return round(float(execucao.pontuacao_obtida), 1)


def definir_nivel(taxa_acerto: float) -> str:
    if taxa_acerto < 70.0:
        return LEVEL_INICIANTE
    if taxa_acerto < 85.0:
        return LEVEL_INTERMEDIARIO
    return LEVEL_AVANCADO


@transaction.atomic
def posicionar_nivel_pos_diagnostico(user, atividade_id: uuid.UUID, matricula_id: uuid.UUID) -> PosicionamentoResult:
    # 1. Validar existência da atividade
    try:
        atividade = Atividade.objects.prefetch_related('questoes').get(pk=atividade_id)
    except Atividade.DoesNotExist:
        raise NotFound('Atividade diagnóstica não encontrada.')

    # 2. Validar contexto de avaliação
    if atividade.contexto_avaliacao != 'DIAGNOSTICO_INICIAL':
        raise ValidationError({
            'detail': "O posicionamento só pode ser executado para atividades com contexto 'DIAGNOSTICO_INICIAL'."
        })

    # 3. Validar matrícula
    try:
        matricula = (
            Matricula.objects.select_related('trilha', 'usuario')
            .select_for_update()
            .get(pk=matricula_id)
        )
    except Matricula.DoesNotExist:
        raise NotFound('Matrícula não encontrada.')

    # 4. Validar permissão (dono da matrícula ou administrador)
    if matricula.usuario_id != user.id and not getattr(user, 'is_staff', False):
        raise PermissionDenied('A matrícula informada não pertence ao usuário autenticado.')

    # 5. Validar execução prévia da atividade diagnóstica
    execucao = (
        ExecucaoAtividade.objects.filter(usuario=matricula.usuario, atividade=atividade)
        .order_by('-executado_em')
        .first()
    )
    if not execucao:
        raise ValidationError({
            'detail': 'Nenhuma execução diagnóstica encontrada para este usuário nesta atividade.'
        })

    # 6. Apurar desempenho e definir nível
    taxa_acerto = calcular_taxa_acerto(atividade, execucao)
    nivel_posicionado = definir_nivel(taxa_acerto)
    target_rank = LEVEL_RANK[nivel_posicionado]

    # 7. Buscar módulos da trilha
    modulos_trilha = list(matricula.trilha.modulos.all().order_by('ordem_modulo'))
    if not modulos_trilha:
        raise ValidationError({
            'detail': 'A trilha associada à matrícula não possui módulos cadastrados.'
        })

    modulos_liberados = []
    first_target_level_found = False

    # 8. Atualizar atomicamente PROGRESSO_MODULO
    for mod in modulos_trilha:
        mod_nivel = mod.nivel.upper()
        mod_rank = LEVEL_RANK.get(mod_nivel, 1)

        if mod_rank < target_rank:
            status = 'CONCLUIDO'
            concluido_em = timezone.now()
        elif mod_rank == target_rank:
            if not first_target_level_found:
                status = 'EM_ANDAMENTO'
                concluido_em = None
                first_target_level_found = True
            else:
                status = 'BLOQUEADO'
                concluido_em = None
        else:
            status = 'BLOQUEADO'
            concluido_em = None

        ProgressoModulo.objects.update_or_create(
            matricula=matricula,
            modulo=mod,
            defaults={
                'status': status,
                'concluido_em': concluido_em,
            },
        )

        if status == 'EM_ANDAMENTO':
            modulos_liberados.append({
                'id': mod.id,
                'titulo': mod.titulo,
                'nivel': mod.nivel,
                'status': status,
            })

    mensagem_assistente = ASSISTANT_MESSAGES.get(
        nivel_posicionado,
        f'Seu nível foi definido como {nivel_posicionado}. Módulos liberados com sucesso!'
    )

    return PosicionamentoResult(
        nivel_posicionado=nivel_posicionado,
        taxa_acerto=taxa_acerto,
        modulos_liberados=modulos_liberados,
        mensagem_assistente=mensagem_assistente,
    )


@transaction.atomic
def efetivar_matricula(usuario, trilha: Trilha) -> Matricula:
    """Efetiva a matrícula e inicializa o PROGRESSO_MODULO (módulo 1 EM_ANDAMENTO, demais BLOQUEADO)."""
    if Matricula.objects.filter(usuario=usuario, trilha=trilha).exists():
        raise ValidationError({
            'detail': (
                f'Já existe uma matrícula de {usuario.apelido} ({usuario.email}) '
                f'na trilha "{trilha.titulo}".'
            )
        })

    matricula = Matricula.objects.create(
        usuario=usuario,
        trilha=trilha,
        status='EM_ANDAMENTO',
    )

    modulos = list(trilha.modulos.all().order_by('ordem_modulo'))
    if not modulos:
        raise ValidationError({
            'detail': 'A trilha não possui módulos cadastrados.'
        })

    ProgressoModulo.objects.bulk_create([
        ProgressoModulo(
            matricula=matricula,
            modulo=modulo,
            status='EM_ANDAMENTO' if indice == 0 else 'BLOQUEADO',
        )
        for indice, modulo in enumerate(modulos)
    ])

    return matricula


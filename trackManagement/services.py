from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List
import uuid

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count, Q, QuerySet
from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from activityManagement.models import Atividade, ExecucaoAtividade, RespostaQuestao
from questionsManagement.models import Questao
from trackManagement.models import Matricula, Modulo, ProgressoModulo, Trilha
from userManagement.models import UsuarioInteresse

DIAGNOSTICO_ERROS_THRESHOLD_PERCENT = 70.0

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


@dataclass
class DiagnosticoErrosResult:
    modulo_id: uuid.UUID
    total_respondidas: int
    total_acertos: int
    taxa_acerto: float
    questoes_erradas: List[Questao]
    parecer: str


def _conceito_da_questao(questao: Questao) -> str:
    """Texto conceitual mais específico disponível para citar no parecer formativo."""
    if questao.dica_conceitual and questao.dica_conceitual.strip():
        return questao.dica_conceitual.strip()
    if questao.explicacao and questao.explicacao.strip():
        return questao.explicacao.strip()
    return questao.enunciado.strip()


def _gerar_parecer_formativo(total_respondidas: int, taxa_acerto: float, questoes_erradas: List[Questao]) -> str:
    if total_respondidas == 0:
        return (
            'Você ainda não respondeu questões neste módulo. '
            'Realize as atividades para receber seu diagnóstico.'
        )

    if taxa_acerto >= DIAGNOSTICO_ERROS_THRESHOLD_PERCENT:
        parecer = (
            f'Você demonstra domínio sólido do conteúdo deste módulo, '
            f'com {taxa_acerto}% de acerto nas questões já respondidas.'
        )
        if questoes_erradas:
            conceitos = '; '.join(_conceito_da_questao(q) for q in questoes_erradas)
            parecer += f' Como ponto de atenção secundário, vale revisar: {conceitos}.'
        else:
            parecer += ' Continue assim!'
        return parecer

    conceitos = '; '.join(_conceito_da_questao(q) for q in questoes_erradas)
    return (
        f'Sua taxa de acerto neste módulo foi de {taxa_acerto}%, '
        f'abaixo do esperado ({DIAGNOSTICO_ERROS_THRESHOLD_PERCENT:.0f}%). '
        f'Recomendamos revisar os seguintes conceitos antes de prosseguir: {conceitos}.'
    )


def obter_diagnostico_erros(usuario, modulo_id: uuid.UUID) -> DiagnosticoErrosResult:
    """Consolida, a partir de RESPOSTA_QUESTAO, o diagnóstico de erros do usuário
    na última execução de cada atividade do módulo informado, com parecer formativo
    determinístico (>= 70% de acerto: domínio; < 70%: revisão dos conceitos errados).
    """
    try:
        modulo = Modulo.objects.get(pk=modulo_id)
    except (Modulo.DoesNotExist, ValueError):
        raise NotFound('Módulo não encontrado.')

    ultimas_execucoes_ids = (
        ExecucaoAtividade.objects.filter(usuario=usuario, atividade__modulo=modulo)
        .order_by('atividade_id', '-executado_em')
        .distinct('atividade_id')
        .values_list('id', flat=True)
    )

    respostas = list(
        RespostaQuestao.objects.filter(execucao_id__in=list(ultimas_execucoes_ids))
        .select_related('questao')
    )

    total_respondidas = len(respostas)
    total_acertos = sum(1 for resposta in respostas if resposta.correta)
    taxa_acerto = (
        round(total_acertos * 100.0 / total_respondidas, 1) if total_respondidas else 0.0
    )
    questoes_erradas = [resposta.questao for resposta in respostas if not resposta.correta]

    parecer = _gerar_parecer_formativo(total_respondidas, taxa_acerto, questoes_erradas)

    return DiagnosticoErrosResult(
        modulo_id=modulo.id,
        total_respondidas=total_respondidas,
        total_acertos=total_acertos,
        taxa_acerto=taxa_acerto,
        questoes_erradas=questoes_erradas,
        parecer=parecer,
    )


# Pesos da similaridade entre estudantes usada na recomendação "Recomendado para você".
PESO_INTERESSES = 3.0
PESO_IDADE_PROXIMA = 1.0
PESO_IDADE_FAIXA = 0.5
PESO_SEXO = 0.5
IDADE_PROXIMA_ANOS = 3
IDADE_FAIXA_ANOS = 7

CRITERIO_PERFIL_SIMILAR = 'PERFIL_SIMILAR'
CRITERIO_POPULARIDADE = 'POPULARIDADE'
CRITERIO_CATALOGO = 'CATALOGO'


def trilhas_ativas_com_contagens() -> QuerySet:
    return Trilha.objects.filter(ativo=True).annotate(
        total_modulos=Count('modulos', distinct=True),
        total_atividades=Count(
            'modulos__atividades',
            filter=Q(modulos__atividades__ativo=True),
            distinct=True,
        ),
    )


def _similaridade_perfil(usuario, meus_interesses: set, outro, interesses_outro: set) -> tuple[float, set]:
    """Pontua o quanto `outro` se parece com `usuario` e indica quais dimensões coincidiram."""
    pontuacao, dimensoes = 0.0, set()

    if meus_interesses and interesses_outro:
        jaccard = len(meus_interesses & interesses_outro) / len(meus_interesses | interesses_outro)
        if jaccard:
            pontuacao += PESO_INTERESSES * jaccard
            dimensoes.add('interesses')

    if usuario.idade is not None and outro.idade is not None:
        diferenca = abs(usuario.idade - outro.idade)
        if diferenca <= IDADE_PROXIMA_ANOS:
            pontuacao += PESO_IDADE_PROXIMA
            dimensoes.add('idade')
        elif diferenca <= IDADE_FAIXA_ANOS:
            pontuacao += PESO_IDADE_FAIXA
            dimensoes.add('idade')

    if usuario.sexo and usuario.sexo == outro.sexo:
        pontuacao += PESO_SEXO
        dimensoes.add('sexo')

    return pontuacao, dimensoes


def _pontuar_por_perfis_similares(usuario, trilha_ids: list) -> tuple[Dict, Dict]:
    """
    Soma, por trilha, a similaridade dos estudantes parecidos com `usuario` que estão matriculados nela.
    Estudantes anonimizados ou que revogaram o consentimento não entram no cálculo (LGPD).
    """
    meus_interesses = set(
        UsuarioInteresse.objects.filter(usuario=usuario).values_list('interesse_id', flat=True)
    )

    filtro_similar = Q()
    if meus_interesses:
        filtro_similar |= Q(interesses_usuario__interesse_id__in=meus_interesses)
    if usuario.idade is not None:
        filtro_similar |= Q(idade__range=(usuario.idade - IDADE_FAIXA_ANOS, usuario.idade + IDADE_FAIXA_ANOS))
    if usuario.sexo:
        filtro_similar |= Q(sexo=usuario.sexo)
    if not filtro_similar:
        return {}, {}

    candidatos = list(
        get_user_model().objects.filter(
            filtro_similar,
            is_active=True,
            anonimizado_em__isnull=True,
            consentimento_revogado_em__isnull=True,
            matriculas__trilha_id__in=trilha_ids,
        ).exclude(pk=usuario.pk).distinct()
    )

    interesses_por_usuario = defaultdict(set)
    for usuario_id, interesse_id in UsuarioInteresse.objects.filter(
        usuario__in=candidatos,
    ).values_list('usuario_id', 'interesse_id'):
        interesses_por_usuario[usuario_id].add(interesse_id)

    similares = {}
    for outro in candidatos:
        pontuacao, dimensoes = _similaridade_perfil(
            usuario, meus_interesses, outro, interesses_por_usuario[outro.pk],
        )
        if pontuacao > 0:
            similares[outro.pk] = (pontuacao, dimensoes)

    pontuacoes, dimensoes_por_trilha = defaultdict(float), defaultdict(set)
    for usuario_id, trilha_id in Matricula.objects.filter(
        usuario_id__in=similares.keys(), trilha_id__in=trilha_ids,
    ).values_list('usuario_id', 'trilha_id'):
        pontuacao, dimensoes = similares[usuario_id]
        pontuacoes[trilha_id] += pontuacao
        dimensoes_por_trilha[trilha_id] |= dimensoes

    return pontuacoes, dimensoes_por_trilha


def _motivo_perfil_similar(dimensoes: set) -> str:
    partes = []
    if 'interesses' in dimensoes:
        partes.append('interesses parecidos com os seus')
    if 'idade' in dimensoes:
        partes.append('idade próxima à sua')
    if not partes:
        return 'Estudantes com perfil parecido com o seu estão fazendo esta trilha.'
    return f'Estudantes com {" e ".join(partes)} estão fazendo esta trilha.'


def recomendar_trilhas_por_perfil(usuario, limite: int = 3) -> List[Trilha]:
    """
    Recomenda trilhas ativas em que o estudante ainda não está matriculado, priorizando as que
    estudantes de perfil similar (interesses, idade e sexo) estão fazendo. Sem perfis similares,
    recorre às trilhas mais procuradas e, por fim, ao catálogo em ordem alfabética.
    Cada trilha retornada recebe os atributos `criterio` e `motivo`.
    """
    trilhas = list(
        trilhas_ativas_com_contagens()
        .exclude(matriculas__usuario=usuario)
        .annotate(total_matriculas=Count('matriculas', distinct=True))
    )
    pontuacoes, dimensoes_por_trilha = _pontuar_por_perfis_similares(usuario, [t.id for t in trilhas])

    trilhas.sort(key=lambda t: (-pontuacoes.get(t.id, 0.0), -t.total_matriculas, t.titulo))

    for trilha in trilhas[:limite]:
        if pontuacoes.get(trilha.id):
            trilha.criterio = CRITERIO_PERFIL_SIMILAR
            trilha.motivo = _motivo_perfil_similar(dimensoes_por_trilha[trilha.id])
        elif trilha.total_matriculas:
            trilha.criterio = CRITERIO_POPULARIDADE
            trilha.motivo = 'Uma das trilhas mais procuradas pelos estudantes do VariSkill.'
        else:
            trilha.criterio = CRITERIO_CATALOGO
            trilha.motivo = trilha.descricao or 'Uma boa trilha para começar sua jornada no VariSkill.'

    return trilhas[:limite]

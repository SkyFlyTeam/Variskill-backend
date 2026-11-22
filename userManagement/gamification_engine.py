"""Motor determinístico de conquistas (gamificação).

Uso:
    GamificationEngine().avaliar_conquistas_usuario(usuario, 'ATIVIDADE_CONCLUIDA', {...})

Eventos suportados e o `dados_evento` esperado:
- ATIVIDADE_CONCLUIDA: {'aprovado': bool, 'taxa_acerto': float}
    -> PRIMEIRO_PASSO (primeira atividade aprovada), PRECISAO_MAXIMA (100% de acerto)
- STREAK_ATUALIZADO: {'streak_dias': int}
    -> DEDICACAO_INICIAL (>= 3 dias), HABITO_DE_FERRO (>= 7 dias)
- MODULO_CONCLUIDO: {'modulo_id': UUID}
    -> EXPLORADOR_MODULO (todas as atividades ativas do módulo aprovadas)
- TRILHA_CONCLUIDA: {'trilha_id': UUID}
    -> MESTRE_TRILHA (todas as atividades ativas da trilha aprovadas)

A concessão é idempotente: uma conquista já registrada em UsuarioConquista nunca é
concedida de novo, nem credita XP outra vez.
"""
from django.db import transaction
from django.db.models import F

from activityManagement.models import Atividade, ExecucaoAtividade

from .models import Conquista, User, UsuarioConquista, UsuarioInventario

EVENTO_ATIVIDADE_CONCLUIDA = 'ATIVIDADE_CONCLUIDA'
EVENTO_STREAK_ATUALIZADO = 'STREAK_ATUALIZADO'
EVENTO_MODULO_CONCLUIDO = 'MODULO_CONCLUIDO'
EVENTO_TRILHA_CONCLUIDA = 'TRILHA_CONCLUIDA'

MARCOS_STREAK = (
    (3, 'DEDICACAO_INICIAL'),
    (7, 'HABITO_DE_FERRO'),
)


class GamificationEngine:
    def __init__(self):
        self._avaliadores = {
            EVENTO_ATIVIDADE_CONCLUIDA: self._avaliar_atividade_concluida,
            EVENTO_STREAK_ATUALIZADO: self._avaliar_streak,
            EVENTO_MODULO_CONCLUIDO: self._avaliar_modulo_concluido,
            EVENTO_TRILHA_CONCLUIDA: self._avaliar_trilha_concluida,
        }

    @transaction.atomic
    def avaliar_conquistas_usuario(self, usuario, evento: str, dados_evento: dict) -> list[dict]:
        avaliador = self._avaliadores.get(evento)
        if avaliador is None:
            raise ValueError(f'Evento de gamificação desconhecido: {evento!r}')

        codigos = avaliador(usuario, dados_evento or {})
        if not codigos:
            return []

        desbloqueadas = []
        conquistas = Conquista.objects.filter(codigo__in=codigos).order_by('ordem')
        for conquista in conquistas:
            dados = self._conceder(usuario, conquista)
            if dados is not None:
                desbloqueadas.append(dados)
        return desbloqueadas

    # --- Regras de elegibilidade -------------------------------------------------

    def _avaliar_atividade_concluida(self, usuario, dados):
        if not dados.get('aprovado'):
            return []
        codigos = []
        if ExecucaoAtividade.objects.filter(usuario=usuario, aprovado=True).exists():
            codigos.append('PRIMEIRO_PASSO')
        if float(dados.get('taxa_acerto') or 0) >= 100:
            codigos.append('PRECISAO_MAXIMA')
        return codigos

    def _avaliar_streak(self, usuario, dados):
        streak = int(dados.get('streak_dias') or 0)
        return [codigo for marco, codigo in MARCOS_STREAK if streak >= marco]

    def _avaliar_modulo_concluido(self, usuario, dados):
        modulo_id = dados.get('modulo_id')
        if modulo_id is None or not modulo_concluido(usuario, modulo_id):
            return []
        return ['EXPLORADOR_MODULO']

    def _avaliar_trilha_concluida(self, usuario, dados):
        trilha_id = dados.get('trilha_id')
        if trilha_id is None or not trilha_concluida(usuario, trilha_id):
            return []
        return ['MESTRE_TRILHA']

    # --- Concessão atômica -------------------------------------------------------

    def _conceder(self, usuario, conquista):
        _, created = UsuarioConquista.objects.get_or_create(usuario=usuario, conquista=conquista)
        if not created:
            return None

        if conquista.xp_recompensa:
            User.objects.filter(pk=usuario.pk).update(
                xp_total=F('xp_total') + conquista.xp_recompensa
            )
            usuario.refresh_from_db(fields=['xp_total'])

        itens = list(conquista.itens_cosmeticos.order_by('tipo', 'nome'))
        for item in itens:
            UsuarioInventario.objects.get_or_create(
                usuario=usuario, item=item, defaults={'equipado': False}
            )

        return serializar_conquista(conquista, itens)


def modulo_concluido(usuario, modulo_id) -> bool:
    """True se o usuário tem execução aprovada em todas as atividades ativas do módulo."""
    return _todas_aprovadas(usuario, Atividade.objects.filter(modulo_id=modulo_id, ativo=True))


def trilha_concluida(usuario, trilha_id) -> bool:
    """True se o usuário tem execução aprovada em todas as atividades ativas da trilha."""
    return _todas_aprovadas(usuario, Atividade.objects.filter(modulo__trilha_id=trilha_id, ativo=True))


def _todas_aprovadas(usuario, atividades) -> bool:
    atividades_ids = set(atividades.values_list('id', flat=True))
    if not atividades_ids:
        return False
    aprovadas = set(
        ExecucaoAtividade.objects.filter(
            usuario=usuario, aprovado=True, atividade_id__in=atividades_ids
        ).values_list('atividade_id', flat=True)
    )
    return atividades_ids <= aprovadas


def _serializar_item(item):
    return {
        'id': str(item.id),
        'nome': item.nome,
        'tipo': item.tipo,
        'asset_url': item.asset_url,
    }


def serializar_conquista(conquista, itens):
    itens_serializados = [_serializar_item(item) for item in itens]
    return {
        'id': str(conquista.id),
        'codigo': conquista.codigo,
        'titulo': conquista.titulo,
        'descricao': conquista.descricao,
        'icone': conquista.icone,
        'xp_recompensa': conquista.xp_recompensa,
        'item_desbloqueado': itens_serializados[0] if itens_serializados else None,
        'itens_desbloqueados': itens_serializados,
    }

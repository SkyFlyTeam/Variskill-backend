from datetime import datetime, timedelta
import uuid
from zoneinfo import ZoneInfo
from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from activityManagement.models import ExecucaoAtividade, RespostaQuestao
from .models import User


class GamificationService:
    @staticmethod
    def calcular_nivel(xp_total: int) -> int:
        """Calcula o nível do usuário baseado nas faixas de XP:
        - Nível 1: 0 a 99 XP (faixa de 100 XP)
        - Nível 2: 100 a 299 XP (faixa de 200 XP)
        - Nível 3: 300 a 599 XP (faixa de 300 XP)
        - Nível 4: 600 a 999 XP (faixa de 400 XP)
        - Nível 5+: 1000+ XP (a cada 500 XP adicionais, +1 nível)
        """
        xp = max(0, xp_total or 0)
        if xp < 100:
            return 1
        elif xp < 300:
            return 2
        elif xp < 600:
            return 3
        elif xp < 1000:
            return 4
        return 5 + ((xp - 1000) // 500)

    @staticmethod
    def obter_progresso_nivel(xp_total: int) -> dict:
        """Retorna detalhes do progresso atual do usuário na sua faixa de nível."""
        xp = max(0, xp_total or 0)
        nivel = GamificationService.calcular_nivel(xp)

        if nivel == 1:
            xp_min_faixa = 0
            xp_proximo_nivel = 100
        elif nivel == 2:
            xp_min_faixa = 100
            xp_proximo_nivel = 300
        elif nivel == 3:
            xp_min_faixa = 300
            xp_proximo_nivel = 600
        elif nivel == 4:
            xp_min_faixa = 600
            xp_proximo_nivel = 1000
        else:
            xp_min_faixa = 1000 + ((nivel - 5) * 500)
            xp_proximo_nivel = xp_min_faixa + 500

        faixa_total = xp_proximo_nivel - xp_min_faixa
        xp_na_faixa = xp - xp_min_faixa
        progresso_pct = round((xp_na_faixa / faixa_total) * 100, 1)
        xp_restante = max(0, xp_proximo_nivel - xp)

        return {
            "nivel": nivel,
            "xp_atual": xp,
            "xp_min_faixa": xp_min_faixa,
            "xp_proximo_nivel": xp_proximo_nivel,
            "xp_restante": xp_restante,
            "progresso_pct": progresso_pct,
        }

    @transaction.atomic
    def creditar_xp(self, usuario, atividade) -> int:
        """Soma Atividade.xp_recompensa a Usuario.xp_total de forma atômica.
        Retorna o novo xp_total.
        """
        if not atividade or not getattr(atividade, 'xp_recompensa', 0):
            return usuario.xp_total

        User.objects.filter(pk=usuario.pk).update(
            xp_total=F('xp_total') + atividade.xp_recompensa
        )
        usuario.refresh_from_db(fields=['xp_total'])
        return usuario.xp_total

    @transaction.atomic
    def atualizar_streak(self, usuario, data_referencia=None) -> int:
        """Aplica a regra incrementar / manter / resetar conforme o último acesso.
        Retorna o novo streak_dias.

        regras:
        - Último acesso ontem -> streak_dias += 1
        - Último acesso hoje -> manter o valor atual
        - Último acesso anterior a ontem ou inexistente -> streak_dias = 1
        """
        # Se data_referencia for omitida, busca a ultima execucao aprovada do usuario no banco
        if data_referencia is None:
            data_referencia = (
                ExecucaoAtividade.objects.filter(usuario=usuario, aprovado=True)
                .order_by('-executado_em')
                .values_list('executado_em', flat=True)
                .first()
            )

        tz = ZoneInfo(getattr(settings, 'TIME_ZONE', 'America/Sao_Paulo'))
        hoje = timezone.now().astimezone(tz).date()

        if data_referencia is None:
            # Sem acesso anterior registrado no banco ou inexistente
            novo_streak = 1
        else:
            if isinstance(data_referencia, datetime):
                data_referencia = data_referencia.astimezone(tz).date()

            if data_referencia == hoje:
                novo_streak = max(usuario.streak_dias, 1)
            elif data_referencia == hoje - timedelta(days=1):
                novo_streak = (usuario.streak_dias if usuario.streak_dias > 0 else 0) + 1
            else:
                novo_streak = 1

        User.objects.filter(pk=usuario.pk).update(streak_dias=novo_streak)
        usuario.refresh_from_db(fields=['streak_dias'])
        return usuario.streak_dias


@transaction.atomic
def anonimizar_usuario(usuario):
    """Anonimiza o titular preservando métricas (FKs) e bloquear o login.

    A exclusão self-service usa anonimização por padrão: o usuário deixa de ser
    identificável, mas execuções/progresso continuam válidos para estatísticas.
    """
    from assistantManagement.models import Sessao
    from .models import UsuarioInteresse

    locked = User.objects.select_for_update().get(pk=usuario.pk)
    sufixo = uuid.uuid4().hex

    locked.apelido = f"anonimo_{sufixo}"
    locked.nome = 'Usuário anonimizado'
    locked.email = f"anonimo_{sufixo}@anonimizado.local"
    locked.sexo = None
    locked.idade = None
    locked.is_active = False
    locked.is_staff = False
    locked.is_superuser = False
    locked.last_login = None
    locked.aceite_privacidade_versao = None
    locked.aceite_privacidade_em = None
    locked.consentimento_revogado_em = timezone.now()
    locked.anonimizado_em = timezone.now()
    locked.set_unusable_password()
    locked.groups.clear()
    locked.user_permissions.clear()
    locked.save()

    UsuarioInteresse.objects.filter(usuario=locked).delete()
    # Conversas e textos livres podem conter dado pessoal: removemos as sessões.
    Sessao.objects.filter(usuario=locked).delete()

    # Mantém desempenho/métricas, mas remove respostas e textos livres.
    ExecucaoAtividade.objects.filter(usuario=locked).update(resposta={})
    RespostaQuestao.objects.filter(execucao__usuario=locked).update(resposta_fornecida=None)

    return locked


def exportar_dados_usuario(usuario):
    """Monta o pacote de portabilidade do titular (perfil, histórico e conversas)."""
    from assistantManagement.models import Sessao
    from trackManagement.models import Matricula, ProgressoModulo

    interesses = list(
        usuario.interesses_usuario.select_related('interesse')
        .values('interesse__id', 'interesse__nome')
    )
    matriculas = list(
        Matricula.objects.filter(usuario=usuario)
        .select_related('trilha')
        .values(
            'id', 'trilha_id', 'trilha__titulo', 'status',
            'criado_em', 'concluido_em',
        )
    )
    progresso = list(
        ProgressoModulo.objects.filter(matricula__usuario=usuario)
        .select_related('modulo')
        .values(
            'id', 'matricula_id', 'modulo_id', 'modulo__titulo',
            'status', 'concluido_em',
        )
    )

    execucoes = []
    for execucao in (
        ExecucaoAtividade.objects.filter(usuario=usuario)
        .select_related('atividade')
        .prefetch_related('respostas_questoes')
        .order_by('executado_em')
    ):
        execucoes.append({
            'id': execucao.id,
            'atividade_id': execucao.atividade_id,
            'atividade_titulo': execucao.atividade.titulo,
            'resposta': execucao.resposta,
            'pontuacao_obtida': execucao.pontuacao_obtida,
            'aprovado': execucao.aprovado,
            'executado_em': execucao.executado_em,
            'respostas_questoes': [
                {
                    'id': resposta.id,
                    'questao_id': resposta.questao_id,
                    'resposta_fornecida': resposta.resposta_fornecida,
                    'correta': resposta.correta,
                    'criado_em': resposta.criado_em,
                }
                for resposta in execucao.respostas_questoes.all()
            ],
        })

    sessoes = []
    for sessao in (
        Sessao.objects.filter(usuario=usuario)
        .prefetch_related('mensagens')
        .order_by('criada_em')
    ):
        sessoes.append({
            'id': sessao.id,
            'trilha_contexto_id': sessao.trilha_contexto_id,
            'criada_em': sessao.criada_em,
            'atualizada_em': sessao.atualizada_em,
            'mensagens': [
                {
                    'id': mensagem.id,
                    'remetente': mensagem.remetente,
                    'conteudo': mensagem.conteudo,
                    'intencao': mensagem.intencao.code if mensagem.intencao else None,
                    'distancia': mensagem.distancia,
                    'origem_resposta': mensagem.origem_resposta or None,
                    'criada_em': mensagem.criada_em,
                }
                for mensagem in sessao.mensagens.all().order_by('criada_em')
            ],
        })

    return {
        'exportado_em': timezone.now(),
        'perfil': {
            'id': usuario.id,
            'apelido': usuario.apelido,
            'nome': usuario.nome,
            'email': usuario.email,
            'xp_total': usuario.xp_total,
            'streak_dias': usuario.streak_dias,
            'is_primeiro_acesso': usuario.is_primeiro_acesso,
            'sexo': usuario.sexo,
            'idade': usuario.idade,
            'criado_em': usuario.criado_em,
            'aceite_privacidade_versao': usuario.aceite_privacidade_versao,
            'aceite_privacidade_em': usuario.aceite_privacidade_em,
            'consentimento_revogado_em': usuario.consentimento_revogado_em,
            'consentimento_ativo': usuario.consentimento_ativo,
        },
        'interesses': interesses,
        'matriculas': matriculas,
        'progresso_modulos': progresso,
        'execucoes': execucoes,
        'sessoes_chat': sessoes,
    }

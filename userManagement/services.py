from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from activityManagement.models import ExecucaoAtividade
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

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from activityManagement.models import ExecucaoAtividade
from .models import User


class GamificationService:
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
                novo_streak = usuario.streak_dias
            elif data_referencia == hoje - timedelta(days=1):
                novo_streak = usuario.streak_dias + 1
            else:
                novo_streak = 1

        User.objects.filter(pk=usuario.pk).update(streak_dias=novo_streak)
        usuario.refresh_from_db(fields=['streak_dias'])
        return usuario.streak_dias

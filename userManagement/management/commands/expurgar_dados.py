from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from activityManagement.models import ExecucaoAtividade, RespostaQuestao
from assistantManagement.models import Sessao
from userManagement.audit import registrar_evento


class Command(BaseCommand):
    """Expurgo/anonimização de dados pessoais fora do prazo de retenção.

    O padrão é dry-run: nada é alterado sem --executar.
    """

    help = (
        'Apaga sessões de chat antigas e anonimiza respostas de execuções antigas, '
        'preservando métricas agregadas.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias',
            type=int,
            default=None,
            help='Idade mínima em dias (default: LGPD_RETENCAO_DIAS).',
        )
        parser.add_argument(
            '--executar',
            action='store_true',
            help='Aplica a exclusão/anonimização (sem esta flag, apenas simula).',
        )

    def handle(self, *args, **options):
        dias = options['dias'] or getattr(settings, 'LGPD_RETENCAO_DIAS', 365)
        cutoff = timezone.now() - timedelta(days=dias)

        sessoes = Sessao.objects.filter(criada_em__lt=cutoff)
        execucoes = ExecucaoAtividade.objects.filter(executado_em__lt=cutoff)
        respostas = RespostaQuestao.objects.filter(execucao__executado_em__lt=cutoff)
        totais = {
            'sessoes': sessoes.count(),
            'execucoes': execucoes.count(),
            'respostas': respostas.count(),
        }

        self.stdout.write(
            f'Retenção: {dias} dias (cutoff {cutoff.isoformat()}). '
            f'Sessões: {totais["sessoes"]} | Execuções: {totais["execucoes"]} | '
            f'Respostas: {totais["respostas"]}'
        )

        if not options['executar']:
            self.stdout.write(self.style.WARNING(
                'Dry-run: nada foi alterado. Use --executar para aplicar.'
            ))
            return

        with transaction.atomic():
            sessoes.delete()
            execucoes.update(resposta={})
            respostas.update(resposta_fornecida=None)

        registrar_evento(
            usuario=None,
            acao='EXPURGO_EXECUTADO',
            metadata={**totais, 'dias': dias},
        )

        self.stdout.write(self.style.SUCCESS('Expurgo concluído.'))

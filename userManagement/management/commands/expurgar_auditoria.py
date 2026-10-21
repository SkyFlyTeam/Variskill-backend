from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from userManagement.models import EventoAuditoria


class Command(BaseCommand):
    """Expurgo manual dos eventos de auditoria fora do prazo (default: 1 ano)."""

    help = 'Remove eventos de auditoria mais antigos que LGPD_AUDITORIA_RETENCAO_DIAS.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias',
            type=int,
            default=None,
            help='Idade mínima em dias (default: LGPD_AUDITORIA_RETENCAO_DIAS).',
        )
        parser.add_argument(
            '--executar',
            action='store_true',
            help='Aplica a exclusão (sem esta flag, apenas simula).',
        )

    def handle(self, *args, **options):
        dias = options['dias'] or getattr(settings, 'LGPD_AUDITORIA_RETENCAO_DIAS', 365)
        cutoff = timezone.now() - timedelta(days=dias)
        eventos = EventoAuditoria.objects.filter(criado_em__lt=cutoff)

        self.stdout.write(
            f'Auditoria: retenção de {dias} dias (cutoff {cutoff.isoformat()}). '
            f'Eventos elegíveis: {eventos.count()}'
        )

        if not options['executar']:
            self.stdout.write(self.style.WARNING(
                'Dry-run: nada foi alterado. Use --executar para aplicar.'
            ))
            return

        removidos, _ = eventos.delete()
        self.stdout.write(self.style.SUCCESS(f'Eventos removidos: {removidos}'))

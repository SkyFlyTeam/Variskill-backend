from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from activityManagement.models import ExecucaoAtividade, RespostaQuestao
from assistantManagement.models import Sessao
from userManagement.audit import registrar_evento
from userManagement.models import EventoAuditoria, User


class Command(BaseCommand):
    """Expurgo/anonimização de dados pessoais fora do prazo de retenção.

    O padrão é dry-run: nada é alterado sem --executar. Os prazos podem ser
    definidos por categoria (LGPD_RETENCAO_*_DIAS). Contas com legal hold
    (retencao_suspensa_ate no futuro) são sempre ignoradas.
    """

    help = (
        'Apaga sessões de chat antigas, anonimiza respostas de execuções antigas '
        'e, opcionalmente, anonimiza contas inativas, preservando métricas.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias',
            type=int,
            default=None,
            help='Sobrepõe todos os prazos por categoria (default: settings).',
        )
        parser.add_argument(
            '--incluir-contas',
            action='store_true',
            help='Anonimiza contas inativas fora do prazo (respeita legal hold).',
        )
        parser.add_argument(
            '--incluir-auditoria',
            action='store_true',
            help='Remove eventos de auditoria fora do prazo de retenção.',
        )
        parser.add_argument(
            '--executar',
            action='store_true',
            help='Aplica a exclusão/anonimização (sem esta flag, apenas simula).',
        )

    def _prazo(self, options, categoria):
        if options['dias']:
            return options['dias']
        return getattr(
            settings,
            f'LGPD_RETENCAO_{categoria}_DIAS',
            getattr(settings, 'LGPD_RETENCAO_DIAS', 365),
        )

    def handle(self, *args, **options):
        agora = timezone.now()
        dias_mensagens = self._prazo(options, 'MENSAGENS')
        dias_execucoes = self._prazo(options, 'EXECUCOES')
        dias_auditoria = self._prazo(options, 'AUDITORIA')

        cutoff_mensagens = agora - timedelta(days=dias_mensagens)
        cutoff_execucoes = agora - timedelta(days=dias_execucoes)
        cutoff_auditoria = agora - timedelta(days=dias_auditoria)

        sessoes = Sessao.objects.filter(criada_em__lt=cutoff_mensagens)
        execucoes = ExecucaoAtividade.objects.filter(
            executado_em__lt=cutoff_execucoes
        )
        respostas = RespostaQuestao.objects.filter(
            execucao__executado_em__lt=cutoff_execucoes
        )

        contas = User.objects.none()
        if options['incluir_contas']:
            contas = (
                User.objects.filter(
                    is_staff=False,
                    anonimizado_em__isnull=True,
                )
                .filter(
                    models_q_inativas(cutoff_execucoes)
                )
                .exclude(retencao_suspensa_ate__gte=timezone.localdate())
            )

        auditoria = EventoAuditoria.objects.none()
        if options['incluir_auditoria']:
            auditoria = EventoAuditoria.objects.filter(
                criado_em__lt=cutoff_auditoria
            )

        totais = {
            'sessoes': sessoes.count(),
            'execucoes': execucoes.count(),
            'respostas': respostas.count(),
            'contas': contas.count(),
            'eventos_auditoria': auditoria.count(),
        }

        self.stdout.write(
            'Retenção: '
            f'mensagens {dias_mensagens}d | execuções {dias_execucoes}d | '
            f'auditoria {dias_auditoria}d. '
            f'Sessões: {totais["sessoes"]} | Execuções: {totais["execucoes"]} | '
            f'Respostas: {totais["respostas"]} | Contas: {totais["contas"]} | '
            f'Eventos: {totais["eventos_auditoria"]}'
        )

        if not options['executar']:
            self.stdout.write(self.style.WARNING(
                'Dry-run: nada foi alterado. Use --executar para aplicar.'
            ))
            return

        from userManagement.services import anonimizar_usuario

        with transaction.atomic():
            sessoes.delete()
            execucoes.update(resposta={})
            respostas.update(resposta_fornecida=None)

            for usuario in contas:
                anonimizar_usuario(usuario)

            if options['incluir_auditoria']:
                auditoria.delete()

        registrar_evento(
            usuario=None,
            acao='EXPURGO_EXECUTADO',
            metadata={
                **totais,
                'dias_mensagens': dias_mensagens,
                'dias_execucoes': dias_execucoes,
                'dias_auditoria': dias_auditoria,
            },
        )

        self.stdout.write(self.style.SUCCESS('Expurgo concluído.'))


def models_q_inativas(cutoff):
    """Contas sem login recente (ou que nunca entraram) antes do cutoff."""
    from django.db.models import Q

    return Q(last_login__lt=cutoff) | Q(last_login__isnull=True, criado_em__lt=cutoff)

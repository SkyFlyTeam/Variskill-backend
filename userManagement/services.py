from datetime import datetime, timedelta
import uuid
from zoneinfo import ZoneInfo
from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from activityManagement.models import ExecucaoAtividade, RespostaQuestao
from .models import ItemCosmetico, RegistroAcessoDiario, User, UsuarioInventario


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


class StreakService:
    @staticmethod
    @transaction.atomic
    def computar_atividade_diaria(usuario, xp_ganho=0, nova_conclusao=True) -> dict:
        """Serviço determinístico de streaks (VAR-105).

        A data corrente é obtida estritamente via timezone.localdate() (data local do
        fuso configurado em TIME_ZONE) para evitar que a virada de dia em UTC, próxima
        da meia-noite em UTC-3, quebre a regra de consecutividade.

        Regras (aplicadas sobre o ultimo_dia_estudo já persistido no usuário):
        - ultimo_dia_estudo == hoje: mantém streak_dias (mesmo dia, sem incrementos repetidos).
        - ultimo_dia_estudo == ontem: streak_dias += 1.
        - ultimo_dia_estudo < ontem ou None: streak_dias = 1.

        Sempre relê streak_dias/maior_streak/ultimo_dia_estudo do banco antes de calcular,
        em vez de confiar no estado em memória de `usuario`: evita um resultado incorreto
        quando o chamador (ou um script manual) alterou esses campos via `.update()` sem
        dar refresh no objeto Python (apontado na review de VAR-105/PR#38).

        `nova_conclusao=False` marca o dia como estudado (streak) mas não incrementa
        `RegistroAcessoDiario.atividades_concluidas`/`xp_obtido` — usado pelo reenvio de
        uma atividade já aprovada anteriormente, para não contar a mesma atividade duas
        vezes no registro diário (ponto 2 da review de VAR-105/PR#38).
        """
        usuario.refresh_from_db(fields=['streak_dias', 'maior_streak', 'ultimo_dia_estudo'])

        hoje = timezone.localdate()
        ontem = hoje - timedelta(days=1)

        if usuario.ultimo_dia_estudo == hoje:
            novo_streak = usuario.streak_dias
        elif usuario.ultimo_dia_estudo == ontem:
            novo_streak = usuario.streak_dias + 1
        else:
            novo_streak = 1

        novo_maior_streak = max(usuario.maior_streak, novo_streak)

        User.objects.filter(pk=usuario.pk).update(
            streak_dias=novo_streak,
            maior_streak=novo_maior_streak,
            ultimo_dia_estudo=hoje,
        )
        usuario.refresh_from_db(fields=['streak_dias', 'maior_streak', 'ultimo_dia_estudo'])

        registro, _ = RegistroAcessoDiario.objects.get_or_create(usuario=usuario, data=hoje)
        if nova_conclusao:
            RegistroAcessoDiario.objects.filter(pk=registro.pk).update(
                atividades_concluidas=F('atividades_concluidas') + 1,
                xp_obtido=F('xp_obtido') + xp_ganho,
            )

        return {
            'streak_dias': usuario.streak_dias,
            'maior_streak': usuario.maior_streak,
            'ultimo_dia_estudo': usuario.ultimo_dia_estudo,
        }


def conceder_itens_padrao(usuarios, itens=None) -> int:
    """Garante que os itens cosméticos padrão estejam no inventário dos usuários.

    Idempotente: vínculos já existentes são ignorados (unique usuario+item).
    Retorna a quantidade de vínculos efetivamente criados.
    """
    if isinstance(usuarios, User):
        usuarios = [usuarios]
    if itens is None:
        itens = list(ItemCosmetico.objects.filter(padrao_desbloqueado=True))
    if not itens:
        return 0

    usuario_ids = [u.pk for u in usuarios]
    existentes = set(
        UsuarioInventario.objects.filter(usuario_id__in=usuario_ids, item__in=itens)
        .values_list('usuario_id', 'item_id')
    )
    novos = [
        UsuarioInventario(usuario_id=uid, item=item)
        for uid in usuario_ids
        for item in itens
        if (uid, item.pk) not in existentes
    ]
    UsuarioInventario.objects.bulk_create(novos, ignore_conflicts=True)
    return len(novos)


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

    responsavel = getattr(usuario, 'aceite_responsavel', None)

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
        'responsavel': (
            {
                'nome': responsavel.nome,
                'cpf': responsavel.cpf,
                'email': responsavel.email,
                'criado_em': responsavel.criado_em,
            }
            if responsavel
            else None
        ),
    }


def _valor_csv(valor):
    """Serializa valores de forma estável para o CSV (sem depender do locale)."""
    import json

    if valor is None:
        return ''
    if isinstance(valor, bool):
        return 'sim' if valor else 'nao'
    if hasattr(valor, 'isoformat'):
        return valor.isoformat()
    if isinstance(valor, (dict, list)):
        return json.dumps(valor, ensure_ascii=False, default=str)
    return str(valor)


def _linhas_csv(secao, valor, registro_id='', prefixo=''):
    """Achata estruturas aninhadas no formato longo secao/registro/campo/valor."""
    if isinstance(valor, dict):
        registro = str(valor.get('id') or registro_id or '')
        for campo, subvalor in valor.items():
            if campo == 'id':
                continue
            nome_campo = f'{prefixo}.{campo}' if prefixo else campo
            yield from _linhas_csv(secao, subvalor, registro, nome_campo)
        return

    if isinstance(valor, list):
        if not valor:
            yield [secao, registro_id, prefixo, '']
            return
        for item in valor:
            if isinstance(item, (dict, list)):
                yield from _linhas_csv(secao, item, registro_id, prefixo)
            else:
                yield [secao, registro_id, prefixo, _valor_csv(item)]
        return

    yield [secao, registro_id or '', prefixo, _valor_csv(valor)]


def exportar_dados_csv(usuario):
    """Gera um único CSV (formato longo) com todos os dados do titular."""
    import csv
    import io

    dados = exportar_dados_usuario(usuario)

    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator='\n')
    writer.writerow(['secao', 'registro_id', 'campo', 'valor'])

    for secao, valor in dados.items():
        if secao == 'exportado_em':
            writer.writerow(['exportacao', '', 'exportado_em', _valor_csv(valor)])
            continue
        for linha in _linhas_csv(secao, valor):
            writer.writerow(linha)

    # BOM para o Excel pt-BR reconhecer UTF-8 (acentos).
    return '\ufeff' + buffer.getvalue()


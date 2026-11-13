import uuid

from django.conf import settings
from django.db import models


class Sessao(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sessoes_assistente', db_column='usuario_id', on_delete=models.CASCADE)
    # Última trilha discutida na conversa; permite que mensagens seguintes ("confirmo", "começar do zero") herdem o contexto.
    trilha_contexto = models.ForeignKey('trackManagement.Trilha', related_name='sessoes_assistente', db_column='trilha_contexto_id', on_delete=models.SET_NULL, null=True, blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'SESSAO'
        indexes = [models.Index(fields=['usuario'], name='sessao_usuario_idx')]


class Mensagem(models.Model):
    class Remetente(models.TextChoices):
        USUARIO = 'USUARIO', 'Usuario'
        ASSISTENTE = 'ASSISTENTE', 'Assistente'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sessao = models.ForeignKey(Sessao, related_name='mensagens', db_column='sessao_id', on_delete=models.CASCADE)
    intencao = models.ForeignKey('intents.Intention', related_name='mensagens', db_column='intencao_id', on_delete=models.SET_NULL, null=True, blank=True)
    remetente = models.CharField(max_length=10, choices=Remetente.choices)
    conteudo = models.TextField()
    distancia = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    # Origem da resposta do assistente (PLN_LOCAL/IA_EXTERNA/CONTINGENCIA), útil para
    # transparência do uso de IA (LGPD) sem alterar o contrato existente.
    origem_resposta = models.CharField(max_length=20, blank=True, default='')
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'MENSAGEM'
        indexes = [models.Index(fields=['sessao'], name='mensagem_sessao_idx')]


class MemoriaPedagogicaUsuario(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='memoria_pedagogica',
        db_column='usuario_id',
    )
    pontos_fortes = models.JSONField(default=list, blank=True)
    topicos_dificuldade = models.JSONField(default=list, blank=True)
    total_atividades_avaliadas = models.PositiveIntegerField(default=0)
    taxa_acerto_geral = models.FloatField(default=0.0)
    resumo_perfil_didatico = models.TextField(blank=True, default='')
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'MEMORIA_PEDAGOGICA_USUARIO'
        verbose_name = 'Memória Pedagógica do Usuário'
        verbose_name_plural = 'Memórias Pedagógicas dos Usuários'

    def __str__(self):
        return f"Memória Pedagógica - {self.usuario}"


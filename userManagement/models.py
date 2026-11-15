import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    username = None
    apelido = models.CharField(max_length=150, unique=True)
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    xp_total = models.IntegerField(default=0)
    streak_dias = models.IntegerField(default=0)
    is_primeiro_acesso = models.BooleanField(default=True)
    sexo = models.CharField(max_length=20, choices=SEXO_CHOICES, null=True, blank=True)
    idade = models.PositiveIntegerField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    aceite_privacidade_versao = models.CharField(max_length=50, null=True, blank=True)
    aceite_privacidade_em = models.DateTimeField(null=True, blank=True)
    consentimento_revogado_em = models.DateTimeField(null=True, blank=True)
    anonimizado_em = models.DateTimeField(null=True, blank=True)
    avatar_equipado = models.ForeignKey(
        'ItemCosmetico', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )
    titulo_equipado = models.ForeignKey(
        'ItemCosmetico', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )
    borda_equipada = models.ForeignKey(
        'ItemCosmetico', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )

    USERNAME_FIELD = 'apelido'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.apelido

    @property
    def consentimento_ativo(self) -> bool:
        return (
            self.aceite_privacidade_em is not None
            and self.consentimento_revogado_em is None
        )


class Interesse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=50, unique=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        db_table = 'INTERESSE'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class UsuarioInteresse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interesses_usuario'
    )
    interesse = models.ForeignKey(
        Interesse, on_delete=models.CASCADE, related_name='usuarios_interessados'
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'USUARIO_INTERESSE'
        unique_together = ('usuario', 'interesse')

    def __str__(self):
        return f"{self.usuario} -> {self.interesse}"


class Conquista(models.Model):
    CATEGORIA_CHOICES = [
        ('PROGRESSO', 'Progresso'),
        ('STREAK', 'Sequência'),
        ('PRECISAO', 'Precisão'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=50, unique=True)
    titulo = models.CharField(max_length=100)
    descricao = models.TextField()
    categoria = models.CharField(max_length=30, choices=CATEGORIA_CHOICES)
    icone = models.CharField(max_length=255)
    xp_recompensa = models.PositiveIntegerField(default=50)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'CONQUISTA'
        ordering = ['ordem']

    def __str__(self):
        return self.titulo


class ItemCosmetico(models.Model):
    TIPO_CHOICES = [
        ('AVATAR', 'Avatar'),
        ('TITULO', 'Título de Honra'),
        ('BORDA', 'Borda de Perfil'),
    ]
    RARIDADE_CHOICES = [
        ('COMUM', 'Comum'),
        ('RARO', 'Raro'),
        ('EPICO', 'Épico'),
        ('LENDARIO', 'Lendário'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    raridade = models.CharField(max_length=20, default='COMUM', choices=RARIDADE_CHOICES)
    recurso_visual = models.CharField(max_length=255)
    asset_url = models.URLField(max_length=500, blank=True)
    conquista_requisito = models.ForeignKey(
        Conquista, null=True, blank=True, on_delete=models.SET_NULL, related_name='itens_cosmeticos'
    )
    padrao_desbloqueado = models.BooleanField(default=False)

    class Meta:
        db_table = 'ITEM_COSMETICO'

    def __str__(self):
        return self.nome


class UsuarioConquista(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conquistas_usuario'
    )
    conquista = models.ForeignKey(
        Conquista, on_delete=models.CASCADE, related_name='usuarios_que_desbloquearam'
    )
    desbloqueado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'USUARIO_CONQUISTA'
        unique_together = ('usuario', 'conquista')

    def __str__(self):
        return f"{self.usuario} -> {self.conquista}"


class UsuarioInventario(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inventario_usuario'
    )
    item = models.ForeignKey(
        ItemCosmetico, on_delete=models.CASCADE, related_name='usuarios_que_possuem'
    )
    desbloqueado_em = models.DateTimeField(auto_now_add=True)
    equipado = models.BooleanField(default=False)

    class Meta:
        db_table = 'USUARIO_INVENTARIO'
        unique_together = ('usuario', 'item')

    def __str__(self):
        return f"{self.usuario} -> {self.item}"


class SolicitacaoRevisao(models.Model):
    TIPO_CHOICES = [
        ('NIVELAMENTO', 'Nivelamento'),
        ('PARECER', 'Parecer formativo'),
        ('RECOMENDACAO', 'Recomendação de trilha'),
    ]
    STATUS_CHOICES = [
        ('ABERTA', 'Aberta'),
        ('REVISADA', 'Revisada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='solicitacoes_revisao'
    )
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
    referencia_id = models.UUIDField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ABERTA')
    criado_em = models.DateTimeField(auto_now_add=True)
    respondido_em = models.DateTimeField(null=True, blank=True)
    resposta = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'SOLICITACAO_REVISAO'
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.usuario} - {self.tipo} ({self.status})"


class EventoAuditoria(models.Model):
    ACAO_CHOICES = [
        ('REQUISICAO', 'Requisição'),
        ('LOGIN', 'Login'),
        ('LOGIN_FALHA', 'Falha de login'),
        ('LOGOUT', 'Logout'),
        ('CADASTRO', 'Cadastro'),
        ('ALTERACAO_PERFIL', 'Alteração de perfil'),
        ('CONSENTIMENTO_CONCEDIDO', 'Consentimento concedido'),
        ('CONSENTIMENTO_REVOGADO', 'Consentimento revogado'),
        ('EXPORTACAO_DADOS', 'Exportação de dados'),
        ('ANONIMIZACAO_CONTA', 'Anonimização de conta'),
        ('HARD_DELETE', 'Exclusão definitiva'),
        ('TROCA_SENHA', 'Troca de senha'),
        ('REVISAO_SOLICITADA', 'Revisão solicitada'),
        ('REVISAO_RESPONDIDA', 'Revisão respondida'),
        ('EXPURGO_EXECUTADO', 'Expurgo executado'),
    ]
    RESULTADO_CHOICES = [
        ('SUCESSO', 'Sucesso'),
        ('FALHA', 'Falha'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='eventos_auditoria',
    )
    # Snapshot do e-mail/identificador no momento do evento: preserva a evidência
    # mesmo se a conta for anonimizada ou apagada. Não guardar senha/token/conteúdo.
    ator_email = models.CharField(max_length=254, blank=True, default='')
    ator_is_staff = models.BooleanField(default=False)
    acao = models.CharField(max_length=40, choices=ACAO_CHOICES)
    metodo = models.CharField(max_length=10, blank=True, default='')
    rota = models.CharField(max_length=500, blank=True, default='')
    status_code = models.PositiveSmallIntegerField(null=True, blank=True)
    resultado = models.CharField(max_length=20, choices=RESULTADO_CHOICES, default='SUCESSO')
    recurso = models.CharField(max_length=40, blank=True, default='')
    recurso_id = models.UUIDField(null=True, blank=True)
    ip_hash = models.CharField(max_length=64, blank=True, default='')
    user_agent = models.TextField(blank=True, default='')
    metadata = models.JSONField(default=dict, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'EVENTO_AUDITORIA'
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['usuario', 'criado_em'], name='auditoria_usuario_idx'),
            models.Index(fields=['acao', 'criado_em'], name='auditoria_acao_idx'),
            models.Index(fields=['criado_em'], name='auditoria_data_idx'),
        ]

    def __str__(self):
        return f"{self.criado_em} - {self.acao} - {self.ator_email or 'sistema'}"

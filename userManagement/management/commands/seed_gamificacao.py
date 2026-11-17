from django.core.management.base import BaseCommand
from django.db import transaction

from userManagement.models import Conquista, ItemCosmetico, User
from userManagement.services import conceder_itens_padrao

CONQUISTAS = [
    {
        'codigo': 'PRIMEIRO_PASSO',
        'titulo': 'Primeiro Passo',
        'descricao': 'Concluiu a primeira atividade.',
        'categoria': 'PROGRESSO',
        'icone': 'conquistas/primeiro_passo.svg',
        'xp_recompensa': 50,
    },
    {
        'codigo': 'DEDICACAO_INICIAL',
        'titulo': 'Fogo Aceso',
        'descricao': 'Estudou por 3 dias seguidos.',
        'categoria': 'STREAK',
        'icone': 'conquistas/fogo_aceso.svg',
        'xp_recompensa': 100,
    },
    {
        'codigo': 'HABITO_DE_FERRO',
        'titulo': 'Semana Vitoriosa',
        'descricao': 'Estudou por 7 dias seguidos.',
        'categoria': 'STREAK',
        'icone': 'conquistas/semana_vitoriosa.svg',
        'xp_recompensa': 250,
    },
    {
        'codigo': 'PRECISAO_MAXIMA',
        'titulo': 'Tiro Certeiro',
        'descricao': 'Acertou 100% de uma bateria de questões sem errar.',
        'categoria': 'PRECISAO',
        'icone': 'conquistas/tiro_certeiro.svg',
        'xp_recompensa': 150,
    },
    {
        'codigo': 'EXPLORADOR_MODULO',
        'titulo': 'Módulo Concluído',
        'descricao': 'Finalizou todos os tópicos de um módulo.',
        'categoria': 'PROGRESSO',
        'icone': 'conquistas/modulo_concluido.svg',
        'xp_recompensa': 100,
    },
    {
        'codigo': 'MESTRE_TRILHA',
        'titulo': 'Trilha Completa',
        'descricao': 'Concluiu uma trilha de aprendizagem.',
        'categoria': 'PROGRESSO',
        'icone': 'conquistas/trilha_completa.svg',
        'xp_recompensa': 500,
    },
]

# conquista=None => item padrão (padrao_desbloqueado=True)
ITENS_COSMETICOS = [
    # Avatares
    {
        'nome': 'Vari Clássico', 'tipo': 'AVATAR', 'raridade': 'COMUM',
        'descricao': 'O Vari de sempre, pronto para estudar.',
        'recurso_visual': 'avatares/vari_classico.png', 'conquista': None,
    },
    {
        'nome': 'Vari Estudioso', 'tipo': 'AVATAR', 'raridade': 'COMUM',
        'descricao': 'Desbloqueado ao concluir a primeira atividade.',
        'recurso_visual': 'avatares/vari_estudioso.png', 'conquista': 'PRIMEIRO_PASSO',
    },
    {
        'nome': 'Vari Sensei', 'tipo': 'AVATAR', 'raridade': 'LENDARIO',
        'descricao': 'Desbloqueado ao concluir uma trilha de aprendizagem.',
        'recurso_visual': 'avatares/vari_sensei.png', 'conquista': 'MESTRE_TRILHA',
    },
    {
        'nome': 'Vari Cyberpunk', 'tipo': 'AVATAR', 'raridade': 'EPICO',
        'descricao': 'Desbloqueado ao finalizar todos os tópicos de um módulo.',
        'recurso_visual': 'avatares/vari_cyberpunk.png', 'conquista': 'EXPLORADOR_MODULO',
    },
    # Títulos
    {
        'nome': 'Estudante VariSkill', 'tipo': 'TITULO', 'raridade': 'COMUM',
        'descricao': 'Título inicial de todo estudante.',
        'recurso_visual': 'titulos/estudante_variskill', 'conquista': None,
    },
    {
        'nome': 'Iniciante Imparável', 'tipo': 'TITULO', 'raridade': 'RARO',
        'descricao': 'Desbloqueado ao manter 3 dias seguidos de estudo.',
        'recurso_visual': 'titulos/iniciante_imparavel', 'conquista': 'DEDICACAO_INICIAL',
    },
    {
        'nome': 'Explorador de Código', 'tipo': 'TITULO', 'raridade': 'RARO',
        'descricao': 'Desbloqueado ao finalizar todos os tópicos de um módulo.',
        'recurso_visual': 'titulos/explorador_de_codigo', 'conquista': 'EXPLORADOR_MODULO',
    },
    {
        'nome': 'Mestre da Lógica', 'tipo': 'TITULO', 'raridade': 'EPICO',
        'descricao': 'Desbloqueado ao acertar 100% de uma bateria de questões.',
        'recurso_visual': 'titulos/mestre_da_logica', 'conquista': 'PRECISAO_MAXIMA',
    },
    # Bordas
    {
        'nome': 'Borda Básica', 'tipo': 'BORDA', 'raridade': 'COMUM',
        'descricao': 'Borda padrão do perfil.',
        'recurso_visual': 'bordas/basica.png', 'conquista': None,
    },
    {
        'nome': 'Borda Flamejante', 'tipo': 'BORDA', 'raridade': 'EPICO',
        'descricao': 'Desbloqueada ao manter 7 dias seguidos de estudo.',
        'recurso_visual': 'bordas/flamejante.png', 'conquista': 'HABITO_DE_FERRO',
    },
    {
        'nome': 'Borda Neon', 'tipo': 'BORDA', 'raridade': 'RARO',
        'descricao': 'Desbloqueada ao acertar 100% de uma bateria de questões.',
        'recurso_visual': 'bordas/neon.png', 'conquista': 'PRECISAO_MAXIMA',
    },
]


class Command(BaseCommand):
    help = (
        'Cadastra conquistas e itens cosméticos iniciais da gamificação e garante '
        'que todos os usuários possuam os itens padrão no inventário. Idempotente.'
    )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Iniciando seed de gamificação...')

        conquistas = self._seed_conquistas()
        itens_padrao = self._seed_itens(conquistas)

        usuarios = list(User.objects.only('pk'))
        criados = conceder_itens_padrao(usuarios, itens=itens_padrao)
        self.stdout.write(
            f'  Inventário: {criados} vínculo(s) de itens padrão criado(s) '
            f'para {len(usuarios)} usuário(s).'
        )

        self.stdout.write(self.style.SUCCESS('Seed de gamificação concluído.'))

    def _seed_conquistas(self):
        conquistas = {}
        for ordem, dados in enumerate(CONQUISTAS, start=1):
            dados = dict(dados)
            codigo = dados.pop('codigo')
            conquista, created = Conquista.objects.update_or_create(
                codigo=codigo, defaults={**dados, 'ordem': ordem}
            )
            conquistas[codigo] = conquista
            self._log('Conquista', conquista.titulo, created)
        return conquistas

    def _seed_itens(self, conquistas):
        itens_padrao = []
        for dados in ITENS_COSMETICOS:
            dados = dict(dados)
            codigo_conquista = dados.pop('conquista')
            nome = dados.pop('nome')
            tipo = dados.pop('tipo')
            padrao = codigo_conquista is None
            # nome não é unique no model; (nome, tipo) é a chave natural do seed.
            item, created = ItemCosmetico.objects.update_or_create(
                nome=nome,
                tipo=tipo,
                defaults={
                    **dados,
                    'padrao_desbloqueado': padrao,
                    'conquista_requisito': None if padrao else conquistas[codigo_conquista],
                },
            )
            if padrao:
                itens_padrao.append(item)
            self._log(f'Item {tipo}', nome, created)
        return itens_padrao

    def _log(self, tipo, nome, created):
        if created:
            self.stdout.write(self.style.SUCCESS(f"  {tipo} criado: '{nome}'"))
        else:
            self.stdout.write(f"  {tipo} atualizado: '{nome}'")

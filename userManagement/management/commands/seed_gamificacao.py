from django.core.management.base import BaseCommand
from django.db import transaction

from userManagement.models import Conquista, ItemCosmetico, User
from userManagement.services import conceder_itens_padrao
from settings.s3_storage import default_storage_service
import io



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

    def _garantir_asset_no_storage(self, recurso_visual: str, nome: str) -> str:
        """
        Verifica se o asset já existe no storage (S3 ou local).
        Se não existir, faz o upload físico do asset para o storage e só então retorna o link!
        """
        if not recurso_visual:
            return ''

        # Se já existir fisicamente no bucket / storage local, apenas retorna a URL
        if default_storage_service.exists(recurso_visual):
            return default_storage_service.get_asset_url(recurso_visual)

        # Se não existe, provisiona o arquivo real no storage
        ext = recurso_visual.split('.')[-1].lower() if '.' in recurso_visual else 'png'
        content_type = 'image/svg+xml' if ext == 'svg' else 'image/png'

        if ext == 'svg':
            conteudo_arquivo = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y="50">{nome}</text></svg>'.encode('utf-8')
        else:
            # 1x1 PNG mínimo válido
            conteudo_arquivo = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'

        url = default_storage_service.upload_asset(
            file_content=io.BytesIO(conteudo_arquivo),
            s3_key=recurso_visual,
            content_type=content_type,
        )
        self.stdout.write(self.style.SUCCESS(f"  [Storage] Asset '{recurso_visual}' enviado para o bucket!"))
        return url

    def _seed_itens(self, conquistas):
        itens_padrao = []
        for dados in ITENS_COSMETICOS:
            dados = dict(dados)
            codigo_conquista = dados.pop('conquista')
            nome = dados.pop('nome')
            tipo = dados.pop('tipo')
            padrao = codigo_conquista is None
            recurso_visual = dados.get('recurso_visual', '')

            # Garante que o objeto existe fisicamente no bucket/storage antes de salvar a URL no banco
            asset_url = self._garantir_asset_no_storage(recurso_visual, nome)

            # nome não é unique no model; (nome, tipo) é a chave natural do seed.
            item, created = ItemCosmetico.objects.update_or_create(
                nome=nome,
                tipo=tipo,
                defaults={
                    **dados,
                    'asset_url': asset_url,
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

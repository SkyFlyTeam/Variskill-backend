from io import StringIO

import pytest
from django.core.management import call_command
from model_bakery import baker

from userManagement.management.commands.seed_gamificacao import CONQUISTAS, ITENS_COSMETICOS
from userManagement.models import Conquista, ItemCosmetico, User, UsuarioInventario

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def _seed():
    call_command('seed_gamificacao', stdout=StringIO())


def test_seed_cria_conquistas_e_itens():
    _seed()

    assert Conquista.objects.count() == len(CONQUISTAS)
    assert ItemCosmetico.objects.count() == len(ITENS_COSMETICOS)
    assert Conquista.objects.get(codigo='HABITO_DE_FERRO').xp_recompensa == 250


def test_seed_e_idempotente():
    usuario = baker.make(User)
    _seed()
    _seed()

    assert Conquista.objects.count() == len(CONQUISTAS)
    assert ItemCosmetico.objects.count() == len(ITENS_COSMETICOS)
    assert UsuarioInventario.objects.filter(usuario=usuario).count() == 3


def test_vinculos_de_conquista_resolvidos():
    _seed()

    padroes = ItemCosmetico.objects.filter(padrao_desbloqueado=True)
    assert set(padroes.values_list('nome', flat=True)) == {
        'Vari Clássico', 'Estudante VariSkill', 'Borda Básica',
    }
    assert not padroes.filter(conquista_requisito__isnull=False).exists()
    assert not ItemCosmetico.objects.filter(
        padrao_desbloqueado=False, conquista_requisito__isnull=True
    ).exists()
    assert (
        ItemCosmetico.objects.get(nome='Borda Flamejante').conquista_requisito.codigo
        == 'HABITO_DE_FERRO'
    )


def test_seed_concede_itens_padrao_a_usuarios_existentes():
    usuario = baker.make(User)
    _seed()

    nomes = set(
        UsuarioInventario.objects.filter(usuario=usuario).values_list('item__nome', flat=True)
    )
    assert nomes == {'Vari Clássico', 'Estudante VariSkill', 'Borda Básica'}


def test_novo_usuario_recebe_itens_padrao_automaticamente():
    _seed()
    usuario = User.objects.create_user(apelido='novato', password='senha-forte-123', email='n@x.com')

    assert UsuarioInventario.objects.filter(
        usuario=usuario, item__padrao_desbloqueado=True
    ).count() == 3


def _nomes_equipados(usuario):
    usuario.refresh_from_db()
    return (
        usuario.avatar_equipado.nome,
        usuario.titulo_equipado.nome,
        usuario.borda_equipada.nome,
    )


def test_novo_usuario_ja_vem_com_itens_padrao_equipados():
    _seed()
    usuario = User.objects.create_user(apelido='novato', password='senha-forte-123', email='n@x.com')

    assert _nomes_equipados(usuario) == ('Vari Clássico', 'Estudante VariSkill', 'Borda Básica')
    assert set(
        UsuarioInventario.objects.filter(usuario=usuario, equipado=True)
        .values_list('item__nome', flat=True)
    ) == {'Vari Clássico', 'Estudante VariSkill', 'Borda Básica'}


def test_seed_equipa_padroes_em_usuarios_existentes_sem_sobrescrever_escolhas():
    usuario = baker.make(User)
    _seed()
    titulo_escolhido = ItemCosmetico.objects.get(nome='Mestre da Lógica')
    UsuarioInventario.objects.create(usuario=usuario, item=titulo_escolhido, equipado=True)
    UsuarioInventario.objects.filter(usuario=usuario, item__tipo='TITULO').exclude(
        item=titulo_escolhido
    ).update(equipado=False)
    User.objects.filter(pk=usuario.pk).update(titulo_equipado=titulo_escolhido)

    _seed()

    assert _nomes_equipados(usuario) == ('Vari Clássico', 'Mestre da Lógica', 'Borda Básica')

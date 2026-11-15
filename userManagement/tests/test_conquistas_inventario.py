import pytest
from django.db import IntegrityError
from model_bakery import baker

from userManagement.models import Conquista, ItemCosmetico, User, UsuarioConquista, UsuarioInventario

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def usuario():
    return baker.make(User)


@pytest.fixture
def conquista():
    return Conquista.objects.create(
        codigo='PRIMEIRO_PASSO',
        titulo='Primeiro Passo',
        descricao='Concluiu a primeira atividade.',
        categoria='PROGRESSO',
        icone='icone-primeiro-passo.svg',
    )


@pytest.fixture
def item_cosmetico():
    return ItemCosmetico.objects.create(
        nome='Avatar Padrão',
        tipo='AVATAR',
        recurso_visual='avatares/padrao.png',
    )


def test_conquista_codigo_e_unico(conquista):
    with pytest.raises(IntegrityError):
        Conquista.objects.create(
            codigo='PRIMEIRO_PASSO',
            titulo='Duplicada',
            descricao='...',
            categoria='STREAK',
            icone='icone.svg',
        )


def test_item_cosmetico_pode_exigir_uma_conquista(conquista):
    item = ItemCosmetico.objects.create(
        nome='Borda Dourada',
        tipo='BORDA',
        recurso_visual='bordas/dourada.png',
        conquista_requisito=conquista,
    )

    assert item.conquista_requisito == conquista
    assert conquista.itens_cosmeticos.filter(pk=item.pk).exists()


def test_apagar_conquista_requisito_nao_apaga_o_item_cosmetico(conquista):
    item = ItemCosmetico.objects.create(
        nome='Borda Dourada',
        tipo='BORDA',
        recurso_visual='bordas/dourada.png',
        conquista_requisito=conquista,
    )

    conquista.delete()
    item.refresh_from_db()

    assert item.conquista_requisito is None


def test_usuario_conquista_unique_together(usuario, conquista):
    UsuarioConquista.objects.create(usuario=usuario, conquista=conquista)

    with pytest.raises(IntegrityError):
        UsuarioConquista.objects.create(usuario=usuario, conquista=conquista)


def test_apagar_usuario_apaga_suas_usuario_conquista_em_cascata(usuario, conquista):
    registro = UsuarioConquista.objects.create(usuario=usuario, conquista=conquista)

    usuario.delete()

    assert not UsuarioConquista.objects.filter(pk=registro.pk).exists()


def test_apagar_conquista_apaga_as_usuario_conquista_relacionadas_em_cascata(usuario, conquista):
    registro = UsuarioConquista.objects.create(usuario=usuario, conquista=conquista)

    conquista.delete()

    assert not UsuarioConquista.objects.filter(pk=registro.pk).exists()


def test_usuario_inventario_unique_together(usuario, item_cosmetico):
    UsuarioInventario.objects.create(usuario=usuario, item=item_cosmetico)

    with pytest.raises(IntegrityError):
        UsuarioInventario.objects.create(usuario=usuario, item=item_cosmetico)


def test_apagar_usuario_apaga_seu_usuario_inventario_em_cascata(usuario, item_cosmetico):
    registro = UsuarioInventario.objects.create(usuario=usuario, item=item_cosmetico)

    usuario.delete()

    assert not UsuarioInventario.objects.filter(pk=registro.pk).exists()


def test_apagar_item_cosmetico_apaga_os_usuario_inventario_relacionados_em_cascata(usuario, item_cosmetico):
    registro = UsuarioInventario.objects.create(usuario=usuario, item=item_cosmetico)

    item_cosmetico.delete()

    assert not UsuarioInventario.objects.filter(pk=registro.pk).exists()


def test_usuario_pode_equipar_avatar_titulo_e_borda_simultaneamente(usuario):
    avatar = ItemCosmetico.objects.create(nome='Avatar', tipo='AVATAR', recurso_visual='a.png')
    titulo = ItemCosmetico.objects.create(nome='Título', tipo='TITULO', recurso_visual='t.png')
    borda = ItemCosmetico.objects.create(nome='Borda', tipo='BORDA', recurso_visual='b.png')

    usuario.avatar_equipado = avatar
    usuario.titulo_equipado = titulo
    usuario.borda_equipada = borda
    usuario.save()

    usuario.refresh_from_db()
    assert usuario.avatar_equipado == avatar
    assert usuario.titulo_equipado == titulo
    assert usuario.borda_equipada == borda


def test_apagar_item_cosmetico_equipado_desequipa_o_usuario_sem_apagar_o_usuario(usuario):
    avatar = ItemCosmetico.objects.create(nome='Avatar', tipo='AVATAR', recurso_visual='a.png')
    usuario.avatar_equipado = avatar
    usuario.save()

    avatar.delete()
    usuario.refresh_from_db()

    assert usuario.avatar_equipado is None
    assert User.objects.filter(pk=usuario.pk).exists()

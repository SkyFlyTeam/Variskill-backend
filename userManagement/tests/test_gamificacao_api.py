import pytest
from django.urls import reverse
from django.utils.dateparse import parse_datetime
from model_bakery import baker

from userManagement.models import (
    Conquista,
    ItemCosmetico,
    User,
    UsuarioConquista,
    UsuarioInventario,
)

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def usuario():
    return baker.make(User)


@pytest.fixture
def cliente(client, usuario):
    client.force_login(usuario)
    return client


def _conquista(codigo, ordem):
    return Conquista.objects.create(
        codigo=codigo, titulo=codigo.title(), descricao='...',
        categoria='PROGRESSO', icone='icone.svg', ordem=ordem,
    )


def _item(nome, tipo):
    return ItemCosmetico.objects.create(nome=nome, tipo=tipo, recurso_visual=f'{nome}.png')


def _equipar_url(registro):
    return reverse('gamificacao-inventario-equipar', kwargs={'inventario_id': registro.pk})


def test_endpoints_exigem_autenticacao(client):
    registro = UsuarioInventario.objects.create(usuario=baker.make(User), item=_item('a', 'AVATAR'))
    assert client.get(reverse('gamificacao-conquistas')).status_code in (401, 403)
    assert client.get(reverse('gamificacao-inventario')).status_code in (401, 403)
    assert client.post(_equipar_url(registro)).status_code in (401, 403)


def test_lista_conquistas_ordenadas_com_status_de_desbloqueio(cliente, usuario):
    segunda = _conquista('SEGUNDA', 2)
    primeira = _conquista('PRIMEIRA', 1)
    desbloqueio = UsuarioConquista.objects.create(usuario=usuario, conquista=segunda)
    UsuarioConquista.objects.create(usuario=baker.make(User), conquista=primeira)

    response = cliente.get(reverse('gamificacao-conquistas'))

    assert response.status_code == 200
    dados = response.json()
    assert [c['codigo'] for c in dados] == ['PRIMEIRA', 'SEGUNDA']
    assert dados[0]['desbloqueada'] is False
    assert dados[0]['desbloqueada_em'] is None
    assert dados[1]['desbloqueada'] is True
    assert dados[1]['desbloqueada_em'] is not None
    assert parse_datetime(dados[1]['desbloqueada_em']) == desbloqueio.desbloqueado_em


def test_inventario_agrupado_por_categoria(cliente, usuario):
    avatar = _item('avatar', 'AVATAR')
    titulo = _item('titulo', 'TITULO')
    _item('fora_do_inventario', 'BORDA')
    inv_avatar = UsuarioInventario.objects.create(usuario=usuario, item=avatar, equipado=True)
    inv_titulo = UsuarioInventario.objects.create(usuario=usuario, item=titulo)
    UsuarioInventario.objects.create(usuario=baker.make(User), item=_item('alheio', 'BORDA'))

    response = cliente.get(reverse('gamificacao-inventario'))

    assert response.status_code == 200
    dados = response.json()
    assert set(dados) == {'avatares', 'titulos', 'bordas'}
    assert [(i['id'], i['item_id'], i['equipado']) for i in dados['avatares']] == [
        (str(inv_avatar.pk), str(avatar.pk), True)
    ]
    assert [(i['id'], i['item_id'], i['equipado']) for i in dados['titulos']] == [
        (str(inv_titulo.pk), str(titulo.pk), False)
    ]
    assert dados['bordas'] == []


def test_equipar_item_desequipa_anterior_do_mesmo_tipo(cliente, usuario):
    antigo = _item('antigo', 'AVATAR')
    novo = _item('novo', 'AVATAR')
    titulo = _item('titulo', 'TITULO')
    inv_antigo = UsuarioInventario.objects.create(usuario=usuario, item=antigo, equipado=True)
    inv_novo = UsuarioInventario.objects.create(usuario=usuario, item=novo)
    inv_titulo = UsuarioInventario.objects.create(usuario=usuario, item=titulo, equipado=True)
    usuario.avatar_equipado = antigo
    usuario.titulo_equipado = titulo
    usuario.save()

    response = cliente.post(_equipar_url(inv_novo))

    assert response.status_code == 200
    assert response.json() == {'sucesso': True, 'item_equipado_id': str(inv_novo.pk), 'tipo': 'AVATAR'}
    inv_antigo.refresh_from_db()
    inv_novo.refresh_from_db()
    inv_titulo.refresh_from_db()
    usuario.refresh_from_db()
    assert inv_novo.equipado is True
    assert inv_antigo.equipado is False
    assert inv_titulo.equipado is True
    assert usuario.avatar_equipado == novo
    assert usuario.titulo_equipado == titulo


@pytest.mark.parametrize('tipo,campo', [
    ('AVATAR', 'avatar_equipado'),
    ('TITULO', 'titulo_equipado'),
    ('BORDA', 'borda_equipada'),
])
def test_equipar_atualiza_fk_correspondente(cliente, usuario, tipo, campo):
    item = _item('item', tipo)
    registro = UsuarioInventario.objects.create(usuario=usuario, item=item)

    response = cliente.post(_equipar_url(registro))

    assert response.status_code == 200
    assert response.json()['tipo'] == tipo
    usuario.refresh_from_db()
    assert getattr(usuario, campo) == item


def test_equipar_item_fora_do_inventario_retorna_404(cliente, usuario):
    item = _item('alheio', 'AVATAR')
    registro_alheio = UsuarioInventario.objects.create(usuario=baker.make(User), item=item)

    response = cliente.post(_equipar_url(registro_alheio))

    assert response.status_code == 404
    registro_alheio.refresh_from_db()
    assert registro_alheio.equipado is False
    usuario.refresh_from_db()
    assert usuario.avatar_equipado is None
    assert not UsuarioInventario.objects.filter(usuario=usuario).exists()


def test_equipar_item_inexistente_retorna_404(cliente):
    url = reverse(
        'gamificacao-inventario-equipar',
        kwargs={'inventario_id': '00000000-0000-0000-0000-000000000000'},
    )
    assert cliente.post(url).status_code == 404

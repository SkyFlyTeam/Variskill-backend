from io import StringIO

import pytest
from django.core.management import call_command
from model_bakery import baker

from activityManagement.models import Atividade, ExecucaoAtividade
from questionsManagement.models import Questao
from trackManagement.models import Modulo, Trilha
from userManagement.gamification_engine import GamificationEngine
from userManagement.models import User, UsuarioConquista, UsuarioInventario

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture(autouse=True)
def seed():
    call_command('seed_gamificacao', stdout=StringIO())


@pytest.fixture
def usuario():
    return baker.make(User, xp_total=0)


@pytest.fixture
def engine():
    return GamificationEngine()


@pytest.fixture
def modulo():
    return baker.make(Modulo, trilha=baker.make(Trilha))


def _atividade_com_questao(modulo, xp=100):
    atividade = baker.make(Atividade, modulo=modulo, xp_recompensa=xp, ativo=True)
    questao = baker.make(
        Questao, atividade=atividade, tipo_exercicio='MULTIPLA_ESCOLHA',
        gabarito_esperado='A', peso_pontuacao=10,
    )
    return atividade, questao


def _codigos(conquistas):
    return {c['codigo'] for c in conquistas}


def test_evento_desconhecido_levanta_erro(engine, usuario):
    with pytest.raises(ValueError):
        engine.avaliar_conquistas_usuario(usuario, 'XYZ', {})


def test_atividade_concluida_concede_primeiro_passo_e_precisao(engine, usuario, modulo):
    atividade = baker.make(Atividade, modulo=modulo)
    baker.make(ExecucaoAtividade, usuario=usuario, atividade=atividade, aprovado=True, resposta={})

    result = engine.avaliar_conquistas_usuario(
        usuario, 'ATIVIDADE_CONCLUIDA', {'aprovado': True, 'taxa_acerto': 100.0}
    )

    assert _codigos(result) == {'PRIMEIRO_PASSO', 'PRECISAO_MAXIMA'}
    usuario.refresh_from_db()
    assert usuario.xp_total == 50 + 150


def test_atividade_reprovada_nao_concede(engine, usuario):
    result = engine.avaliar_conquistas_usuario(
        usuario, 'ATIVIDADE_CONCLUIDA', {'aprovado': False, 'taxa_acerto': 100.0}
    )
    assert result == []


def test_nao_concede_em_duplicidade(engine, usuario):
    primeiro = engine.avaliar_conquistas_usuario(usuario, 'STREAK_ATUALIZADO', {'streak_dias': 3})
    segundo = engine.avaliar_conquistas_usuario(usuario, 'STREAK_ATUALIZADO', {'streak_dias': 3})

    assert _codigos(primeiro) == {'DEDICACAO_INICIAL'}
    assert segundo == []
    assert UsuarioConquista.objects.filter(usuario=usuario).count() == 1
    usuario.refresh_from_db()
    assert usuario.xp_total == 100


def test_streak_7_concede_marcos_e_item_cosmetico(engine, usuario):
    result = engine.avaliar_conquistas_usuario(usuario, 'STREAK_ATUALIZADO', {'streak_dias': 7})

    assert _codigos(result) == {'DEDICACAO_INICIAL', 'HABITO_DE_FERRO'}
    habito = next(c for c in result if c['codigo'] == 'HABITO_DE_FERRO')
    assert habito['item_desbloqueado']['nome'] == 'Borda Flamejante'
    inv = UsuarioInventario.objects.get(usuario=usuario, item__nome='Borda Flamejante')
    assert inv.equipado is False


def test_modulo_incompleto_nao_concede(engine, usuario, modulo):
    a1 = baker.make(Atividade, modulo=modulo, ativo=True)
    baker.make(Atividade, modulo=modulo, ativo=True)
    baker.make(ExecucaoAtividade, usuario=usuario, atividade=a1, aprovado=True, resposta={})

    result = engine.avaliar_conquistas_usuario(usuario, 'MODULO_CONCLUIDO', {'modulo_id': modulo.pk})
    assert result == []


def test_submissao_ultima_atividade_do_modulo_dispara_atividade_e_modulo(client, usuario, modulo):
    a1, q1 = _atividade_com_questao(modulo)
    a2, q2 = _atividade_com_questao(modulo)
    client.force_login(usuario)

    r1 = client.post(f'/api/atividades/{a1.pk}/submeter/', {'respostas': {str(q1.pk): ['A']}},
                     content_type='application/json')
    assert r1.status_code == 200
    assert _codigos(r1.json()['conquistas_desbloqueadas']) == {'PRIMEIRO_PASSO', 'PRECISAO_MAXIMA'}

    r2 = client.post(f'/api/atividades/{a2.pk}/submeter/', {'respostas': {str(q2.pk): ['A']}},
                     content_type='application/json')
    assert r2.status_code == 200
    body = r2.json()
    assert _codigos(body['conquistas_desbloqueadas']) == {'EXPLORADOR_MODULO'}

    conquista = body['conquistas_desbloqueadas'][0]
    assert set(conquista) >= {
        'id', 'codigo', 'titulo', 'descricao', 'icone', 'xp_recompensa', 'item_desbloqueado',
    }
    assert set(conquista['item_desbloqueado']) == {'id', 'nome', 'tipo', 'asset_url'}

    # 2 atividades (100 cada) + PRIMEIRO_PASSO (50) + PRECISAO_MAXIMA (150) + EXPLORADOR_MODULO (100)
    usuario.refresh_from_db()
    assert usuario.xp_total == 200 + 50 + 150 + 100
    assert body['novo_xp_total'] == usuario.xp_total


def test_submissao_modulo_de_uma_atividade_concede_tudo_de_uma_vez(client, usuario, modulo):
    a1, q1 = _atividade_com_questao(modulo)
    client.force_login(usuario)

    r = client.post(f'/api/atividades/{a1.pk}/submeter/', {'respostas': {str(q1.pk): ['A']}},
                    content_type='application/json')

    assert _codigos(r.json()['conquistas_desbloqueadas']) == {
        'PRIMEIRO_PASSO', 'PRECISAO_MAXIMA', 'EXPLORADOR_MODULO',
    }


def test_resubmissao_nao_duplica_conquistas(client, usuario, modulo):
    a1, q1 = _atividade_com_questao(modulo)
    client.force_login(usuario)
    url = f'/api/atividades/{a1.pk}/submeter/'
    payload = {'respostas': {str(q1.pk): ['A']}}

    client.post(url, payload, content_type='application/json')
    usuario.refresh_from_db()
    xp_apos_primeira = usuario.xp_total

    r = client.post(url, payload, content_type='application/json')

    assert r.json()['conquistas_desbloqueadas'] == []
    usuario.refresh_from_db()
    assert usuario.xp_total == xp_apos_primeira
    assert UsuarioConquista.objects.filter(usuario=usuario).count() == 3

import threading
from datetime import timedelta
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest
from django.conf import settings
from django.db import connection, transaction
from django.utils import timezone
from model_bakery import baker

from activityManagement.models import Atividade, ExecucaoAtividade
from trackManagement.models import Modulo, Trilha
from questionsManagement.models import Questao
from userManagement.models import User
from userManagement.services import GamificationService

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def service():
    return GamificationService()


@pytest.fixture
def usuario():
    return baker.make(User, xp_total=100, streak_dias=0)


@pytest.fixture
def atividade():
    return baker.make(Atividade, xp_recompensa=50)


def test_creditar_xp_atomic(service, usuario, atividade):
    novo_xp = service.creditar_xp(usuario, atividade)
    assert novo_xp == 150
    usuario.refresh_from_db()
    assert usuario.xp_total == 150


@pytest.mark.django_db(transaction=True)
def test_creditar_xp_concorrencia_multithread(atividade):
    user = baker.make(User, xp_total=0)
    user_id = user.pk
    atividade_id = atividade.pk
    threads = []
    num_threads = 10
    xp_por_thread = atividade.xp_recompensa

    def worker():
        u = User.objects.get(pk=user_id)
        a = Atividade.objects.get(pk=atividade_id)
        GamificationService().creditar_xp(u, a)

    for _ in range(num_threads):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    user.refresh_from_db()
    assert user.xp_total == num_threads * xp_por_thread



def test_atualizar_streak_primeiro_acesso(service, usuario):
    streak = service.atualizar_streak(usuario)
    assert streak == 1
    usuario.refresh_from_db()
    assert usuario.streak_dias == 1


def test_atualizar_streak_mesmo_dia(service, usuario):
    tz = ZoneInfo(getattr(settings, 'TIME_ZONE', 'America/Sao_Paulo'))
    hoje = timezone.now().astimezone(tz).date()
    usuario.streak_dias = 3
    usuario.save()

    streak = service.atualizar_streak(usuario, data_referencia=hoje)
    assert streak == 3
    usuario.refresh_from_db()
    assert usuario.streak_dias == 3


def test_atualizar_streak_dia_consecutivo(service, usuario):
    tz = ZoneInfo(getattr(settings, 'TIME_ZONE', 'America/Sao_Paulo'))
    hoje = timezone.now().astimezone(tz).date()
    ontem = hoje - timedelta(days=1)
    usuario.streak_dias = 3
    usuario.save()

    streak = service.atualizar_streak(usuario, data_referencia=ontem)
    assert streak == 4
    usuario.refresh_from_db()
    assert usuario.streak_dias == 4


def test_atualizar_streak_reset_mais_de_um_dia(service, usuario):
    tz = ZoneInfo(getattr(settings, 'TIME_ZONE', 'America/Sao_Paulo'))
    hoje = timezone.now().astimezone(tz).date()
    antes_de_ontem = hoje - timedelta(days=2)
    usuario.streak_dias = 5
    usuario.save()

    streak = service.atualizar_streak(usuario, data_referencia=antes_de_ontem)
    assert streak == 1
    usuario.refresh_from_db()
    assert usuario.streak_dias == 1


def test_atualizar_streak_fuso_horario_sao_paulo(service, usuario):
    # Simula 23h30 em Sao Paulo (que em UTC eh 02h30 do dia seguinte)
    tz_sp = ZoneInfo('America/Sao_Paulo')
    dt_sp_23h30 = timezone.datetime(2026, 9, 24, 23, 30, tzinfo=tz_sp)

    # 1. Primeiro acesso a noite em Sao Paulo
    with patch('django.utils.timezone.now', return_value=dt_sp_23h30):
        streak1 = service.atualizar_streak(usuario)
        assert streak1 == 1

    # 2. Acesso no dia seguinte em Sao Paulo (23h45 do dia consecutivo)
    dt_sp_dia_seguinte = dt_sp_23h30 + timedelta(days=1)
    with patch('django.utils.timezone.now', return_value=dt_sp_dia_seguinte):
        streak2 = service.atualizar_streak(usuario, data_referencia=dt_sp_23h30)
        assert streak2 == 2


def test_submeter_atividade_chama_gamification_uma_unica_vez(client, usuario):
    trilha = baker.make(Trilha)
    m = baker.make(Modulo, trilha=trilha)
    atividade = baker.make(Atividade, modulo=m, xp_recompensa=100)
    questao = baker.make(
        Questao,
        atividade=atividade,
        tipo_exercicio='MULTIPLA_ESCOLHA',
        gabarito_esperado='A',
        peso_pontuacao=10,
    )
    client.force_login(usuario)

    with patch.object(GamificationService, 'creditar_xp', wraps=GamificationService().creditar_xp) as mock_xp, \
         patch.object(GamificationService, 'atualizar_streak', wraps=GamificationService().atualizar_streak) as mock_streak:

        response = client.post(
            f'/api/atividades/{atividade.pk}/submeter/',
            {'respostas': {str(questao.pk): ['A']}},
            format='json',
        )

        assert response.status_code == 200
        assert response.data['aprovado'] is True
        assert mock_xp.call_count == 1
        assert mock_streak.call_count == 1

        usuario.refresh_from_db()
        assert usuario.xp_total == 200  # 100 inicial + 100 da atividade
        assert usuario.streak_dias == 1


def test_submeter_atividade_reprovada_nao_chama_gamification(client, usuario):
    trilha = baker.make(Trilha)
    m = baker.make(Modulo, trilha=trilha)
    atividade = baker.make(Atividade, modulo=m, xp_recompensa=100)
    questao = baker.make(
        Questao,
        atividade=atividade,
        tipo_exercicio='MULTIPLA_ESCOLHA',
        gabarito_esperado='A',
        peso_pontuacao=10,
    )
    client.force_login(usuario)

    with patch.object(GamificationService, 'creditar_xp') as mock_xp, \
         patch.object(GamificationService, 'atualizar_streak') as mock_streak:

        response = client.post(
            f'/api/atividades/{atividade.pk}/submeter/',
            {'respostas': {str(questao.pk): ['B']}},
            format='json',
        )

        assert response.status_code == 200
        assert response.data['aprovado'] is False
        assert mock_xp.call_count == 0
        assert mock_streak.call_count == 0

        usuario.refresh_from_db()
        assert usuario.xp_total == 100  # Mantem 100
        assert usuario.streak_dias == 0

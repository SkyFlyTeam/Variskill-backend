import pytest
from datetime import timedelta
from django.utils import timezone
from model_bakery import baker
from django.db import transaction

from userManagement.models import User
from activityManagement.models import Atividade
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


def test_atualizar_streak_primeiro_acesso(service, usuario):
    streak = service.atualizar_streak(usuario)
    assert streak == 1
    usuario.refresh_from_db()
    assert usuario.streak_dias == 1


def test_atualizar_streak_mesmo_dia(service, usuario):
    hoje = timezone.localdate()
    usuario.streak_dias = 3
    usuario.save()
    
    # Simula último acesso hoje
    streak = service.atualizar_streak(usuario, data_referencia=hoje)
    assert streak == 3
    usuario.refresh_from_db()
    assert usuario.streak_dias == 3


def test_atualizar_streak_dia_consecutivo(service, usuario):
    hoje = timezone.localdate()
    ontem = hoje - timedelta(days=1)
    usuario.streak_dias = 3
    usuario.save()
    
    streak = service.atualizar_streak(usuario, data_referencia=ontem)
    assert streak == 4
    usuario.refresh_from_db()
    assert usuario.streak_dias == 4


def test_atualizar_streak_reset_mais_de_um_dia(service, usuario):
    hoje = timezone.localdate()
    antes_de_ontem = hoje - timedelta(days=2)
    usuario.streak_dias = 5
    usuario.save()
    
    streak = service.atualizar_streak(usuario, data_referencia=antes_de_ontem)
    assert streak == 1
    usuario.refresh_from_db()
    assert usuario.streak_dias == 1

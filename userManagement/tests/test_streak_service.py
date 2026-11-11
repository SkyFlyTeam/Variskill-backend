from datetime import timedelta
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest
from django.db import IntegrityError
from django.utils import timezone
from model_bakery import baker

from userManagement.models import RegistroAcessoDiario, User
from userManagement.services import StreakService

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def usuario():
    return baker.make(User, streak_dias=0, maior_streak=0, ultimo_dia_estudo=None)


def test_primeiro_acesso_define_streak_em_1(usuario):
    resultado = StreakService.computar_atividade_diaria(usuario)

    assert resultado["streak_dias"] == 1
    assert resultado["maior_streak"] == 1
    usuario.refresh_from_db()
    assert usuario.streak_dias == 1
    assert usuario.maior_streak == 1
    assert usuario.ultimo_dia_estudo == timezone.localdate()


def test_mesmo_dia_mantem_streak_sem_incrementos_repetidos(usuario):
    hoje = timezone.localdate()
    usuario.streak_dias = 3
    usuario.maior_streak = 3
    usuario.ultimo_dia_estudo = hoje
    usuario.save()

    StreakService.computar_atividade_diaria(usuario)
    usuario.refresh_from_db()
    assert usuario.streak_dias == 3

    # Concluir uma segunda atividade no mesmo dia não deve incrementar de novo.
    StreakService.computar_atividade_diaria(usuario)
    usuario.refresh_from_db()
    assert usuario.streak_dias == 3


def test_dia_consecutivo_incrementa_streak_mas_preserva_recorde_maior(usuario):
    hoje = timezone.localdate()
    ontem = hoje - timedelta(days=1)
    usuario.streak_dias = 3
    usuario.maior_streak = 5
    usuario.ultimo_dia_estudo = ontem
    usuario.save()

    resultado = StreakService.computar_atividade_diaria(usuario)

    assert resultado["streak_dias"] == 4
    assert resultado["maior_streak"] == 5
    usuario.refresh_from_db()
    assert usuario.streak_dias == 4
    assert usuario.maior_streak == 5
    assert usuario.ultimo_dia_estudo == hoje


def test_dia_consecutivo_supera_recorde_anterior(usuario):
    hoje = timezone.localdate()
    ontem = hoje - timedelta(days=1)
    usuario.streak_dias = 5
    usuario.maior_streak = 5
    usuario.ultimo_dia_estudo = ontem
    usuario.save()

    resultado = StreakService.computar_atividade_diaria(usuario)

    assert resultado["streak_dias"] == 6
    assert resultado["maior_streak"] == 6


def test_quebra_de_mais_de_um_dia_reseta_streak_para_1_preservando_recorde(usuario):
    hoje = timezone.localdate()
    antes_de_ontem = hoje - timedelta(days=2)
    usuario.streak_dias = 7
    usuario.maior_streak = 7
    usuario.ultimo_dia_estudo = antes_de_ontem
    usuario.save()

    resultado = StreakService.computar_atividade_diaria(usuario)

    assert resultado["streak_dias"] == 1
    assert resultado["maior_streak"] == 7
    usuario.refresh_from_db()
    assert usuario.streak_dias == 1


def test_fuso_horario_usa_localdate_proximo_da_meia_noite_utc(usuario):
    # 23h50 em America/Sao_Paulo (UTC-3) já é 02h50 UTC do dia seguinte. A regra deve
    # usar timezone.localdate() -- data local -- e não "now().date()" ingenuamente em UTC.
    tz_sp = ZoneInfo("America/Sao_Paulo")
    dt_sp_23h50 = timezone.datetime(2026, 9, 24, 23, 50, tzinfo=tz_sp)

    with patch("django.utils.timezone.now", return_value=dt_sp_23h50):
        resultado = StreakService.computar_atividade_diaria(usuario)

    assert resultado["ultimo_dia_estudo"].day == 24


def test_registro_acesso_diario_e_criado_e_incrementado_a_cada_chamada(usuario):
    StreakService.computar_atividade_diaria(usuario, xp_ganho=50)
    hoje = timezone.localdate()
    registro = RegistroAcessoDiario.objects.get(usuario=usuario, data=hoje)
    assert registro.atividades_concluidas == 1
    assert registro.xp_obtido == 50

    StreakService.computar_atividade_diaria(usuario, xp_ganho=30)
    registro.refresh_from_db()
    assert registro.atividades_concluidas == 2
    assert registro.xp_obtido == 80


def test_registro_acesso_diario_isolado_por_usuario(usuario):
    outro_usuario = baker.make(User, streak_dias=0, maior_streak=0, ultimo_dia_estudo=None)

    StreakService.computar_atividade_diaria(usuario)
    StreakService.computar_atividade_diaria(outro_usuario)

    hoje = timezone.localdate()
    assert RegistroAcessoDiario.objects.filter(usuario=usuario, data=hoje).count() == 1
    assert RegistroAcessoDiario.objects.filter(usuario=outro_usuario, data=hoje).count() == 1
    assert RegistroAcessoDiario.objects.filter(data=hoje).count() == 2


def test_registro_acesso_diario_unique_together_usuario_data(usuario):
    hoje = timezone.localdate()
    RegistroAcessoDiario.objects.create(usuario=usuario, data=hoje)

    with pytest.raises(IntegrityError):
        RegistroAcessoDiario.objects.create(usuario=usuario, data=hoje)

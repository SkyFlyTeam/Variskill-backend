import pytest
from unittest.mock import MagicMock
from userManagement.services import GamificationService
from userManagement.serializers import UserSerializer
from userManagement.models import User
from learning.serializers import SubmissionResultSerializer
from activityManagement.services import SubmissionResult


@pytest.mark.unit
class TestGamificationNivel:
    @pytest.mark.parametrize("xp,nivel_esperado", [
        (-10, 1),
        (0, 1),
        (50, 1),
        (99, 1),
        (100, 2),
        (200, 2),
        (299, 2),
        (300, 3),
        (450, 3),
        (599, 3),
        (600, 4),
        (800, 4),
        (999, 4),
        (1000, 5),
        (1499, 5),
        (1500, 6),
        (1999, 6),
        (2000, 7),
        (3000, 9),
    ])
    def test_calcular_nivel_faixas(self, xp, nivel_esperado):
        assert GamificationService.calcular_nivel(xp) == nivel_esperado

    @pytest.mark.parametrize("xp,esperado", [
        (0, {"nivel": 1, "xp_atual": 0, "xp_min_faixa": 0, "xp_proximo_nivel": 100, "xp_restante": 100, "progresso_pct": 0.0}),
        (50, {"nivel": 1, "xp_atual": 50, "xp_min_faixa": 0, "xp_proximo_nivel": 100, "xp_restante": 50, "progresso_pct": 50.0}),
        (100, {"nivel": 2, "xp_atual": 100, "xp_min_faixa": 100, "xp_proximo_nivel": 300, "xp_restante": 200, "progresso_pct": 0.0}),
        (200, {"nivel": 2, "xp_atual": 200, "xp_min_faixa": 100, "xp_proximo_nivel": 300, "xp_restante": 100, "progresso_pct": 50.0}),
        (300, {"nivel": 3, "xp_atual": 300, "xp_min_faixa": 300, "xp_proximo_nivel": 600, "xp_restante": 300, "progresso_pct": 0.0}),
        (450, {"nivel": 3, "xp_atual": 450, "xp_min_faixa": 300, "xp_proximo_nivel": 600, "xp_restante": 150, "progresso_pct": 50.0}),
        (600, {"nivel": 4, "xp_atual": 600, "xp_min_faixa": 600, "xp_proximo_nivel": 1000, "xp_restante": 400, "progresso_pct": 0.0}),
        (800, {"nivel": 4, "xp_atual": 800, "xp_min_faixa": 600, "xp_proximo_nivel": 1000, "xp_restante": 200, "progresso_pct": 50.0}),
        (1000, {"nivel": 5, "xp_atual": 1000, "xp_min_faixa": 1000, "xp_proximo_nivel": 1500, "xp_restante": 500, "progresso_pct": 0.0}),
        (1250, {"nivel": 5, "xp_atual": 1250, "xp_min_faixa": 1000, "xp_proximo_nivel": 1500, "xp_restante": 250, "progresso_pct": 50.0}),
        (1500, {"nivel": 6, "xp_atual": 1500, "xp_min_faixa": 1500, "xp_proximo_nivel": 2000, "xp_restante": 500, "progresso_pct": 0.0}),
    ])
    def test_obter_progresso_nivel_detalhado(self, xp, esperado):
        resultado = GamificationService.obter_progresso_nivel(xp)
        assert resultado == esperado

    def test_user_serializer_inclui_nivel_e_progresso(self):
        user = User(id="00000000-0000-0000-0000-000000000001", apelido="coder", nome="Coder", email="coder@test.com", xp_total=250, streak_dias=3)
        serializer = UserSerializer(user)
        data = serializer.data

        assert data["nivel"] == 2
        assert data["progresso_nivel"]["nivel"] == 2
        assert data["progresso_nivel"]["xp_atual"] == 250
        assert data["progresso_nivel"]["xp_min_faixa"] == 100
        assert data["progresso_nivel"]["xp_proximo_nivel"] == 300
        assert data["progresso_nivel"]["xp_restante"] == 50
        assert data["progresso_nivel"]["progresso_pct"] == 75.0

    def test_submission_result_serializer_inclui_level_up(self):
        mock_exec = MagicMock()
        mock_exec.id = "11111111-1111-1111-1111-111111111111"
        mock_exec.executado_em = "2026-10-07T20:00:00Z"

        sub_result = SubmissionResult(
            execution=mock_exec,
            approved=True,
            hit_rate=100.0,
            score_obtained=10,
            xp_granted=100,
            new_xp_total=100,
            feedback=[],
            level_up=True,
            nivel_anterior=1,
            novo_nivel=2,
        )

        serializer = SubmissionResultSerializer(sub_result)
        data = serializer.data

        assert data["level_up"] is True
        assert data["nivel_anterior"] == 1
        assert data["novo_nivel"] == 2
        assert data["xp_concedido"] == 100
        assert data["novo_xp_total"] == 100


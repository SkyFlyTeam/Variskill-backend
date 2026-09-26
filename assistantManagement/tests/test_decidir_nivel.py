import uuid
from django.core.management import call_command
from rest_framework import status
from rest_framework.test import APITestCase
from userManagement.models import User
from assistantManagement.models import Sessao
from trackManagement.models import Trilha, Modulo, Matricula, ProgressoModulo
from activityManagement.models import Atividade
from intents.models import Intention


class DecidirNivelTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            apelido="aluno_test",
            password="password123"
        )
        self.client.force_authenticate(user=self.user)

        self.sessao = Sessao.objects.create(usuario=self.user)

        self.trilha = Trilha.objects.create(
            titulo="Trilha Python",
            descricao="Aprenda Python do zero",
            habilidade="Programacao",
            ativo=True
        )

        self.modulo1 = Modulo.objects.create(
            trilha=self.trilha,
            titulo="Modulo 1 - Basico",
            descricao="Introducao",
            nivel="Iniciante",
            ordem_modulo=1
        )

        self.modulo2 = Modulo.objects.create(
            trilha=self.trilha,
            titulo="Modulo 2 - Avancado",
            descricao="Topicos Avancados",
            nivel="Avancado",
            ordem_modulo=2
        )

        self.atividade_diag = Atividade.objects.create(
            modulo=self.modulo1,
            titulo="Teste Diagnostico Inicial",
            descricao="Avalie seu conhecimento",
            contexto_avaliacao="DIAGNOSTICO_INICIAL",
            xp_recompensa=50,
            ordem=1,
            ativo=True
        )

        self.atividade_normal = Atividade.objects.create(
            modulo=self.modulo1,
            titulo="Primeira Aula de Python",
            descricao="Variaveis e tipos",
            contexto_avaliacao="EXERCICIO",
            xp_recompensa=10,
            ordem=2,
            ativo=True
        )

    def test_decidir_nivel_opcao_teste_diagnostico(self):
        url = f"/api/chat/sessao/{self.sessao.id}/decidir-nivel/"
        payload = {
            "trilha_id": str(self.trilha.id),
            "opcao": "TESTE_DIAGNOSTICO"
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["acao"], "INICIAR_TESTE_DIAGNOSTICO")
        self.assertEqual(response.data["atividade_diagnostica_id"], str(self.atividade_diag.id))
        self.assertEqual(response.data["redirecionar_para"], f"/atividades/{self.atividade_diag.id}")

    def test_decidir_nivel_opcao_iniciar_do_inicio(self):
        url = f"/api/chat/sessao/{self.sessao.id}/decidir-nivel/"
        payload = {
            "trilha_id": str(self.trilha.id),
            "opcao": "INICIAR_DO_INICIO"
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["acao"], "INICIAR_DO_INICIO")
        self.assertEqual(response.data["primeira_atividade_id"], str(self.atividade_normal.id))
        self.assertEqual(response.data["redirecionar_para"], f"/atividades/{self.atividade_normal.id}")

        matricula = Matricula.objects.filter(usuario=self.user, trilha=self.trilha).first()
        self.assertIsNotNone(matricula)
        self.assertEqual(matricula.status, "EM_ANDAMENTO")

        prog1 = ProgressoModulo.objects.filter(matricula=matricula, modulo=self.modulo1).first()
        prog2 = ProgressoModulo.objects.filter(matricula=matricula, modulo=self.modulo2).first()

        self.assertIsNotNone(prog1)
        self.assertEqual(prog1.status, "EM_ANDAMENTO")
        self.assertIsNotNone(prog2)
        self.assertEqual(prog2.status, "BLOQUEADO")

    def test_decidir_nivel_sessao_inexistente(self):
        random_sessao_id = uuid.uuid4()
        url = f"/api/chat/sessao/{random_sessao_id}/decidir-nivel/"
        payload = {
            "trilha_id": str(self.trilha.id),
            "opcao": "TESTE_DIAGNOSTICO"
        }

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_decidir_nivel_trilha_inexistente(self):
        random_trilha_id = uuid.uuid4()
        url = f"/api/chat/sessao/{self.sessao.id}/decidir-nivel/"
        payload = {
            "trilha_id": str(random_trilha_id),
            "opcao": "TESTE_DIAGNOSTICO"
        }

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_decidir_nivel_sem_autenticacao(self):
        self.client.force_authenticate(user=None)
        url = f"/api/chat/sessao/{self.sessao.id}/decidir-nivel/"
        payload = {
            "trilha_id": str(self.trilha.id),
            "opcao": "TESTE_DIAGNOSTICO"
        }

        response = self.client.post(url, payload, format="json")
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_seed_intencoes_cadastra_iniciar_diagnostico(self):
        call_command("seed_intencoes")
        intention = Intention.objects.filter(code="INICIAR_DIAGNOSTICO").first()
        self.assertIsNotNone(intention)
        self.assertEqual(intention.system_action, "DISPARAR_TESTE_DIAGNOSTICO")
        self.assertTrue(intention.examples.filter(text__icontains="nivelamento").exists())


import uuid

from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from semanticSearch.models import DuvidaAssimilada
from userManagement.models import User


class FeedbackDuvidaTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            apelido="aluno_feedback",
            nome="Ana",
            email="aluno_feedback@example.com",
            password="password123",
        )
        self.client.force_authenticate(user=self.user)
        self.duvida = baker.make(
            DuvidaAssimilada, embedding=[0.1] * 384, feedbacks_positivos=2, feedbacks_negativos=1,
        )
        self.url = f"/api/chat/duvidas/{self.duvida.id}/feedback/"

    def test_feedback_util_incrementa_positivos(self):
        resp = self.client.post(self.url, {"util": True}, format="json")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(), {"sucesso": True, "feedbacks_positivos": 3, "feedbacks_negativos": 1},
        )
        self.duvida.refresh_from_db()
        self.assertEqual(self.duvida.feedbacks_positivos, 3)

    def test_feedback_nao_util_incrementa_negativos(self):
        resp = self.client.post(self.url, {"util": False}, format="json")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(), {"sucesso": True, "feedbacks_positivos": 2, "feedbacks_negativos": 2},
        )

    def test_duvida_inexistente_retorna_404(self):
        resp = self.client.post(f"/api/chat/duvidas/{uuid.uuid4()}/feedback/", {"util": True}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_body_sem_util_retorna_400(self):
        resp = self.client.post(self.url, {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.duvida.refresh_from_db()
        self.assertEqual((self.duvida.feedbacks_positivos, self.duvida.feedbacks_negativos), (2, 1))

    def test_requer_autenticacao(self):
        self.client.force_authenticate(user=None)
        resp = self.client.post(self.url, {"util": True}, format="json")
        # Autenticação por sessão: o DRF responde 403 (sem header WWW-Authenticate) em vez de 401.
        self.assertIn(resp.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

import uuid
from unittest.mock import MagicMock, patch

from rest_framework import status
from rest_framework.test import APITestCase

from assistantManagement.models import Mensagem, Sessao
from intents.models import Intention, Response
from trackManagement.models import Trilha
from userManagement.models import User


class ChatEndpointsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            apelido="aluno_chat",
            nome="Guilherme",
            email="aluno_chat@example.com",
            password="password123",
        )
        self.client.force_authenticate(user=self.user)

        self.trilha_js = Trilha.objects.create(
            titulo="Javascript",
            descricao="Trilha de Javascript",
            habilidade="Frontend",
            ativo=True,
        )
        self.trilha_dados = Trilha.objects.create(
            titulo="Introdução a Ciência de Dados",
            descricao="Trilha de Dados",
            habilidade="Dados",
            ativo=True,
        )
        self.trilha_inativa = Trilha.objects.create(
            titulo="Trilha Oculta",
            descricao="Inativa",
            habilidade="Backend",
            ativo=False,
        )

        self.intencao_trilhas = Intention.objects.create(
            code="LISTAR_TRILHAS",
            system_action="RETORNAR_TRILHAS",
            description="Intenção para listar trilhas",
        )
        self.resposta_trilhas = Response.objects.create(
            intention=self.intencao_trilhas,
            text="Aqui estão as nossas trilhas de formação abertas para você!",
        )

    # 1. POST /api/chat/sessao/iniciar/
    def test_iniciar_sessao_sucesso(self):
        url = "/api/chat/sessao/iniciar/"
        response = self.client.post(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("sessao_id", response.data)
        self.assertIn("mensagem_inicial", response.data)

        mensagem_inicial = response.data["mensagem_inicial"]
        self.assertEqual(mensagem_inicial["remetente"], "ASSISTENTE")
        self.assertIn("Olá, Guilherme!", mensagem_inicial["conteudo"])
        self.assertIn("Ver trilhas disponíveis", mensagem_inicial["sugestoes_rapidas"])

        # Verifica persistência no banco
        sessao = Sessao.objects.filter(id=response.data["sessao_id"]).first()
        self.assertIsNotNone(sessao)
        self.assertEqual(sessao.usuario, self.user)

        msg_db = Mensagem.objects.filter(sessao=sessao).first()
        self.assertIsNotNone(msg_db)
        self.assertEqual(msg_db.remetente, Mensagem.Remetente.ASSISTENTE)
        self.assertEqual(msg_db.conteudo, mensagem_inicial["conteudo"])

    def test_iniciar_sessao_sem_autenticacao(self):
        self.client.force_authenticate(user=None)
        url = "/api/chat/sessao/iniciar/"
        response = self.client.post(url, format="json")

        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    # 2. POST /api/chat/sessao/{sessao_id}/mensagem/
    @patch("assistantManagement.services.IntentClassifier")
    @patch("assistantManagement.services.EmbeddingService")
    @patch("assistantManagement.services.TextPreprocessor")
    def test_enviar_mensagem_sucesso_com_intencao_listar_trilhas(
        self, mock_preprocessor_cls, mock_embedding_cls, mock_classifier_cls
    ):
        # Mocks para agilidade e isolamento
        mock_preprocessor = MagicMock()
        mock_preprocessor.processar.return_value = "quais trilhas estao disponiveis"
        mock_preprocessor_cls.get_instance.return_value = mock_preprocessor

        mock_embedding = MagicMock()
        mock_embedding.gerar_embedding.return_value = [0.1] * 384
        mock_embedding_cls.get_instance.return_value = mock_embedding

        mock_classifier = MagicMock()
        mock_classifier.classificar.return_value = {
            "intencao": "LISTAR_TRILHAS",
            "similaridade": 0.95,
            "resposta_texto": "Aqui estão as nossas trilhas de formação abertas para você!",
            "dados_extras": {},
        }
        mock_classifier_cls.return_value = mock_classifier

        sessao = Sessao.objects.create(usuario=self.user)
        url = f"/api/chat/sessao/{sessao.id}/mensagem/"
        payload = {"conteudo": "Quais trilhas estão disponíveis?"}

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("resposta_assistente", response.data)

        resp_assistente = response.data["resposta_assistente"]
        self.assertEqual(resp_assistente["remetente"], "ASSISTENTE")
        self.assertEqual(resp_assistente["intencao_detectada"], "LISTAR_TRILHAS")
        self.assertEqual(
            resp_assistente["conteudo"],
            "Aqui estão as nossas trilhas de formação abertas para você!",
        )

        # Checa opções de trilhas anexadas
        opcoes = resp_assistente["opcoes_trilhas"]
        self.assertEqual(len(opcoes), 2)
        titulos = [op["titulo"] for op in opcoes]
        self.assertIn("Javascript", titulos)
        self.assertIn("Introdução a Ciência de Dados", titulos)
        self.assertNotIn("Trilha Oculta", titulos)

        # Verifica persistência no banco (duas mensagens: usuário e assistente)
        mensagens_db = Mensagem.objects.filter(sessao=sessao).order_by("criada_em")
        self.assertEqual(mensagens_db.count(), 2)

        msg_user = mensagens_db[0]
        self.assertEqual(msg_user.remetente, Mensagem.Remetente.USUARIO)
        self.assertEqual(msg_user.conteudo, "Quais trilhas estão disponíveis?")

        msg_bot = mensagens_db[1]
        self.assertEqual(msg_bot.remetente, Mensagem.Remetente.ASSISTENTE)
        self.assertEqual(msg_bot.intencao, self.intencao_trilhas)
        self.assertAlmostEqual(float(msg_bot.distancia), 0.05, places=2)

    @patch("assistantManagement.services.IntentClassifier")
    @patch("assistantManagement.services.EmbeddingService")
    @patch("assistantManagement.services.TextPreprocessor")
    def test_enviar_mensagem_fallback(
        self, mock_preprocessor_cls, mock_embedding_cls, mock_classifier_cls
    ):
        mock_preprocessor = MagicMock()
        mock_preprocessor.processar.return_value = "xyz abcd"
        mock_preprocessor_cls.get_instance.return_value = mock_preprocessor

        mock_embedding = MagicMock()
        mock_embedding.gerar_embedding.return_value = [0.1] * 384
        mock_embedding_cls.get_instance.return_value = mock_embedding

        mock_classifier = MagicMock()
        mock_classifier.classificar.return_value = {
            "intencao": "FALLBACK",
            "similaridade": 0.30,
            "resposta_texto": "Hmm, não entendi muito bem. Pode reformular sua pergunta?",
            "dados_extras": {},
        }
        mock_classifier_cls.return_value = mock_classifier

        sessao = Sessao.objects.create(usuario=self.user)
        url = f"/api/chat/sessao/{sessao.id}/mensagem/"
        payload = {"conteudo": "qualquer coisa desconhecida"}

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        resp_assistente = response.data["resposta_assistente"]
        self.assertEqual(resp_assistente["intencao_detectada"], "FALLBACK")
        self.assertEqual(len(resp_assistente.get("opcoes_trilhas", [])), 0)

    def test_enviar_mensagem_sessao_inexistente(self):
        url = f"/api/chat/sessao/{uuid.uuid4()}/mensagem/"
        payload = {"conteudo": "Olá"}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_enviar_mensagem_sessao_de_outro_usuario(self):
        outro_user = User.objects.create_user(
            apelido="outro_user", password="password123"
        )
        sessao_outro = Sessao.objects.create(usuario=outro_user)

        url = f"/api/chat/sessao/{sessao_outro.id}/mensagem/"
        payload = {"conteudo": "Tentando acessar outra sessão"}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_enviar_mensagem_corpo_vazio_invalido(self):
        sessao = Sessao.objects.create(usuario=self.user)
        url = f"/api/chat/sessao/{sessao.id}/mensagem/"
        payload = {"conteudo": "   "}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # 3. GET /api/chat/sessao/{sessao_id}/historico/
    def test_obter_historico_sessao_sucesso(self):
        sessao = Sessao.objects.create(usuario=self.user)
        Mensagem.objects.create(
            sessao=sessao,
            remetente=Mensagem.Remetente.ASSISTENTE,
            conteudo="Olá, como posso ajudar?",
        )
        Mensagem.objects.create(
            sessao=sessao,
            remetente=Mensagem.Remetente.USUARIO,
            conteudo="Quero ver as trilhas",
        )
        Mensagem.objects.create(
            sessao=sessao,
            remetente=Mensagem.Remetente.ASSISTENTE,
            conteudo="Aqui estão as trilhas",
            intencao=self.intencao_trilhas,
        )

        url = f"/api/chat/sessao/{sessao.id}/historico/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["sessao_id"], str(sessao.id))
        self.assertEqual(response.data["total_mensagens"], 3)
        self.assertEqual(len(response.data["mensagens"]), 3)

        msgs = response.data["mensagens"]
        self.assertEqual(msgs[0]["remetente"], "ASSISTENTE")
        self.assertEqual(msgs[1]["remetente"], "USUARIO")
        self.assertEqual(msgs[2]["remetente"], "ASSISTENTE")
        self.assertEqual(msgs[2]["intencao_detectada"], "LISTAR_TRILHAS")
        self.assertIn("opcoes_trilhas", msgs[2])
        self.assertEqual(len(msgs[2]["opcoes_trilhas"]), 2)

    def test_obter_historico_sessao_inexistente(self):
        url = f"/api/chat/sessao/{uuid.uuid4()}/historico/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_obter_historico_sem_autenticacao(self):
        self.client.force_authenticate(user=None)
        sessao = Sessao.objects.create(usuario=self.user)
        url = f"/api/chat/sessao/{sessao.id}/historico/"
        response = self.client.get(url)
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )


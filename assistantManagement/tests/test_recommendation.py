import uuid
from unittest.mock import MagicMock, patch

from rest_framework import status
from rest_framework.test import APITestCase

from assistantManagement.models import Mensagem, Sessao
from assistantManagement.services import _recomendar_trilhas_contextual
from intents.models import Intention, Response
from trackManagement.models import Matricula, Trilha
from userManagement.models import Interesse, User, UsuarioInteresse


class TrackRecommendationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            apelido="aluno_rec",
            nome="Guilherme",
            email="aluno_rec@example.com",
            password="password123",
        )
        self.client.force_authenticate(user=self.user)

        self.trilha_python = Trilha.objects.create(
            titulo="Python Fundamentos",
            descricao="Aprenda lógica de programação e backend com Python.",
            habilidade="Backend",
            ativo=True,
        )
        self.trilha_dados = Trilha.objects.create(
            titulo="Ciência de Dados",
            descricao="Análise exploratória, estatística e machine learning.",
            habilidade="Dados",
            ativo=True,
        )
        self.trilha_web = Trilha.objects.create(
            titulo="Desenvolvimento Web Frontend",
            descricao="HTML, CSS, JavaScript e interfaces modernas.",
            habilidade="Frontend",
            ativo=True,
        )

        self.intencao_rec = Intention.objects.create(
            code="RECOMENDAR_TRILHA",
            system_action="RECOMENDAR_TRILHAS_CONTEXTUAL",
            description="Recomenda trilhas de acordo com preferências e histórico",
        )
        self.resp_rec = Response.objects.create(
            intention=self.intencao_rec,
            text="Preparei uma recomendação especial para você:",
        )

        self.sessao = Sessao.objects.create(usuario=self.user)

    def test_recomendar_trilhas_prioriza_interesses_do_estudante(self):
        # Cadastrar interesse do estudante em 'Dados'
        int_dados = Interesse.objects.create(nome="Dados")
        UsuarioInteresse.objects.create(usuario=self.user, interesse=int_dados)

        trilhas_ranqueadas, interesses, motivo = _recomendar_trilhas_contextual(
            self.user, [self.trilha_python, self.trilha_dados, self.trilha_web]
        )

        # A primeira recomendação deve ser Ciência de Dados
        self.assertEqual(trilhas_ranqueadas[0].id, self.trilha_dados.id)
        self.assertIn("Dados", interesses)
        self.assertIn("Ciência de Dados", motivo)

    def test_recomendar_trilhas_considera_historico_de_conclusao(self):
        # Estudante já concluiu Python Fundamentos
        Matricula.objects.create(
            usuario=self.user,
            trilha=self.trilha_python,
            status="CONCLUIDO",
        )

        trilhas_ranqueadas, _, _ = _recomendar_trilhas_contextual(
            self.user, [self.trilha_python, self.trilha_dados, self.trilha_web]
        )

        # Trilha já concluída deve ir para o final da fila de recomendação
        self.assertEqual(trilhas_ranqueadas[-1].id, self.trilha_python.id)

    def test_recomendar_trilhas_sem_interesses_retorna_recomendacao_geral(self):
        trilhas_ranqueadas, interesses, motivo = _recomendar_trilhas_contextual(
            self.user, [self.trilha_python, self.trilha_dados, self.trilha_web]
        )

        self.assertEqual(len(trilhas_ranqueadas), 3)
        self.assertEqual(interesses, [])
        self.assertIn("competências fundamentais", motivo)

    @patch("assistantManagement.services.TextPreprocessor.get_instance")
    @patch("assistantManagement.services.EmbeddingService.get_instance")
    @patch("assistantManagement.services.IntentClassifier.classificar")
    def test_endpoint_chat_executa_intencao_recomendar_trilha(
        self, mock_classificar, mock_embed_inst, mock_prep_inst
    ):
        mock_prep = MagicMock()
        mock_prep.limpar_texto.return_value = "recomende trilha"
        mock_prep.obter_tokens.return_value = ["recomende", "trilha"]
        mock_prep_inst.return_value = mock_prep

        mock_embed = MagicMock()
        mock_embed.gerar_embedding.return_value = [0.1] * 384
        mock_embed_inst.return_value = mock_embed

        mock_classificar.return_value = {
            "intencao": "RECOMENDAR_TRILHA",
            "similaridade": 0.88,
            "resposta_texto": self.resp_rec.text,
        }

        # Cadastrar interesse
        int_front = Interesse.objects.create(nome="Frontend")
        UsuarioInteresse.objects.create(usuario=self.user, interesse=int_front)

        url = f"/api/chat/sessao/{self.sessao.id}/mensagem/"
        response = self.client.post(url, {"conteudo": "Qual trilha você me recomenda?"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dados = response.data["resposta_assistente"]
        self.assertEqual(dados["intencao_detectada"], "RECOMENDAR_TRILHA")
        self.assertEqual(dados["acao"], "RECOMENDACAO_TRILHA")
        self.assertTrue(len(dados["opcoes_trilhas"]) > 0)
        # Primeira opção recomendada deve ser Frontend por conta do interesse
        self.assertEqual(dados["opcoes_trilhas"][0]["titulo"], "Desenvolvimento Web Frontend")
        self.assertTrue(any("Desenvolvimento Web Frontend" in s for s in dados["sugestoes_rapidas"]))


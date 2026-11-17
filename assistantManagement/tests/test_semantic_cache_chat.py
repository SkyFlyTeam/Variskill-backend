from unittest.mock import MagicMock, patch

from rest_framework import status
from rest_framework.test import APITestCase

from activityManagement.models import Atividade
from assistantManagement.models import Sessao
from questionsManagement.models import Questao
from semanticSearch.models import EntradaCorpus, PerguntaCorpus
from trackManagement.models import Modulo, Trilha
from userManagement.models import User


class SemanticCacheChatTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            apelido="aluno_cache_chat",
            nome="Carlos",
            email="carlos_cache@example.com",
            password="password123",
        )
        self.client.force_authenticate(user=self.user)
        self.sessao = Sessao.objects.create(usuario=self.user)
        self.url = f"/api/chat/sessao/{self.sessao.id}/mensagem/"

        self.trilha = Trilha.objects.create(
            titulo="Python: Fundamentos",
            habilidade="Programação",
            ativo=True,
        )

        patchers = [
            patch("assistantManagement.services.TextPreprocessor"),
            patch("assistantManagement.services.EmbeddingService"),
            patch("assistantManagement.services.IntentClassifier"),
        ]
        self.mock_preprocessor = patchers[0].start()
        self.mock_embedding = patchers[1].start()
        self.mock_classifier = patchers[2].start()
        for p in patchers:
            self.addCleanup(p.stop)

        self.preprocessor = MagicMock()
        self.preprocessor.processar.side_effect = lambda t: t.lower()
        self.mock_preprocessor.get_instance.return_value = self.preprocessor

        self.embedding_service = MagicMock()
        self.embedding_service.gerar_embedding.return_value = [0.1] * 384
        self.mock_embedding.get_instance.return_value = self.embedding_service

        self.classifier = MagicMock()
        self.mock_classifier.return_value = self.classifier

    def _configurar_classificador(self, intencao="DUVIDA_CONTEUDO", similaridade=0.85):
        self.classifier.classificar.return_value = {
            "intencao": intencao,
            "similaridade": similaridade,
            "resposta_texto": "{resposta_corpus}",
            "dados_extras": {},
        }

    def test_duvida_encontrada_no_corpus_acima_threshold_retorna_pln_local(self):
        """Dúvida com similaridade >= 0.82 no Corpus retorna direto de PLN_LOCAL sem chamar IA externa."""
        self._configurar_classificador()

        entrada = EntradaCorpus.objects.create(
            topico="Python",
            pergunta="O que é PEP 8?",
            resposta="PEP 8 é o guia de estilo oficial para código Python.",
        )
        # embedding idêntico -> CosineDistance = 0.0 -> similaridade = 1.0 (>= 0.82)
        PerguntaCorpus.objects.create(
            entrada=entrada,
            texto="O que é PEP 8?",
            embedding=[0.1] * 384,
        )

        with patch("assistantManagement.services.HintService.call_external_ai_chat") as mock_ia:
            with patch("assistantManagement.services.CorpusIngestionService.assimilar_duvida_async") as mock_ingest:
                response = self.client.post(
                    self.url,
                    {"conteudo": "o que é pep 8"},
                    format="json",
                )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dados = response.data["resposta_assistente"]
        self.assertEqual(dados["origem_resposta"], "PLN_LOCAL")
        self.assertIn("PEP 8 é o guia de estilo oficial", dados["conteudo"])
        self.assertEqual(dados["dados_acao"]["entrada_corpus_id"], str(entrada.id))
        mock_ia.assert_not_called()
        mock_ingest.assert_not_called()

    def test_duvida_nao_encontrada_faz_fallback_ia_e_dispara_ingestao_assincrona(self):
        """Dúvida sem match no corpus (< 0.82) chama a IA externa e agenda assimilação assíncrona."""
        self._configurar_classificador()

        # Sem nenhum registro no corpus
        with patch("assistantManagement.services.HintService.call_external_ai_chat") as mock_ia:
            with patch("assistantManagement.services.CorpusIngestionService.assimilar_duvida_async") as mock_ingest:
                mock_ia.return_value = "Duck typing é o conceito de que o tipo do objeto é determinado por seus métodos e atributos."

                response = self.client.post(
                    self.url,
                    {"conteudo": "como funciona o duck typing em python?"},
                    format="json",
                )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dados = response.data["resposta_assistente"]
        self.assertEqual(dados["origem_resposta"], "IA_EXTERNA")
        self.assertEqual(dados["conteudo"], "Duck typing é o conceito de que o tipo do objeto é determinado por seus métodos e atributos.")
        mock_ia.assert_called_once()
        mock_ingest.assert_called_once_with(
            "como funciona o duck typing em python?",
            "Duck typing é o conceito de que o tipo do objeto é determinado por seus métodos e atributos.",
            topico="Programação",
        )

    def test_falha_na_ia_externa_retorna_contingencia_sem_erro_500(self):
        """Se a IA externa falhar ou estiver sem chave de API, retorna contingência com status 200."""
        self._configurar_classificador()

        with patch("assistantManagement.services.HintService.call_external_ai_chat") as mock_ia:
            with patch("assistantManagement.services.CorpusIngestionService.assimilar_duvida_async") as mock_ingest:
                mock_ia.return_value = None  # Simula erro de rede, timeout ou cota

                response = self.client.post(
                    self.url,
                    {"conteudo": "duvida desconhecida sem resposta"},
                    format="json",
                )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dados = response.data["resposta_assistente"]
        self.assertEqual(dados["origem_resposta"], "CONTINGENCIA")
        self.assertIn("Ainda não tenho esse assunto", dados["conteudo"])
        mock_ingest.assert_not_called()

    def test_suporte_contextual_pedir_dica_consulta_cache_semantico_e_assimila_pos_ia(self):
        """Endpoint /api/atividades/{id}/pedir-dica/ consulta cache semântico antes da IA e assimila resposta nova."""
        modulo = Modulo.objects.create(
            trilha=self.trilha,
            titulo="Estruturas de Repetição",
            nivel="INICIANTE",
            ordem_modulo=1,
        )
        atividade = Atividade.objects.create(
            modulo=modulo,
            titulo="Exercício de Loops",
            contexto_avaliacao="CODIGO",
            ordem=1,
            ativo=True,
        )
        questao = Questao.objects.create(
            atividade=atividade,
            tipo_exercicio="MULTIPLA_ESCOLHA",
            enunciado="Como interromper um loop?",
            gabarito_esperado="break",
            dica_conceitual="",
            ordem_questao=1,
        )
        url_dica = f"/api/atividades/{atividade.id}/pedir-dica/"

        # 1. Sem cache semântico -> chama IA externa e dispara assimilação assíncrona
        with patch("learning.hint_service.HintService._call_external_ai") as mock_ia:
            with patch("semanticSearch.service.ingestion_service.CorpusIngestionService.assimilar_duvida_async") as mock_ingest:
                mock_ia.return_value = "Use a instrução break para interromper a iteração imediatamente."
                resp1 = self.client.post(
                    url_dica,
                    {
                        "sessao_id": str(self.sessao.id),
                        "questao_id": str(questao.id),
                        "pergunta": "Qual comando interrompe o loop imediatamente?",
                    },
                    format="json",
                )

        self.assertEqual(resp1.status_code, status.HTTP_200_OK)
        self.assertEqual(resp1.data["origem_resposta"], "IA_EXTERNA")
        mock_ia.assert_called_once()
        mock_ingest.assert_called_once_with(
            pergunta="Qual comando interrompe o loop imediatamente?",
            resposta="Use a instrução break para interromper a iteração imediatamente.",
            topico="Estruturas de Repetição",
        )

        # 2. Com dúvida já assimilada no corpus -> retorna de PLN_LOCAL sem chamar IA externa
        entrada = EntradaCorpus.objects.create(
            topico="Estruturas de Repetição",
            pergunta="Qual comando interrompe o loop imediatamente?",
            resposta="Use a instrução break para interromper a iteração imediatamente.",
        )
        PerguntaCorpus.objects.create(
            entrada=entrada,
            texto="Qual comando interrompe o loop imediatamente?",
            embedding=[0.1] * 384,
        )

        with patch("learning.hint_service.HintService._call_external_ai") as mock_ia2:
            with patch("semanticSearch.service.text_embedding_service.TextEmbeddingService.gerar_embedding", return_value=[0.1] * 384):
                resp2 = self.client.post(
                    url_dica,
                    {
                        "sessao_id": str(self.sessao.id),
                        "questao_id": str(questao.id),
                        "pergunta": "Qual comando interrompe o loop imediatamente?",
                    },
                    format="json",
                )

        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertEqual(resp2.data["origem_resposta"], "PLN_LOCAL")
        self.assertIn("instrução break", resp2.data["resposta_coach"])
        mock_ia2.assert_not_called()

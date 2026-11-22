from unittest.mock import MagicMock, patch

from rest_framework import status
from rest_framework.test import APITestCase

from activityManagement.models import Atividade
from assistantManagement.models import Mensagem, Sessao
from questionsManagement.models import Questao
from semanticSearch.models import DuvidaAssimilada, EntradaCorpus, PerguntaCorpus
from trackManagement.models import Modulo, Trilha
from userManagement.models import User

VETOR = [0.1] * 384
RESPOSTA_IA = "Duck typing é o conceito de que o tipo do objeto é determinado por seus métodos e atributos."


class BaseConhecimentoChatTests(APITestCase):
    """Fluxo do chat: apostila -> dúvidas assimiladas -> IA externa + assimilação assíncrona."""

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

        self.trilha = Trilha.objects.create(titulo="Python: Fundamentos", habilidade="Programação", ativo=True)
        self.modulo = Modulo.objects.create(
            trilha=self.trilha, titulo="Estruturas de Repetição", nivel="INICIANTE", ordem_modulo=1,
        )
        self.atividade = Atividade.objects.create(
            modulo=self.modulo, titulo="Exercício de Loops", contexto_avaliacao="CODIGO", ordem=1, ativo=True,
        )

        patchers = [
            patch("assistantManagement.services.TextPreprocessor"),
            patch("assistantManagement.services.EmbeddingService"),
            patch("assistantManagement.services.IntentClassifier"),
        ]
        mock_preprocessor, mock_embedding, mock_classifier = (p.start() for p in patchers)
        for p in patchers:
            self.addCleanup(p.stop)

        self.preprocessor = MagicMock()
        self.preprocessor.processar.side_effect = lambda t: t.lower()
        mock_preprocessor.get_instance.return_value = self.preprocessor

        self.embedding_service = MagicMock()
        self.embedding_service.gerar_embedding.return_value = VETOR
        mock_embedding.get_instance.return_value = self.embedding_service

        self.classifier = MagicMock()
        mock_classifier.return_value = self.classifier

    def _configurar_classificador(self, intencao="DUVIDA_CONTEUDO", resposta_texto="{resposta_corpus}"):
        self.classifier.classificar.return_value = {
            "intencao": intencao,
            "similaridade": 0.85,
            "resposta_texto": resposta_texto,
            "dados_extras": {},
        }

    def _enviar(self, conteudo, resposta_ia=None, **contexto):
        with patch("assistantManagement.services.HintService.call_external_ai_chat") as mock_ia_chat, \
                patch("assistantManagement.services.HintService._call_external_ai") as mock_ia_dica, \
                patch("assistantManagement.services.BaseConhecimento.assimilar_async") as mock_assimilar:
            mock_ia_chat.return_value = resposta_ia
            mock_ia_dica.return_value = resposta_ia
            response = self.client.post(self.url, {"conteudo": conteudo, **contexto}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data["resposta_assistente"], mock_ia_chat, mock_ia_dica, mock_assimilar

    # --- Dúvida conceitual ---------------------------------------------------------------

    def test_duvida_na_apostila_responde_pln_local_sem_chamar_ia(self):
        self._configurar_classificador()
        entrada = EntradaCorpus.objects.create(
            topico="Python", pergunta="O que é PEP 8?", resposta="PEP 8 é o guia de estilo oficial para código Python.",
        )
        PerguntaCorpus.objects.create(entrada=entrada, texto="O que é PEP 8?", embedding=VETOR)

        dados, mock_ia, _, mock_assimilar = self._enviar("o que é pep 8")

        self.assertEqual(dados["origem_resposta"], "PLN_LOCAL")
        self.assertIn("PEP 8 é o guia de estilo oficial", dados["conteudo"])
        self.assertEqual(dados["dados_acao"]["entrada_corpus_id"], str(entrada.id))
        self.assertIsNone(dados["duvida_assimilada_id"])
        mock_ia.assert_not_called()
        mock_assimilar.assert_not_called()

    def test_duvida_assimilada_responde_cache_semantico_e_aceita_feedback(self):
        self._configurar_classificador()
        duvida = DuvidaAssimilada.objects.create(
            pergunta_texto="Como funciona o duck typing?",
            pergunta_normalizada="como funcionar duck typing",
            resposta_didatica=RESPOSTA_IA,
            embedding=VETOR,
        )

        dados, mock_ia, _, mock_assimilar = self._enviar("e esse tal de duck typing?")

        self.assertEqual(dados["origem_resposta"], "CACHE_SEMANTICO")
        self.assertEqual(dados["acao"], "RESPOSTA_DUVIDA_ASSIMILADA")
        self.assertEqual(dados["conteudo"], RESPOSTA_IA)
        self.assertEqual(str(dados["duvida_assimilada_id"]), str(duvida.id))
        self.assertEqual(dados["dados_acao"]["duvida_assimilada_id"], str(duvida.id))
        mock_ia.assert_not_called()
        mock_assimilar.assert_not_called()

        duvida.refresh_from_db()
        self.assertEqual(duvida.contador_utilizacoes, 2)
        mensagem = Mensagem.objects.get(id=dados["id"])
        self.assertEqual(mensagem.origem_resposta, "CACHE_SEMANTICO")
        self.assertEqual(mensagem.duvida_assimilada_id, duvida.id)

        feedback = self.client.post(
            f"/api/chat/duvidas/{dados['duvida_assimilada_id']}/feedback/", {"util": True}, format="json",
        )
        self.assertEqual(feedback.status_code, status.HTTP_200_OK)
        self.assertEqual(feedback.json()["feedbacks_positivos"], 1)

    def test_historico_expoe_origem_e_duvida_assimilada(self):
        self._configurar_classificador()
        duvida = DuvidaAssimilada.objects.create(
            pergunta_texto="Como funciona o duck typing?",
            pergunta_normalizada="como funcionar duck typing",
            resposta_didatica=RESPOSTA_IA,
            embedding=VETOR,
        )
        self._enviar("e esse tal de duck typing?")

        resp = self.client.get(f"/api/chat/sessao/{self.sessao.id}/historico/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ultima = resp.data["mensagens"][-1]
        self.assertEqual(ultima["origem_resposta"], "CACHE_SEMANTICO")
        self.assertEqual(str(ultima["duvida_assimilada_id"]), str(duvida.id))

    def test_duvida_mal_avaliada_nao_e_servida(self):
        self._configurar_classificador()
        DuvidaAssimilada.objects.create(
            pergunta_texto="Como funciona o duck typing?",
            pergunta_normalizada="como funcionar duck typing",
            resposta_didatica="Resposta ruim.",
            embedding=VETOR,
            feedbacks_negativos=5,
            feedbacks_positivos=0,
        )

        dados, mock_ia, _, _ = self._enviar("e esse tal de duck typing?", resposta_ia=RESPOSTA_IA)

        self.assertEqual(dados["origem_resposta"], "IA_EXTERNA")
        mock_ia.assert_called_once()

    def test_dica_de_atividade_nao_responde_duvida_conceitual(self):
        self._configurar_classificador()
        DuvidaAssimilada.objects.create(
            atividade=self.atividade,
            pergunta_texto="Como interromper o loop?",
            pergunta_normalizada="como interromper loop",
            resposta_didatica="Pense em qual instrução encerra a repetição.",
            embedding=VETOR,
        )

        dados, mock_ia, _, _ = self._enviar("como interromper o loop?", resposta_ia=RESPOSTA_IA)

        self.assertEqual(dados["origem_resposta"], "IA_EXTERNA")
        mock_ia.assert_called_once()

    def test_sem_resposta_local_chama_ia_e_assimila_duvida_global(self):
        self._configurar_classificador()

        dados, mock_ia, _, mock_assimilar = self._enviar(
            "como funciona o duck typing em python?", resposta_ia=RESPOSTA_IA,
        )

        self.assertEqual(dados["origem_resposta"], "IA_EXTERNA")
        self.assertEqual(dados["conteudo"], RESPOSTA_IA)
        self.assertIsNone(dados["duvida_assimilada_id"])
        mock_ia.assert_called_once()
        mock_assimilar.assert_called_once_with(
            "como funciona o duck typing em python?", RESPOSTA_IA, modulo_id=None,
        )

    def test_duvida_enviada_de_dentro_da_atividade_registra_o_modulo(self):
        self._configurar_classificador()

        _, _, _, mock_assimilar = self._enviar(
            "como funciona o duck typing em python?", resposta_ia=RESPOSTA_IA, atividade_id=str(self.atividade.id),
        )

        mock_assimilar.assert_called_once_with(
            "como funciona o duck typing em python?", RESPOSTA_IA, modulo_id=self.modulo.id,
        )

    def test_falha_na_ia_externa_retorna_contingencia_sem_assimilar(self):
        self._configurar_classificador()

        dados, _, _, mock_assimilar = self._enviar("duvida desconhecida sem resposta", resposta_ia=None)

        self.assertEqual(dados["origem_resposta"], "CONTINGENCIA")
        self.assertIn("Ainda não tenho esse assunto", dados["conteudo"])
        mock_assimilar.assert_not_called()

    # --- Pedido de dica pelo chat --------------------------------------------------------

    def _criar_questao(self):
        return Questao.objects.create(
            atividade=self.atividade,
            tipo_exercicio="MULTIPLA_ESCOLHA",
            enunciado="Como interromper um loop?",
            gabarito_esperado="break",
            dica_conceitual="",
            ordem_questao=1,
        )

    def test_pedir_dica_usa_dica_assimilada_da_questao(self):
        self._configurar_classificador("PEDIR_DICA", resposta_texto="Dica: {texto_dica}")
        questao = self._criar_questao()
        duvida = DuvidaAssimilada.objects.create(
            questao=questao,
            atividade=self.atividade,
            modulo=self.modulo,
            pergunta_texto="Como interromper o loop?",
            pergunta_normalizada="como interromper loop",
            resposta_didatica="Pense em qual instrução encerra a repetição.",
            embedding=VETOR,
        )

        dados, _, mock_ia, _ = self._enviar(
            "me dá uma dica", atividade_id=str(self.atividade.id), questao_id=str(questao.id),
        )

        self.assertEqual(dados["origem_resposta"], "CACHE_SEMANTICO")
        self.assertEqual(dados["acao"], "DICA_FORNECIDA")
        self.assertEqual(dados["conteudo"], "Dica: Pense em qual instrução encerra a repetição")
        self.assertEqual(str(dados["duvida_assimilada_id"]), str(duvida.id))
        mock_ia.assert_not_called()

    def test_pedir_dica_sem_resposta_local_assimila_como_dica_da_questao(self):
        self._configurar_classificador("PEDIR_DICA", resposta_texto="Dica: {texto_dica}")
        questao = self._criar_questao()

        dados, _, mock_ia, mock_assimilar = self._enviar(
            "me dá uma dica", resposta_ia="Use a instrução break.",
            atividade_id=str(self.atividade.id), questao_id=str(questao.id),
        )

        self.assertEqual(dados["origem_resposta"], "IA_EXTERNA")
        mock_ia.assert_called_once()
        mock_assimilar.assert_called_once_with(
            "me dá uma dica",
            "Use a instrução break.",
            questao_id=questao.id,
            atividade_id=self.atividade.id,
            modulo_id=self.modulo.id,
        )


class BaseConhecimentoSuporteContextualTests(APITestCase):
    """Endpoint /api/atividades/{id}/pedir-dica/ segue o mesmo fluxo do chat, no escopo da questão."""

    def setUp(self):
        self.user = User.objects.create_user(
            apelido="aluno_suporte", nome="Bia", email="bia_suporte@example.com", password="password123",
        )
        self.client.force_authenticate(user=self.user)
        self.sessao = Sessao.objects.create(usuario=self.user)
        trilha = Trilha.objects.create(titulo="Python: Fundamentos", habilidade="Programação", ativo=True)
        self.modulo = Modulo.objects.create(
            trilha=trilha, titulo="Estruturas de Repetição", nivel="INICIANTE", ordem_modulo=1,
        )
        self.atividade = Atividade.objects.create(
            modulo=self.modulo, titulo="Exercício de Loops", contexto_avaliacao="CODIGO", ordem=1, ativo=True,
        )
        self.questao = Questao.objects.create(
            atividade=self.atividade,
            tipo_exercicio="MULTIPLA_ESCOLHA",
            enunciado="Como interromper um loop?",
            gabarito_esperado="break",
            dica_conceitual="",
            ordem_questao=1,
        )
        self.url = f"/api/atividades/{self.atividade.id}/pedir-dica/"
        self.payload = {
            "sessao_id": str(self.sessao.id),
            "questao_id": str(self.questao.id),
            "pergunta": "Qual comando interrompe o loop imediatamente?",
        }

    def test_sem_resposta_local_chama_ia_e_assimila_como_dica_da_questao(self):
        with patch("learning.hint_service.HintService._call_external_ai") as mock_ia, \
                patch("assistantManagement.base_conhecimento.BaseConhecimento.assimilar_async") as mock_assimilar:
            mock_ia.return_value = "Use a instrução break para interromper a iteração imediatamente."
            resp = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["origem_resposta"], "IA_EXTERNA")
        self.assertIsNone(resp.data["duvida_assimilada_id"])
        mock_ia.assert_called_once()
        mock_assimilar.assert_called_once_with(
            pergunta="Qual comando interrompe o loop imediatamente?",
            resposta="Use a instrução break para interromper a iteração imediatamente.",
            questao_id=self.questao.id,
            atividade_id=self.atividade.id,
            modulo_id=self.modulo.id,
        )

    def test_dica_assimilada_da_questao_responde_cache_semantico(self):
        duvida = DuvidaAssimilada.objects.create(
            questao=self.questao,
            atividade=self.atividade,
            modulo=self.modulo,
            pergunta_texto="Qual comando interrompe o loop imediatamente?",
            pergunta_normalizada="qual comando interromper loop imediatamente",
            resposta_didatica="Use a instrução break para interromper a iteração imediatamente.",
            embedding=VETOR,
        )

        with patch("learning.hint_service.HintService._call_external_ai") as mock_ia, \
                patch("assistantManagement.base_conhecimento.vetorizar_duvida", return_value=("x", VETOR)):
            resp = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["origem_resposta"], "CACHE_SEMANTICO")
        self.assertIn("instrução break", resp.data["resposta_coach"])
        self.assertEqual(str(resp.data["duvida_assimilada_id"]), str(duvida.id))
        mock_ia.assert_not_called()

        mensagem = Mensagem.objects.filter(sessao=self.sessao, remetente=Mensagem.Remetente.ASSISTENTE).get()
        self.assertEqual(mensagem.origem_resposta, "CACHE_SEMANTICO")
        self.assertEqual(mensagem.duvida_assimilada_id, duvida.id)

    def test_dica_de_outra_questao_da_mesma_atividade_nao_e_reaproveitada(self):
        outra_questao = Questao.objects.create(
            atividade=self.atividade,
            tipo_exercicio="MULTIPLA_ESCOLHA",
            enunciado="Qual o índice do primeiro item de uma lista?",
            gabarito_esperado="0",
            dica_conceitual="",
            ordem_questao=2,
        )
        DuvidaAssimilada.objects.create(
            questao=outra_questao,
            atividade=self.atividade,
            pergunta_texto=self.payload["pergunta"],
            pergunta_normalizada="qual comando interromper loop imediatamente",
            resposta_didatica="Lembre que listas começam no índice zero.",
            embedding=VETOR,
        )

        with patch("learning.hint_service.HintService._call_external_ai") as mock_ia, \
                patch("assistantManagement.base_conhecimento.BaseConhecimento.assimilar_async"), \
                patch("assistantManagement.base_conhecimento.vetorizar_duvida", return_value=("x", VETOR)):
            mock_ia.return_value = "Use a instrução break."
            resp = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(resp.data["origem_resposta"], "IA_EXTERNA")
        mock_ia.assert_called_once()

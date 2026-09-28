from unittest.mock import MagicMock, patch

from rest_framework import status
from rest_framework.test import APITestCase

from activityManagement.models import Atividade
from assistantManagement.models import Sessao
from assistantManagement.services import identificar_trilha_no_texto, texto_para_classificacao
from questionsManagement.models import Questao
from semanticSearch.models import EntradaCorpus, PerguntaCorpus
from trackManagement.models import Matricula, Modulo, ProgressoModulo, Trilha
from userManagement.models import User


class IntencoesChatTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            apelido="aluno_intencoes",
            nome="Ana",
            email="aluno_intencoes@example.com",
            password="password123",
        )
        self.client.force_authenticate(user=self.user)
        self.sessao = Sessao.objects.create(usuario=self.user)
        self.url = f"/api/chat/sessao/{self.sessao.id}/mensagem/"

        self.trilha_fund = Trilha.objects.create(
            titulo="Python: Fundamentos", habilidade="Fundamentos", ativo=True,
        )
        self.trilha_web = Trilha.objects.create(
            titulo="Python: Desenvolvimento Web", habilidade="Desenvolvimento Web", ativo=True,
        )
        self.modulo1 = Modulo.objects.create(
            trilha=self.trilha_fund, titulo="Basico", nivel="Iniciante", ordem_modulo=1,
        )
        self.modulo2 = Modulo.objects.create(
            trilha=self.trilha_fund, titulo="Avancado", nivel="Avancado", ordem_modulo=2,
        )
        self.atividade = Atividade.objects.create(
            modulo=self.modulo1, titulo="Variaveis", contexto_avaliacao="FORMATIVA", ordem=1, ativo=True,
        )
        Modulo.objects.create(
            trilha=self.trilha_web, titulo="APIs", nivel="Iniciante", ordem_modulo=1,
        )

        patchers = [
            patch("assistantManagement.services.TextPreprocessor"),
            patch("assistantManagement.services.EmbeddingService"),
            patch("assistantManagement.services.IntentClassifier"),
        ]
        mock_pre, mock_emb, mock_cls = [p.start() for p in patchers]
        for p in patchers:
            self.addCleanup(p.stop)
        mock_pre.get_instance.return_value.processar.side_effect = lambda texto: texto
        mock_emb.get_instance.return_value.gerar_embedding.return_value = [0.1] * 384
        self.classifier = MagicMock()
        mock_cls.return_value = self.classifier

    def enviar(self, conteudo, intencao, resposta_texto, **extras):
        self.classifier.classificar.return_value = {
            "intencao": intencao,
            "similaridade": 0.9,
            "resposta_texto": resposta_texto,
            "dados_extras": {},
        }
        response = self.client.post(self.url, {"conteudo": conteudo, **extras}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        return response.data["resposta_assistente"]

    # SAUDACAO / AJUDA_COMANDOS
    def test_saudacao_retorna_sugestoes_iniciais(self):
        resp = self.enviar("Olá", "SAUDACAO", "Olá, Ana! Que bom ter você aqui.")
        self.assertEqual(resp["conteudo"], "Olá, Ana! Que bom ter você aqui.")
        self.assertIn("Ver trilhas disponíveis", resp["sugestoes_rapidas"])

    def test_ajuda_comandos_lista_recursos(self):
        resp = self.enviar("O que você pode fazer?", "AJUDA_COMANDOS", "Posso ajudar você.")
        self.assertIn("Quero fazer o teste de nivelamento", resp["sugestoes_rapidas"])
        self.assertIn("Pode me dar uma dica?", resp["sugestoes_rapidas"])

    # MATRICULAR_TRILHA
    def test_matricular_sem_trilha_identificada_pede_escolha(self):
        resp = self.enviar(
            "Quero escolher a trilha de Python", "MATRICULAR_TRILHA",
            "Vamos confirmar sua matrícula na trilha {titulo_trilha}.",
        )
        self.assertEqual(resp["acao"], "SELECIONAR_TRILHA")
        self.assertEqual(len(resp["opcoes_trilhas"]), 2)
        self.assertIn("Quero me matricular na trilha Python: Fundamentos", resp["sugestoes_rapidas"])
        self.assertFalse(Matricula.objects.filter(usuario=self.user).exists())

    def test_matricular_pede_confirmacao_e_depois_efetiva(self):
        resp = self.enviar(
            "Quero me matricular na trilha de fundamentos", "MATRICULAR_TRILHA",
            "Vamos confirmar sua matrícula na trilha {titulo_trilha}.",
        )
        self.assertEqual(resp["acao"], "CONFIRMAR_MATRICULA")
        self.assertEqual(resp["conteudo"], "Vamos confirmar sua matrícula na trilha Python: Fundamentos.")
        self.assertFalse(Matricula.objects.filter(usuario=self.user).exists())
        self.sessao.refresh_from_db()
        self.assertEqual(self.sessao.trilha_contexto, self.trilha_fund)

        # A confirmação herda a trilha do contexto da sessão.
        resp = self.enviar(
            "Confirmo minha matrícula na trilha", "MATRICULAR_TRILHA",
            "Vamos confirmar sua matrícula na trilha {titulo_trilha}.",
        )
        self.assertEqual(resp["acao"], "MATRICULA_EFETIVADA")
        matricula = Matricula.objects.get(usuario=self.user, trilha=self.trilha_fund)
        self.assertEqual(resp["dados_acao"]["matricula_id"], str(matricula.id))
        self.assertEqual(
            ProgressoModulo.objects.get(matricula=matricula, modulo=self.modulo1).status, "EM_ANDAMENTO",
        )
        self.assertIn("Quero começar do zero", resp["sugestoes_rapidas"])

    def test_matricular_trilha_ja_matriculada(self):
        Matricula.objects.create(usuario=self.user, trilha=self.trilha_fund)
        resp = self.enviar(
            "Confirmo", "MATRICULAR_TRILHA", "{titulo_trilha}", trilha_id=str(self.trilha_fund.id),
        )
        self.assertEqual(resp["acao"], "MATRICULA_EXISTENTE")
        self.assertEqual(resp["redirecionar_para"], f"/trilhas/{self.trilha_fund.id}")

    # INICIAR_DIAGNOSTICO
    def test_diagnostico_redireciona_para_atividade_diagnostica(self):
        diag = Atividade.objects.create(
            modulo=self.modulo1, titulo="Diagnostico", contexto_avaliacao="DIAGNOSTICO_INICIAL", ordem=0, ativo=True,
        )
        resp = self.enviar(
            "quero fazer o teste de nivelamento de fundamentos", "INICIAR_DIAGNOSTICO",
            "Vamos começar seu diagnóstico.",
        )
        self.assertEqual(resp["acao"], "INICIAR_TESTE_DIAGNOSTICO")
        self.assertEqual(resp["redirecionar_para"], f"/trilhas/{self.trilha_fund.id}/atividade/{diag.id}")
        matricula = Matricula.objects.get(usuario=self.user, trilha=self.trilha_fund)
        self.assertEqual(resp["dados_acao"]["matricula_id"], str(matricula.id))

    def test_diagnostico_sem_atividade_sugere_comecar_do_zero(self):
        self.sessao.trilha_contexto = self.trilha_fund
        self.sessao.save()
        resp = self.enviar("fazer o teste de nivelamento", "INICIAR_DIAGNOSTICO", "Vamos começar.")
        self.assertIsNone(resp["acao"])
        self.assertEqual(resp["sugestoes_rapidas"], ["Quero começar do zero"])
        self.assertFalse(Matricula.objects.filter(usuario=self.user).exists())

    # INICIAR_DO_ZERO
    def test_iniciar_do_zero_matricula_no_basico(self):
        resp = self.enviar(
            "Quero começar do zero", "INICIAR_DO_ZERO",
            "Você será matriculado no nível inicial da trilha {titulo_trilha}.",
            trilha_id=str(self.trilha_fund.id),
        )
        self.assertEqual(resp["acao"], "INICIAR_DO_INICIO")
        self.assertEqual(resp["conteudo"], "Você será matriculado no nível inicial da trilha Python: Fundamentos.")
        self.assertEqual(
            resp["redirecionar_para"], f"/trilhas/{self.trilha_fund.id}/atividade/{self.atividade.id}",
        )
        matricula = Matricula.objects.get(usuario=self.user, trilha=self.trilha_fund)
        self.assertEqual(
            ProgressoModulo.objects.get(matricula=matricula, modulo=self.modulo2).status, "BLOQUEADO",
        )

    def test_iniciar_do_zero_sem_trilha_pede_escolha(self):
        resp = self.enviar("Quero começar do zero", "INICIAR_DO_ZERO", "{titulo_trilha}")
        self.assertEqual(resp["acao"], "SELECIONAR_TRILHA")
        self.assertIn("Quero começar do zero na trilha Python: Desenvolvimento Web", resp["sugestoes_rapidas"])

    # PEDIR_DICA
    def test_pedir_dica_usa_dica_conceitual_da_questao(self):
        questao = Questao.objects.create(
            atividade=self.atividade, tipo_exercicio="MULTIPLA_ESCOLHA", enunciado="?",
            gabarito_esperado="x", dica_conceitual="Lembre que variáveis guardam valores.", ordem_questao=1,
        )
        resp = self.enviar(
            "Pode me dar uma dica?", "PEDIR_DICA", "Aqui vai uma pista, sem entregar o gabarito: {texto_dica}.",
            atividade_id=str(self.atividade.id),
        )
        self.assertEqual(resp["acao"], "DICA_FORNECIDA")
        self.assertEqual(
            resp["conteudo"], "Aqui vai uma pista, sem entregar o gabarito: Lembre que variáveis guardam valores.",
        )
        self.assertEqual(resp["dados_acao"]["questao_id"], str(questao.id))

    def test_pedir_dica_sem_atividade_orienta_estudante(self):
        resp = self.enviar("Pode me dar uma dica?", "PEDIR_DICA", "Pista: {texto_dica}.")
        self.assertIsNone(resp["acao"])
        self.assertNotIn("{texto_dica}", resp["conteudo"])

    def test_pedir_dica_questao_de_outra_atividade_retorna_404(self):
        outra = Atividade.objects.create(modulo=self.modulo2, titulo="Outra", ordem=1, ativo=True)
        questao = Questao.objects.create(
            atividade=outra, tipo_exercicio="X", enunciado="?", gabarito_esperado="x", ordem_questao=1,
        )
        self.classifier.classificar.return_value = {
            "intencao": "PEDIR_DICA", "similaridade": 0.9, "resposta_texto": "{texto_dica}", "dados_extras": {},
        }
        response = self.client.post(
            self.url,
            {"conteudo": "dica", "atividade_id": str(self.atividade.id), "questao_id": str(questao.id)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    # DUVIDA_CONTEUDO
    def _entrada_corpus(self, pergunta, topico="Variáveis", embedding=None):
        entrada = EntradaCorpus.objects.create(topico=topico, pergunta=pergunta, resposta=f"Resposta de {pergunta}")
        PerguntaCorpus.objects.create(entrada=entrada, texto=pergunta, embedding=embedding or [0.1] * 384)
        return entrada

    def test_duvida_conteudo_responde_com_corpus(self):
        entrada = self._entrada_corpus("Como definir uma variável em Python?")
        eixo = [0.0] * 384
        eixo[0] = 1.0
        self._entrada_corpus("O que é uma constante?", embedding=eixo)

        resp = self.enviar(
            "como definir uma variável em python", "DUVIDA_CONTEUDO", "Boa pergunta! {resposta_corpus}",
        )

        self.assertEqual(resp["acao"], "RESPOSTA_CORPUS")
        self.assertEqual(resp["conteudo"], "Boa pergunta! Resposta de Como definir uma variável em Python?")
        self.assertEqual(resp["dados_acao"]["entrada_corpus_id"], str(entrada.id))
        self.assertEqual(resp["sugestoes_rapidas"], ["O que é uma constante?"])

    def test_duvida_conteudo_sem_resultado_no_corpus(self):
        resp = self.enviar("o que é recursão?", "DUVIDA_CONTEUDO", "{resposta_corpus}")
        self.assertIsNone(resp["acao"])
        self.assertIn("base de conhecimento", resp["conteudo"])
        self.assertNotIn("{resposta_corpus}", resp["conteudo"])

    def test_fallback_encontrado_no_corpus_vira_duvida_conteudo(self):
        self._entrada_corpus("O que é self?")
        resp = self.enviar("pra que serve o self", "FALLBACK", "Hmm, não entendi muito bem.")
        self.assertEqual(resp["intencao_detectada"], "DUVIDA_CONTEUDO")
        self.assertEqual(resp["conteudo"], "Resposta de O que é self?")


class IdentificarTrilhaNoTextoTests(APITestCase):
    def setUp(self):
        self.trilhas = [
            Trilha(titulo="Python: Fundamentos", habilidade="Fundamentos"),
            Trilha(titulo="Python: Desenvolvimento Web", habilidade="Desenvolvimento Web"),
            Trilha(titulo="Python: Analise de Dados", habilidade="Analise de Dados"),
        ]

    def test_identifica_por_palavra_distintiva_sem_acento(self):
        self.assertEqual(identificar_trilha_no_texto("quero a de análise de dados", self.trilhas), self.trilhas[2])
        self.assertEqual(identificar_trilha_no_texto("trilha WEB por favor", self.trilhas), self.trilhas[1])

    def test_identifica_titulo_completo(self):
        texto = "Quero me matricular na trilha Python: Fundamentos"
        self.assertEqual(identificar_trilha_no_texto(texto, self.trilhas), self.trilhas[0])

    def test_palavra_compartilhada_nao_identifica(self):
        self.assertIsNone(identificar_trilha_no_texto("Quero a trilha de Python", self.trilhas))

    def test_texto_para_classificacao_remove_mencao_da_trilha(self):
        preprocessor = MagicMock()
        preprocessor.processar.side_effect = lambda texto: texto
        texto = texto_para_classificacao(
            preprocessor, "Quero começar do zero na trilha Python: Análise de Dados", self.trilhas,
        )
        self.assertEqual(texto, "quero comecar do zero na trilha")

    def test_texto_para_classificacao_sem_mencao_preserva_texto(self):
        preprocessor = MagicMock()
        preprocessor.processar.side_effect = lambda texto: texto
        self.assertEqual(texto_para_classificacao(preprocessor, "Olá, Coach!", self.trilhas), "Olá, Coach!")

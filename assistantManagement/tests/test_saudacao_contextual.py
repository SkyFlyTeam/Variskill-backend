import re
from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from activityManagement.models import Atividade, ExecucaoAtividade, RespostaQuestao
from assistantManagement.services import iniciar_sessao_chat
from intents.management.commands.seed_intencoes import INTENCOES_CANONICAS
from intents.models import Intention, Response
from questionsManagement.models import Questao
from trackManagement.models import Matricula, Modulo, ProgressoModulo, Trilha
from userManagement.models import User

SLOTS_PERMITIDOS = {"nome", "streak_dias", "nome_atividade", "nome_modulo", "topico_dificuldade", "ponto_forte"}
CATEGORIAS_CONTEXTUAIS = {
    "SAUDACAO_BOAS_VINDAS", "SAUDACAO_STREAK", "SAUDACAO_RETORNO", "SAUDACAO_RETOMADA", "SAUDACAO_REFORCO",
}


class CatalogoSaudacaoSeedTests(APITestCase):
    def test_categorias_contextuais_nao_tem_exemplos_e_usam_apenas_slots_permitidos(self):
        catalogo = {item["code"]: item for item in INTENCOES_CANONICAS}
        for codigo in CATEGORIAS_CONTEXTUAIS:
            self.assertIn(codigo, catalogo)
            # Sem exemplos, o classificador nunca retorna a categoria diretamente.
            self.assertEqual(catalogo[codigo]["examples"], [])
            self.assertTrue(catalogo[codigo]["responses"])
            for template in catalogo[codigo]["responses"]:
                self.assertLessEqual(set(re.findall(r"\{(\w+)\}", template)), SLOTS_PERMITIDOS, template)

    def test_templates_de_reforco_sempre_citam_o_topico(self):
        reforco = next(i for i in INTENCOES_CANONICAS if i["code"] == "SAUDACAO_REFORCO")
        for template in reforco["responses"]:
            self.assertIn("{topico_dificuldade}", template)


class SaudacaoContextualTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            apelido="aluno_contexto", nome="Paula", email="aluno_contexto@example.com", password="password123",
        )
        self.trilha = Trilha.objects.create(titulo="Python: Fundamentos", habilidade="Fundamentos", ativo=True)
        self.modulo = Modulo.objects.create(
            trilha=self.trilha, titulo="Variáveis e Tipos", nivel="Iniciante", ordem_modulo=1,
        )
        self.atividade = Atividade.objects.create(
            modulo=self.modulo, titulo="Declarando variáveis", contexto_avaliacao="FORMATIVA", ordem=1, ativo=True,
        )

    def _matricular(self):
        matricula = Matricula.objects.create(usuario=self.user, trilha=self.trilha, status="EM_ANDAMENTO")
        ProgressoModulo.objects.create(matricula=matricula, modulo=self.modulo, status="EM_ANDAMENTO")
        return matricula

    def _definir_streak(self, dias, ultimo_dia_estudo):
        User.objects.filter(pk=self.user.pk).update(streak_dias=dias, ultimo_dia_estudo=ultimo_dia_estudo)
        self.user.refresh_from_db()

    def _criar_dificuldade(self):
        questoes = [
            Questao.objects.create(
                atividade=self.atividade, tipo_exercicio="MULTIPLA_ESCOLHA",
                enunciado=f"Q{i}", gabarito_esperado="a", ordem_questao=i,
            )
            for i in (1, 2)
        ]
        execucao = ExecucaoAtividade.objects.create(
            usuario=self.user, atividade=self.atividade, resposta={}, pontuacao_obtida=0, aprovado=False,
        )
        RespostaQuestao.objects.bulk_create([
            RespostaQuestao(execucao=execucao, questao=q, resposta_fornecida="x", correta=False) for q in questoes
        ])

    def _abrir(self):
        return iniciar_sessao_chat(self.user)["mensagem_inicial"]

    def test_novato_recebe_boas_vindas_do_catalogo(self):
        mensagem = self._abrir()
        boas_vindas = next(i for i in INTENCOES_CANONICAS if i["code"] == "SAUDACAO_BOAS_VINDAS")
        textos = [t.replace("{nome}", "Paula") for t in boas_vindas["responses"]]
        self.assertIn(mensagem["conteudo"], textos)
        self.assertIn("Ver trilhas disponíveis", mensagem["sugestoes_rapidas"])

    def test_streak_ativo_reconhece_dias_seguidos(self):
        self._definir_streak(5, timezone.localdate())
        mensagem = self._abrir()
        self.assertIn("5", mensagem["conteudo"])
        self.assertIn("Paula", mensagem["conteudo"])

    def test_streak_interrompido_nao_e_celebrado_e_dispara_retorno(self):
        self._definir_streak(7, timezone.localdate() - timedelta(days=5))
        mensagem = self._abrir()
        self.assertNotIn("7", mensagem["conteudo"])
        retorno = next(i for i in INTENCOES_CANONICAS if i["code"] == "SAUDACAO_RETORNO")
        textos = [t.replace("{nome}", "Paula") for t in retorno["responses"] if "{nome_" not in t]
        self.assertIn(mensagem["conteudo"], textos)

    def test_atividade_pendente_gera_retomada_e_chips_dinamicos(self):
        self._matricular()
        mensagem = self._abrir()
        self.assertIn("Declarando variáveis", mensagem["conteudo"])
        self.assertEqual(
            mensagem["sugestoes_rapidas"],
            ["Continuar Declarando variáveis", "Tirar uma dúvida", "Ver meu progresso"],
        )

    def test_reforco_tem_prioridade_e_chips_combinam_revisao_e_continuidade(self):
        self._matricular()
        self._definir_streak(4, timezone.localdate())
        self._criar_dificuldade()
        mensagem = self._abrir()
        self.assertIn("Variáveis e Tipos", mensagem["conteudo"])
        self.assertEqual(mensagem["sugestoes_rapidas"][:2], [
            "Quero revisar Variáveis e Tipos", "Continuar Declarando variáveis",
        ])

    def test_templates_do_banco_prevalecem_sobre_o_seed(self):
        intencao = Intention.objects.create(code="SAUDACAO_STREAK", system_action="X", description="X")
        Response.objects.create(intention=intencao, text="Ofensiva de {streak_dias} dias, {nome}!")
        self._definir_streak(3, timezone.localdate())
        self.assertEqual(self._abrir()["conteudo"], "Ofensiva de 3 dias, Paula!")

    def test_payload_fica_abaixo_de_250_tokens_com_titulos_longos(self):
        self.atividade.titulo = "Atividade " * 20
        self.atividade.save()
        self.modulo.titulo = "Módulo " * 14
        self.modulo.save()
        self._matricular()
        self._definir_streak(10, timezone.localdate())
        self._criar_dificuldade()
        mensagem = self._abrir()
        caracteres = len(mensagem["conteudo"]) + sum(len(s) for s in mensagem["sugestoes_rapidas"])
        # Aproximação conservadora de ~4 caracteres por token.
        self.assertLess(caracteres, 250 * 4)


class SaudacaoContextualChatTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            apelido="aluno_chat_ctx", nome="Rui", email="aluno_chat_ctx@example.com", password="password123",
        )
        self.client.force_authenticate(user=self.user)
        trilha = Trilha.objects.create(titulo="Python: Fundamentos", habilidade="Fundamentos", ativo=True)
        modulo = Modulo.objects.create(trilha=trilha, titulo="Laços", nivel="Iniciante", ordem_modulo=1)
        self.atividade = Atividade.objects.create(
            modulo=modulo, titulo="Laço for", contexto_avaliacao="FORMATIVA", ordem=1, ativo=True,
        )
        matricula = Matricula.objects.create(usuario=self.user, trilha=trilha, status="EM_ANDAMENTO")
        ProgressoModulo.objects.create(matricula=matricula, modulo=modulo, status="EM_ANDAMENTO")

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
        classifier = MagicMock()
        classifier.classificar.return_value = {
            "intencao": "SAUDACAO", "similaridade": 0.9, "resposta_texto": "Olá, Rui!", "dados_extras": {},
        }
        mock_cls.return_value = classifier

    def test_saudacao_no_chat_sugere_continuidade_da_proxima_atividade(self):
        sessao_id = iniciar_sessao_chat(self.user)["sessao_id"]
        response = self.client.post(f"/api/chat/sessao/{sessao_id}/mensagem/", {"conteudo": "Oi"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        resp = response.data["resposta_assistente"]

        self.assertIn("Laço for", resp["conteudo"])
        self.assertIn("Continuar Laço for", resp["sugestoes_rapidas"])
        self.assertEqual(resp["dados_acao"]["categoria_saudacao"], "SAUDACAO_RETOMADA")
        self.assertEqual(resp["dados_acao"]["atividade_id"], str(self.atividade.id))

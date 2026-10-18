import uuid
from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from model_bakery import baker

from activityManagement.models import Atividade, ExecucaoAtividade, RespostaQuestao
from assistantManagement.models import Sessao
from assistantManagement.services import (
    HANDLERS_INTENCAO,
    ResumoPedagogico,
    agregar_historico_pedagogico,
    enviar_mensagem_chat,
)
from questionsManagement.models import Questao
from trackManagement.models import Modulo, Trilha
from userManagement.models import User


def make_atividade(modulo, ordem=1):
    return baker.make(Atividade, modulo=modulo, ordem=ordem, ativo=True)


def make_questao(atividade, ordem=1):
    return baker.make(Questao, atividade=atividade, ordem_questao=ordem)


def make_execucao_com_respostas(usuario, atividade, respostas, **kwargs):
    """Cria uma ExecucaoAtividade e suas RESPOSTA_QUESTAO (lista de (questao, correta))."""
    execucao = baker.make(
        ExecucaoAtividade, usuario=usuario, atividade=atividade,
        resposta={}, aprovado=kwargs.get("aprovado", False),
        pontuacao_obtida=kwargs.get("pontuacao_obtida", 0),
    )
    if kwargs.get("executado_em"):
        ExecucaoAtividade.objects.filter(pk=execucao.pk).update(executado_em=kwargs["executado_em"])
        execucao.refresh_from_db()
    RespostaQuestao.objects.bulk_create([
        RespostaQuestao(execucao=execucao, questao=questao, resposta_fornecida="[]", correta=correta)
        for questao, correta in respostas
    ])
    return execucao


class AgregarHistoricoPedagogicoTests(TestCase):
    def setUp(self):
        self.user = baker.make(User, apelido="estudante_historico")
        self.trilha = Trilha.objects.create(titulo="Trilha Python", habilidade="Backend", ativo=True)

    def test_modulo_abaixo_de_70_por_cento_entra_em_dificuldade(self):
        modulo = Modulo.objects.create(trilha=self.trilha, titulo="Módulo Fraco", nivel="INICIANTE", ordem_modulo=1)
        atividade = make_atividade(modulo)
        q1, q2, q3 = (make_questao(atividade, ordem=i) for i in range(1, 4))
        make_execucao_com_respostas(self.user, atividade, [(q1, True), (q2, False), (q3, False)])

        resumo = agregar_historico_pedagogico(self.user)

        self.assertEqual(len(resumo.modulos_com_dificuldade), 1)
        item = resumo.modulos_com_dificuldade[0]
        self.assertEqual(item["modulo_id"], modulo.id)
        self.assertEqual(item["titulo"], "Módulo Fraco")
        self.assertAlmostEqual(item["taxa_acerto"], 33.3, places=1)
        self.assertEqual(resumo.modulos_com_dominio, [])

    def test_modulo_igual_ou_acima_de_80_por_cento_entra_em_dominio(self):
        modulo = Modulo.objects.create(trilha=self.trilha, titulo="Módulo Forte", nivel="INICIANTE", ordem_modulo=1)
        atividade = make_atividade(modulo)
        questoes = [make_questao(atividade, ordem=i) for i in range(1, 6)]
        respostas = [(q, True) for q in questoes[:4]] + [(questoes[4], False)]  # 4/5 = 80%
        make_execucao_com_respostas(self.user, atividade, respostas)

        resumo = agregar_historico_pedagogico(self.user)

        self.assertEqual(resumo.modulos_com_dificuldade, [])
        self.assertEqual(len(resumo.modulos_com_dominio), 1)
        self.assertEqual(resumo.modulos_com_dominio[0]["modulo_id"], modulo.id)
        self.assertEqual(resumo.modulos_com_dominio[0]["taxa_acerto"], 80.0)

    def test_modulo_entre_70_e_80_nao_entra_em_nenhuma_lista(self):
        modulo = Modulo.objects.create(trilha=self.trilha, titulo="Módulo Médio", nivel="INICIANTE", ordem_modulo=1)
        atividade = make_atividade(modulo)
        questoes = [make_questao(atividade, ordem=i) for i in range(1, 11)]
        respostas = [(q, idx < 7) for idx, q in enumerate(questoes)]  # 7/10 = 70%, nem dificuldade nem dominio
        make_execucao_com_respostas(self.user, atividade, respostas)

        resumo = agregar_historico_pedagogico(self.user)

        self.assertEqual(resumo.modulos_com_dificuldade, [])
        self.assertEqual(resumo.modulos_com_dominio, [])

    def test_considera_apenas_a_ultima_execucao_de_cada_atividade(self):
        modulo = Modulo.objects.create(trilha=self.trilha, titulo="Módulo 1", nivel="INICIANTE", ordem_modulo=1)
        atividade = make_atividade(modulo)
        questao = make_questao(atividade)

        make_execucao_com_respostas(
            self.user, atividade, [(questao, False)],
            executado_em=timezone.now() - timedelta(hours=1),
        )
        make_execucao_com_respostas(self.user, atividade, [(questao, True)])

        resumo = agregar_historico_pedagogico(self.user)

        self.assertEqual(resumo.modulos_com_dificuldade, [])
        self.assertEqual(len(resumo.modulos_com_dominio), 1)
        self.assertEqual(resumo.modulos_com_dominio[0]["taxa_acerto"], 100.0)

    def test_nao_mistura_historico_de_outro_usuario(self):
        outro = baker.make(User, apelido="outro_estudante_historico")
        modulo = Modulo.objects.create(trilha=self.trilha, titulo="Módulo 1", nivel="INICIANTE", ordem_modulo=1)
        atividade = make_atividade(modulo)
        questao = make_questao(atividade)
        make_execucao_com_respostas(outro, atividade, [(questao, False)])

        resumo = agregar_historico_pedagogico(self.user)

        self.assertEqual(resumo.modulos_com_dificuldade, [])
        self.assertEqual(resumo.modulos_com_dominio, [])

    def test_sem_execucoes_retorna_resumo_vazio(self):
        resumo = agregar_historico_pedagogico(self.user)

        self.assertEqual(resumo.modulos_com_dificuldade, [])
        self.assertEqual(resumo.modulos_com_dominio, [])

    def test_consulta_eficiente_sem_queries_redundantes(self):
        # Vários módulos/atividades/questões: o número de queries não deve crescer
        # com a quantidade de dados (sem N+1 ao acessar execucao/atividade/modulo).
        for i in range(4):
            modulo = Modulo.objects.create(
                trilha=self.trilha, titulo=f"Módulo {i}", nivel="INICIANTE", ordem_modulo=i + 1,
            )
            atividade = make_atividade(modulo, ordem=1)
            questoes = [make_questao(atividade, ordem=j) for j in range(1, 4)]
            make_execucao_com_respostas(
                self.user, atividade, [(q, j % 2 == 0) for j, q in enumerate(questoes)],
            )

        with CaptureQueriesContext(connection) as capturado:
            agregar_historico_pedagogico(self.user)

        self.assertEqual(len(capturado.captured_queries), 2)


class InjecaoResumoPedagogicoNoContextoTests(TestCase):
    def setUp(self):
        self.user = baker.make(User, apelido="estudante_chat_historico")

    @patch("assistantManagement.services.agregar_historico_pedagogico")
    @patch("assistantManagement.services.IntentClassifier")
    @patch("assistantManagement.services.EmbeddingService")
    @patch("assistantManagement.services.TextPreprocessor")
    def test_resumo_pedagogico_chega_populado_ao_despachador_da_intencao(
        self, mock_preprocessor_cls, mock_embedding_cls, mock_classifier_cls, mock_agregar,
    ):
        resumo_esperado = ResumoPedagogico(
            modulos_com_dificuldade=[{"modulo_id": uuid.uuid4(), "titulo": "Módulo X", "taxa_acerto": 40.0}],
            modulos_com_dominio=[{"modulo_id": uuid.uuid4(), "titulo": "Módulo Y", "taxa_acerto": 90.0}],
        )
        mock_agregar.return_value = resumo_esperado

        mock_preprocessor = MagicMock()
        mock_preprocessor.processar.return_value = "oi"
        mock_preprocessor_cls.get_instance.return_value = mock_preprocessor

        mock_embedding = MagicMock()
        mock_embedding.gerar_embedding.return_value = [0.1] * 384
        mock_embedding_cls.get_instance.return_value = mock_embedding

        mock_classifier = MagicMock()
        mock_classifier.classificar.return_value = {
            "intencao": "SAUDACAO",
            "similaridade": 0.95,
            "resposta_texto": "Oi!",
            "dados_extras": {},
        }
        mock_classifier_cls.return_value = mock_classifier

        sessao = Sessao.objects.create(usuario=self.user)

        ctx_capturado = {}
        handler_original = HANDLERS_INTENCAO["SAUDACAO"]

        def handler_espiao(ctx):
            ctx_capturado["ctx"] = ctx
            return handler_original(ctx)

        with patch.dict("assistantManagement.services.HANDLERS_INTENCAO", {"SAUDACAO": handler_espiao}):
            enviar_mensagem_chat(self.user, sessao.id, "Oi")

        mock_agregar.assert_called_once_with(self.user)

        ctx = ctx_capturado["ctx"]
        self.assertIs(ctx.resumo_pedagogico, resumo_esperado)
        self.assertEqual(ctx.resumo_pedagogico.modulos_com_dificuldade[0]["titulo"], "Módulo X")
        self.assertEqual(ctx.resumo_pedagogico.modulos_com_dominio[0]["titulo"], "Módulo Y")

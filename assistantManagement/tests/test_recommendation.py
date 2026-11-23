import uuid
from unittest.mock import MagicMock, patch

from rest_framework import status
from rest_framework.test import APITestCase

from assistantManagement.models import Mensagem, Sessao
from assistantManagement.services import (
    _recomendar_trilhas_contextual,
    _singular,
    _tema_da_mensagem,
    _tema_do_pedido,
    identificar_modulos_no_texto,
    texto_sem_tema,
)
from intents.models import Intention, Response
from trackManagement.models import Matricula, Modulo, Trilha
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



@patch("assistantManagement.services.TextPreprocessor.get_instance")
@patch("assistantManagement.services.EmbeddingService.get_instance")
@patch(
    "assistantManagement.services.IntentClassifier.classificar",
    return_value={"intencao": "RECOMENDAR_TRILHA", "similaridade": 0.95, "resposta_texto": ""},
)
class RecomendacaoPorTemaTests(APITestCase):
    """Pedidos como "Quero aprender X, por onde começo?" recomendam a trilha do tema citado."""

    def setUp(self):
        self.user = User.objects.create_user(
            apelido="aluno_tema", nome="Bia", email="aluno_tema@example.com", password="password123",
        )
        self.client.force_authenticate(user=self.user)
        Intention.objects.create(
            code="RECOMENDAR_TRILHA", system_action="RECOMENDAR_TRILHAS_CONTEXTUAL", description="Recomendação",
        )

        self.fundamentos = self._trilha("Python: Fundamentos", "Python", "Variaveis e Tipos")
        self.web = self._trilha("Python: Desenvolvimento Web", "Backend", "APIs com FastAPI")
        self.dados = self._trilha("Python: Analise de Dados", "Ciência de Dados", "NumPy")
        self.devops = self._trilha("DevOps e Cloud: Docker e CI/CD", "DevOps/Cloud", "Containers com Docker")
        self.banco = self._trilha("Banco de Dados: SQL e Modelagem", "Banco de Dados", "Consultas SQL")
        self.sessao = Sessao.objects.create(usuario=self.user)

    @staticmethod
    def _trilha(titulo, habilidade, primeiro_modulo):
        trilha = Trilha.objects.create(
            titulo=titulo, habilidade=habilidade, descricao=f"Descricao de {titulo}.", ativo=True,
        )
        Modulo.objects.create(trilha=trilha, titulo=primeiro_modulo, nivel="INICIANTE", ordem_modulo=1)
        return trilha

    def _enviar(self, mock_prep_inst, mock_embed_inst, texto):
        mock_prep_inst.return_value.processar.return_value = texto
        mock_embed_inst.return_value.gerar_embedding.return_value = [0.1] * 384
        response = self.client.post(
            f"/api/chat/sessao/{self.sessao.id}/mensagem/", {"conteudo": texto}, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data["resposta_assistente"]

    def test_recomenda_trilha_do_tema_e_guarda_no_contexto_da_sessao(self, _clf, mock_embed, mock_prep):
        dados = self._enviar(mock_prep, mock_embed, "Quero entender devops, qual trilha faço?")

        self.assertEqual(dados["intencao_detectada"], "RECOMENDAR_TRILHA")
        self.assertEqual(dados["acao"], "RECOMENDACAO_TRILHA")
        self.assertEqual([t["titulo"] for t in dados["opcoes_trilhas"]], [self.devops.titulo])
        self.assertIn("**DevOps e Cloud: Docker e CI/CD**", dados["conteudo"])
        self.assertIn("Containers com Docker", dados["conteudo"])
        self.assertIn("Quero começar do zero", dados["sugestoes_rapidas"])
        self.assertIn("Quero fazer o teste de nivelamento", dados["sugestoes_rapidas"])
        self.sessao.refresh_from_db()
        self.assertEqual(self.sessao.trilha_contexto, self.devops)

    def test_linguagem_compartilhada_recomenda_a_trilha_da_habilidade(self, _clf, mock_embed, mock_prep):
        dados = self._enviar(mock_prep, mock_embed, "Quero aprender python, por onde começo?")

        self.assertEqual([t["titulo"] for t in dados["opcoes_trilhas"]], [self.fundamentos.titulo])

    def test_tema_mais_especifico_prevalece_sobre_a_linguagem(self, _clf, mock_embed, mock_prep):
        dados = self._enviar(mock_prep, mock_embed, "QUero aprender análise de dados em python.")

        self.assertEqual([t["titulo"] for t in dados["opcoes_trilhas"]], [self.dados.titulo])

    def test_termo_de_varias_trilhas_pede_para_o_estudante_escolher(self, _clf, mock_embed, mock_prep):
        dados = self._enviar(mock_prep, mock_embed, "Quero aprender dados")

        self.assertEqual(
            {t["titulo"] for t in dados["opcoes_trilhas"]}, {self.dados.titulo, self.banco.titulo},
        )
        self.assertIn("mais de uma trilha", dados["conteudo"])
        self.sessao.refresh_from_db()
        self.assertIsNone(self.sessao.trilha_contexto)

    def test_estudante_ja_matriculado_e_levado_a_continuar(self, _clf, mock_embed, mock_prep):
        Matricula.objects.create(usuario=self.user, trilha=self.devops, status="EM_ANDAMENTO")

        dados = self._enviar(mock_prep, mock_embed, "Quero aprender devops")

        self.assertIn("já está matriculado", dados["conteudo"])
        self.assertEqual(dados["redirecionar_para"], f"/trilhas/{self.devops.id}")
        self.assertIn("O que estudar agora?", dados["sugestoes_rapidas"])

    def test_trilha_do_tema_concluida_sugere_proximas_trilhas(self, _clf, mock_embed, mock_prep):
        Matricula.objects.create(usuario=self.user, trilha=self.devops, status="CONCLUIDO")

        dados = self._enviar(mock_prep, mock_embed, "Quero aprender devops")

        self.assertIn("já concluiu", dados["conteudo"])
        titulos = [t["titulo"] for t in dados["opcoes_trilhas"]]
        self.assertTrue(titulos)
        self.assertNotIn(self.devops.titulo, titulos)

    def test_sem_tema_mantem_recomendacao_por_interesses(self, _clf, mock_embed, mock_prep):
        dados = self._enviar(mock_prep, mock_embed, "Qual trilha você me recomenda?")

        self.assertEqual(len(dados["opcoes_trilhas"]), 3)
        self.assertNotIn("Para esse tema", dados["conteudo"])


def _trilha_gerada_pela_ia(titulo="Culinária: Primeiros Passos", habilidade="Culinária"):
    def questao(n):
        return {
            "enunciado": f"Pergunta {n}?",
            "opcoes": ["A", "B", "C", "D"],
            "gabarito_idx": n % 4,
            "dica": f"Dica {n}",
        }

    return {
        "resultado": "NOVA_TRILHA",
        "trilha_existente": None,
        "trilha": {
            "titulo": titulo,
            "descricao": "Aprenda o básico da cozinha.",
            "habilidade": habilidade,
            "modulos": [
                {
                    "titulo": f"Módulo {m}",
                    "descricao": f"Descrição {m}",
                    "nivel": "INICIANTE",
                    "licao": {"titulo": f"Lição {m}", "texto": "### Aula\n\nConteúdo."},
                    "questoes": [questao(n) for n in range(3)],
                }
                for m in (1, 2)
            ],
        }
    }


@patch("trackManagement.geracao_trilha.HintService.call_external_ai_json")
@patch("assistantManagement.services.TextPreprocessor.get_instance")
@patch("assistantManagement.services.EmbeddingService.get_instance")
@patch(
    "assistantManagement.services.IntentClassifier.classificar",
    return_value={"intencao": "RECOMENDAR_TRILHA", "similaridade": 0.95, "resposta_texto": ""},
)
class RecomendacaoComTrilhaGeradaTests(APITestCase):
    """Tema sem trilha no catálogo (ex.: "Quero aprender culinária") ganha uma trilha gerada pela IA."""

    def setUp(self):
        self.user = User.objects.create_user(
            apelido="aluno_ia", nome="Caio", email="aluno_ia@example.com", password="password123",
        )
        self.client.force_authenticate(user=self.user)
        Intention.objects.create(
            code="RECOMENDAR_TRILHA", system_action="RECOMENDAR_TRILHAS_CONTEXTUAL", description="Recomendação",
        )
        self.fundamentos = Trilha.objects.create(titulo="Python: Fundamentos", habilidade="Python", ativo=True)
        Modulo.objects.create(trilha=self.fundamentos, titulo="Variaveis", nivel="INICIANTE", ordem_modulo=1)
        self.sessao = Sessao.objects.create(usuario=self.user)

    def _enviar(self, mock_prep_inst, mock_embed_inst, texto):
        mock_prep_inst.return_value.processar.return_value = texto
        mock_embed_inst.return_value.gerar_embedding.return_value = [0.1] * 384
        response = self.client.post(
            f"/api/chat/sessao/{self.sessao.id}/mensagem/", {"conteudo": texto}, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data["resposta_assistente"]

    def test_tema_sem_trilha_gera_e_recomenda_trilha_nova(self, _clf, mock_embed, mock_prep, mock_ia):
        mock_ia.return_value = _trilha_gerada_pela_ia()

        dados = self._enviar(mock_prep, mock_embed, "QUero aprender culinária, por onde começo?")

        trilha = Trilha.objects.get(titulo="Culinária: Primeiros Passos")
        self.assertTrue(trilha.ativo)
        self.assertTrue(trilha.gerada_por_ia)
        self.assertEqual(trilha.criada_por, self.user)
        self.assertEqual(trilha.modulos.count(), 2)
        for modulo in trilha.modulos.all():
            licao, exercicio = modulo.atividades.order_by("ordem")
            self.assertIsNotNone(licao.conteudo)
            questoes = list(exercicio.questoes.all())
            self.assertEqual(len(questoes), 3)
            self.assertEqual(sum(q.peso_pontuacao for q in questoes), exercicio.xp_recompensa)
            for n, questao in enumerate(questoes):
                correta = questao.opcoes.get(id=questao.gabarito_esperado)
                self.assertEqual(correta.texto_opcao, "ABCD"[n % 4])

        self.assertEqual(dados["acao"], "RECOMENDACAO_TRILHA")
        self.assertEqual(dados["origem_resposta"], "IA_EXTERNA")
        self.assertTrue(dados["dados_acao"]["trilha_gerada"])
        self.assertEqual(
            [(t["titulo"], t["gerada_por_ia"]) for t in dados["opcoes_trilhas"]], [(trilha.titulo, True)],
        )
        self.assertIn("criei uma para você", dados["conteudo"])
        self.assertIn("Quero começar do zero", dados["sugestoes_rapidas"])
        self.sessao.refresh_from_db()
        self.assertEqual(self.sessao.trilha_contexto, trilha)

    def test_trilha_gerada_e_reaproveitada_no_proximo_pedido(self, _clf, mock_embed, mock_prep, mock_ia):
        mock_ia.return_value = _trilha_gerada_pela_ia()
        self._enviar(mock_prep, mock_embed, "Quero aprender culinária")

        dados = self._enviar(mock_prep, mock_embed, "Quero aprender culinária, por onde começo?")

        mock_ia.assert_called_once()
        self.assertEqual(Trilha.objects.filter(gerada_por_ia=True).count(), 1)
        self.assertEqual([t["titulo"] for t in dados["opcoes_trilhas"]], ["Culinária: Primeiros Passos"])

    def test_ia_indica_trilha_existente_sem_criar_outra(self, _clf, mock_embed, mock_prep, mock_ia):
        mock_ia.return_value = {"resultado": "TRILHA_EXISTENTE", "trilha_existente": "Python: Fundamentos", "trilha": None}

        dados = self._enviar(mock_prep, mock_embed, "Quero aprender programação, por onde começo?")

        self.assertFalse(Trilha.objects.filter(gerada_por_ia=True).exists())
        self.assertEqual([t["titulo"] for t in dados["opcoes_trilhas"]], [self.fundamentos.titulo])
        self.assertFalse(dados["dados_acao"]["trilha_gerada"])
        self.assertNotIn("criei", dados["conteudo"])

    def test_ia_indisponivel_mantem_recomendacao_por_interesses(self, _clf, mock_embed, mock_prep, mock_ia):
        mock_ia.return_value = None

        dados = self._enviar(mock_prep, mock_embed, "Quero aprender culinária")

        self.assertFalse(Trilha.objects.filter(gerada_por_ia=True).exists())
        self.assertIn("Ainda não temos uma trilha sobre esse tema", dados["conteudo"])
        self.assertEqual([t["titulo"] for t in dados["opcoes_trilhas"]], [self.fundamentos.titulo])

    def test_limite_de_trilhas_geradas_por_estudante(self, _clf, mock_embed, mock_prep, mock_ia):
        for tema in ("Violão", "Fotografia"):
            Trilha.objects.create(
                titulo=f"{tema}: Primeiros Passos", habilidade=tema, gerada_por_ia=True, criada_por=self.user,
            )

        dados = self._enviar(mock_prep, mock_embed, "Quero aprender culinária")

        mock_ia.assert_not_called()
        self.assertFalse(Trilha.objects.filter(habilidade="Culinária").exists())
        self.assertIn("o limite por estudante", dados["conteudo"])
        self.assertTrue(dados["opcoes_trilhas"])

    def test_trilha_gerada_por_outro_estudante_nao_conta_no_limite(self, _clf, mock_embed, mock_prep, mock_ia):
        outro = User.objects.create_user(apelido="outro_ia", nome="Ana", email="outro_ia@example.com", password="x")
        for tema in ("Violão", "Fotografia"):
            Trilha.objects.create(
                titulo=f"{tema}: Primeiros Passos", habilidade=tema, gerada_por_ia=True, criada_por=outro,
            )
        mock_ia.return_value = _trilha_gerada_pela_ia()

        self._enviar(mock_prep, mock_embed, "Quero aprender culinária")

        self.assertTrue(Trilha.objects.filter(criada_por=self.user, gerada_por_ia=True).exists())

    def test_tema_fora_de_escopo_nao_gera_trilha(self, _clf, mock_embed, mock_prep, mock_ia):
        mock_ia.return_value = {"resultado": "FORA_DE_ESCOPO", "trilha_existente": None, "trilha": None}

        self._enviar(mock_prep, mock_embed, "Quero aprender a fazer bombas")

        self.assertFalse(Trilha.objects.filter(gerada_por_ia=True).exists())

    def test_trilha_com_menos_modulos_validos_e_descartada(self, _clf, mock_embed, mock_prep, mock_ia):
        resposta = _trilha_gerada_pela_ia()
        resposta["trilha"]["modulos"][1]["questoes"] = [{"enunciado": "Sem opções", "gabarito_idx": 0}]
        mock_ia.return_value = resposta

        self._enviar(mock_prep, mock_embed, "Quero aprender culinária")

        self.assertFalse(Trilha.objects.filter(gerada_por_ia=True).exists())

    def test_ia_indica_trilha_fora_do_catalogo_nao_gera_nada(self, _clf, mock_embed, mock_prep, mock_ia):
        mock_ia.return_value = {"resultado": "TRILHA_EXISTENTE", "trilha_existente": "Culinária Avançada", "trilha": None}

        dados = self._enviar(mock_prep, mock_embed, "Quero aprender culinária")

        self.assertFalse(Trilha.objects.filter(gerada_por_ia=True).exists())
        self.assertIn("Ainda não temos uma trilha sobre esse tema", dados["conteudo"])

    def test_pedido_sem_tema_nao_consulta_a_ia(self, _clf, mock_embed, mock_prep, mock_ia):
        self._enviar(mock_prep, mock_embed, "Qual trilha você me recomenda?")

        mock_ia.assert_not_called()

    def test_exemplos_sem_tema_da_intencao_nao_tem_tema(self, *_mocks):
        from intents.management.commands.seed_intencoes import INTENCOES_CANONICAS

        exemplos = next(i["examples"] for i in INTENCOES_CANONICAS if i["code"] == "RECOMENDAR_TRILHA")
        com_tema = {e for e in exemplos if any(t in e for t in ("programação", "culinária", "violão"))}
        for exemplo in set(exemplos) - com_tema:
            self.assertIsNone(_tema_do_pedido(exemplo), exemplo)
        self.assertEqual(_tema_do_pedido("Quero aprender culinária, por onde começo?"), "culinaria")


class BuscaPorModuloTests(APITestCase):
    """O tema da mensagem também é procurado nos títulos e descrições dos módulos."""

    def setUp(self):
        self.fundamentos = Trilha.objects.create(titulo="Python: Fundamentos", habilidade="Python", ativo=True)
        self.variaveis = Modulo.objects.create(
            trilha=self.fundamentos, titulo="Variaveis, Tipos de Dados e Operadores",
            descricao="Tipos primitivos e operadores aritmeticos.", nivel="INICIANTE", ordem_modulo=1,
        )
        self.lacos = Modulo.objects.create(
            trilha=self.fundamentos, titulo="Estruturas de Repeticao (For e While)",
            descricao="Iteracao com o laco for, break e continue.", nivel="INICIANTE", ordem_modulo=2,
        )
        self.dados = Trilha.objects.create(titulo="Python: Analise de Dados", habilidade="Ciência de Dados", ativo=True)
        self.pandas = Modulo.objects.create(
            trilha=self.dados, titulo="Manipulacao Tabular com Pandas",
            descricao="DataFrames e estatisticas descritivas.", nivel="INTERMEDIARIO", ordem_modulo=1,
        )
        self.js = Trilha.objects.create(titulo="JavaScript: Fundamentos", habilidade="JavaScript", ativo=True)
        self.js_variaveis = Modulo.objects.create(
            trilha=self.js, titulo="Variaveis, Tipos e Operadores",
            descricao="let, const e template literals.", nivel="INICIANTE", ordem_modulo=1,
        )
        self.typescript = Trilha.objects.create(titulo="TypeScript: Tipagem Estatica", habilidade="TypeScript", ativo=True)
        Modulo.objects.create(
            trilha=self.typescript, titulo="Tipos Basicos e Anotacoes",
            descricao="Anotacoes de tipo.", nivel="INICIANTE", ordem_modulo=1,
        )
        self.trilhas = [self.fundamentos, self.dados, self.js, self.typescript]

    def test_singular_reduz_plurais_regulares(self):
        self.assertEqual(_singular("variaveis"), "variavel")
        self.assertEqual(_singular("lacos"), "laco")
        self.assertEqual(_singular("funcoes"), "funcao")
        self.assertEqual(_singular("listas"), "lista")

    def test_assunto_do_modulo_identifica_trilha_sem_nome_da_trilha(self):
        trilhas, modulo = _tema_da_mensagem("Quero aprender pandas", self.trilhas)

        self.assertEqual(trilhas, [self.dados])
        self.assertEqual(modulo, self.pandas)

    def test_plural_e_acento_na_mensagem_casam_com_o_modulo(self):
        trilhas, modulo = _tema_da_mensagem("Quero estudar laços de repetição", self.trilhas)

        self.assertEqual((trilhas, modulo), ([self.fundamentos], self.lacos))

    def test_trilha_citada_desempata_modulos_de_trilhas_diferentes(self):
        trilhas, modulo = _tema_da_mensagem(
            "Quero aprender sobre variaveis em python, o nível bem básico sabe? Por onde começo?", self.trilhas,
        )

        self.assertEqual((trilhas, modulo), ([self.fundamentos], self.variaveis))

    def test_modulo_em_trilhas_diferentes_sem_trilha_citada_e_ambiguo(self):
        trilhas, modulo = _tema_da_mensagem("Quero aprender variaveis", self.trilhas)

        self.assertEqual(set(trilhas), {self.fundamentos, self.js})
        self.assertIsNone(modulo)

    def test_palavras_de_nivel_nao_identificam_modulos(self):
        self.assertEqual(identificar_modulos_no_texto("Quero o nível bem básico", self.trilhas), [])

    def test_texto_sem_tema_remove_trilha_e_assunto_do_modulo(self):
        self.assertEqual(
            texto_sem_tema("Quero aprender variaveis em python, por onde começo?", self.trilhas),
            "quero aprender em por onde comeco",
        )
        self.assertIsNone(texto_sem_tema("Quero aprender python", self.trilhas))


@patch("assistantManagement.services.TextPreprocessor.get_instance")
@patch("assistantManagement.services.EmbeddingService.get_instance")
@patch("assistantManagement.services.IntentClassifier.classificar")
class RecomendacaoPorModuloChatTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            apelido="aluno_modulo", nome="Caio", email="aluno_modulo@example.com", password="password123",
        )
        self.client.force_authenticate(user=self.user)
        for code in ("RECOMENDAR_TRILHA", "INICIAR_DO_ZERO", "DUVIDA_CONTEUDO"):
            Intention.objects.create(code=code, system_action=code, description=code)
        self.trilha = Trilha.objects.create(titulo="Python: Fundamentos", habilidade="Python", ativo=True)
        Modulo.objects.create(
            trilha=self.trilha, titulo="Variaveis e Operadores", nivel="INICIANTE", ordem_modulo=1,
        )
        self.lacos = Modulo.objects.create(
            trilha=self.trilha, titulo="Estruturas de Repeticao", descricao="Laco for e while.",
            nivel="INICIANTE", ordem_modulo=2,
        )
        self.sessao = Sessao.objects.create(usuario=self.user)

    def _enviar(self, mock_prep_inst, mock_embed_inst, texto):
        mock_prep_inst.return_value.processar.side_effect = lambda t: t
        mock_embed_inst.return_value.gerar_embedding.return_value = [0.1] * 384
        response = self.client.post(
            f"/api/chat/sessao/{self.sessao.id}/mensagem/", {"conteudo": texto}, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data["resposta_assistente"]

    @staticmethod
    def _classificacao(intencao, similaridade):
        return {"intencao": intencao, "similaridade": similaridade, "resposta_texto": ""}

    def test_pedido_sem_o_assunto_vira_recomendacao_do_modulo(self, mock_clf, mock_embed, mock_prep):
        mock_clf.side_effect = [
            self._classificacao("INICIAR_DO_ZERO", 0.80),
            self._classificacao("RECOMENDAR_TRILHA", 0.90),
        ]

        dados = self._enviar(mock_prep, mock_embed, "Quero aprender laços em python, bem do básico. Por onde começo?")

        self.assertEqual(dados["intencao_detectada"], "RECOMENDAR_TRILHA")
        self.assertEqual(dados["dados_acao"]["modulo_id"], str(self.lacos.id))
        self.assertIn("módulo 2, **Estruturas de Repeticao**", dados["conteudo"])
        self.assertIn("comece pelo módulo 1, **Variaveis e Operadores**", dados["conteudo"])
        self.assertFalse(Matricula.objects.filter(usuario=self.user).exists())
        # Segunda classificação usou a mensagem sem a trilha e sem o assunto do módulo.
        textos = [c.args[0] for c in mock_embed.return_value.gerar_embedding.call_args_list]
        self.assertEqual(textos[-1], "quero aprender em bem do basico por onde comeco")

    def test_segunda_classificacao_menos_confiavel_e_descartada(self, mock_clf, mock_embed, mock_prep):
        mock_clf.side_effect = [
            self._classificacao("INICIAR_DO_ZERO", 0.95),
            self._classificacao("RECOMENDAR_TRILHA", 0.80),
        ]

        dados = self._enviar(mock_prep, mock_embed, "Quero começar do zero em laços")

        self.assertEqual(dados["intencao_detectada"], "INICIAR_DO_ZERO")

    def test_duvida_de_conteudo_nao_e_reclassificada(self, mock_clf, mock_embed, mock_prep):
        mock_clf.return_value = self._classificacao("DUVIDA_CONTEUDO", 0.75)

        with patch("assistantManagement.services.BaseConhecimento.buscar") as mock_base:
            mock_base.return_value = MagicMock(resposta=None, relacionadas=[])
            dados = self._enviar(mock_prep, mock_embed, "Como funciona o laço for?")

        self.assertEqual(dados["intencao_detectada"], "DUVIDA_CONTEUDO")
        self.assertEqual(mock_clf.call_count, 1)

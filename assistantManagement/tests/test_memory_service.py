from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from activityManagement.models import Atividade, ExecucaoAtividade, RespostaQuestao
from questionsManagement.models import Questao
from trackManagement.models import Modulo, Trilha
from assistantManagement.models import MemoriaPedagogicaUsuario
from assistantManagement.memory_service import (
    PedagogicalMemoryService,
    LIMIAR_DOMINIO_PERCENT,
    LIMIAR_DIFICULDADE_PERCENT,
    MIN_QUESTOES_PARA_PONTO_FORTE,
    JANELA_RETENTATIVA,
)

pytestmark = [pytest.mark.integration, pytest.mark.django_db]

User = get_user_model()


@pytest.fixture
def usuario(db):
    return User.objects.create_user(
        apelido="alunomemoria",
        email="aluno_memoria@teste.com",
        password="hash_teste",
        nome="Aluno Memória",
    )


@pytest.fixture
def trilha(db):
    return Trilha.objects.create(
        titulo="Trilha Teste Memória",
        habilidade="Python",
    )


@pytest.fixture
def modulo_condicionais(db, trilha):
    return Modulo.objects.create(
        trilha=trilha,
        titulo="Estruturas Condicionais",
        nivel="BASICO",
        ordem_modulo=1,
    )


@pytest.fixture
def modulo_repeticao(db, trilha):
    return Modulo.objects.create(
        trilha=trilha,
        titulo="Estruturas de Repetição",
        nivel="BASICO",
        ordem_modulo=2,
    )


@pytest.fixture
def atividade_condicionais(db, modulo_condicionais):
    return Atividade.objects.create(
        modulo=modulo_condicionais,
        titulo="Exercícios If/Else",
        contexto_avaliacao="FORMATIVA",
        ordem=1,
    )


@pytest.fixture
def atividade_repeticao(db, modulo_repeticao):
    return Atividade.objects.create(
        modulo=modulo_repeticao,
        titulo="Exercícios For/While",
        contexto_avaliacao="FORMATIVA",
        ordem=2,
    )


@pytest.mark.django_db
def test_estudante_sem_atividades_gera_memoria_vazia(usuario):
    memoria = PedagogicalMemoryService.consolidar_perfil(usuario)
    
    assert memoria.total_atividades_avaliadas == 0
    assert memoria.taxa_acerto_geral == 0.0
    assert memoria.pontos_fortes == []
    assert memoria.topicos_dificuldade == []
    assert "ainda não realizou" in memoria.resumo_perfil_didatico


@pytest.mark.django_db
def test_classifica_modulo_com_dominio_como_ponto_forte(
    usuario, modulo_condicionais, atividade_condicionais
):
    # Criar 3 questões no módulo de condicionais (atendendo ao mínimo de 3 questões para Ponto Forte)
    q1 = Questao.objects.create(
        atividade=atividade_condicionais,
        tipo_exercicio="MULTIPLA_ESCOLHA",
        enunciado="Questão 1",
        gabarito_esperado="A",
        ordem_questao=1,
    )
    q2 = Questao.objects.create(
        atividade=atividade_condicionais,
        tipo_exercicio="MULTIPLA_ESCOLHA",
        enunciado="Questão 2",
        gabarito_esperado="B",
        ordem_questao=2,
    )
    q3 = Questao.objects.create(
        atividade=atividade_condicionais,
        tipo_exercicio="MULTIPLA_ESCOLHA",
        enunciado="Questão 3",
        gabarito_esperado="C",
        ordem_questao=3,
    )

    execucao = ExecucaoAtividade.objects.create(
        usuario=usuario,
        atividade=atividade_condicionais,
        resposta={},
        pontuacao_obtida=100,
        aprovado=True,
    )

    # 100% de acertos (>= 80% e total >= 3)
    RespostaQuestao.objects.create(execucao=execucao, questao=q1, correta=True)
    RespostaQuestao.objects.create(execucao=execucao, questao=q2, correta=True)
    RespostaQuestao.objects.create(execucao=execucao, questao=q3, correta=True)

    memoria = PedagogicalMemoryService.consolidar_perfil(usuario)

    assert memoria.total_atividades_avaliadas == 1
    assert memoria.taxa_acerto_geral == 100.0
    assert "Estruturas Condicionais" in memoria.pontos_fortes
    assert memoria.topicos_dificuldade == []


@pytest.mark.django_db
def test_classifica_modulo_com_baixo_aproveitamento_como_dificuldade(
    usuario, modulo_repeticao, atividade_repeticao
):
    q1 = Questao.objects.create(
        atividade=atividade_repeticao,
        tipo_exercicio="MULTIPLA_ESCOLHA",
        enunciado="Questão Loop 1",
        gabarito_esperado="A",
        ordem_questao=1,
    )
    q2 = Questao.objects.create(
        atividade=atividade_repeticao,
        tipo_exercicio="MULTIPLA_ESCOLHA",
        enunciado="Questão Loop 2",
        gabarito_esperado="B",
        ordem_questao=2,
    )

    execucao = ExecucaoAtividade.objects.create(
        usuario=usuario,
        atividade=atividade_repeticao,
        resposta={},
        pontuacao_obtida=0,
        aprovado=False,
    )

    # 0% de acertos (< 60%)
    RespostaQuestao.objects.create(execucao=execucao, questao=q1, correta=False)
    RespostaQuestao.objects.create(execucao=execucao, questao=q2, correta=False)

    memoria = PedagogicalMemoryService.consolidar_perfil(usuario)

    assert memoria.total_atividades_avaliadas == 1
    assert memoria.taxa_acerto_geral == 0.0
    assert "Estruturas de Repetição" in memoria.topicos_dificuldade
    assert memoria.pontos_fortes == []


@pytest.mark.django_db
def test_considera_apenas_a_primeira_execucao_de_cada_atividade(
    usuario, modulo_repeticao, atividade_repeticao
):
    q1 = Questao.objects.create(
        atividade=atividade_repeticao,
        tipo_exercicio="MULTIPLA_ESCOLHA",
        enunciado="Questão 1",
        gabarito_esperado="A",
        ordem_questao=1,
    )
    q2 = Questao.objects.create(
        atividade=atividade_repeticao,
        tipo_exercicio="MULTIPLA_ESCOLHA",
        enunciado="Questão 2",
        gabarito_esperado="B",
        ordem_questao=2,
    )
    q3 = Questao.objects.create(
        atividade=atividade_repeticao,
        tipo_exercicio="MULTIPLA_ESCOLHA",
        enunciado="Questão 3",
        gabarito_esperado="C",
        ordem_questao=3,
    )

    # 1ª execução com erro
    exec1 = ExecucaoAtividade.objects.create(
        usuario=usuario,
        atividade=atividade_repeticao,
        resposta={},
        pontuacao_obtida=0,
        aprovado=False,
    )
    RespostaQuestao.objects.create(execucao=exec1, questao=q1, correta=False)
    RespostaQuestao.objects.create(execucao=exec1, questao=q2, correta=False)
    RespostaQuestao.objects.create(execucao=exec1, questao=q3, correta=False)

    # 2ª execução (retentativa) com acerto
    exec2 = ExecucaoAtividade.objects.create(
        usuario=usuario,
        atividade=atividade_repeticao,
        resposta={},
        pontuacao_obtida=100,
        aprovado=True,
    )
    RespostaQuestao.objects.create(execucao=exec2, questao=q1, correta=True)
    RespostaQuestao.objects.create(execucao=exec2, questao=q2, correta=True)
    RespostaQuestao.objects.create(execucao=exec2, questao=q3, correta=True)
    ExecucaoAtividade.objects.filter(pk=exec2.pk).update(
        executado_em=exec1.executado_em + timedelta(hours=1)
    )

    memoria = PedagogicalMemoryService.consolidar_perfil(usuario)

    # Deve refletir a 1ª execução: a retentativa não apaga os erros (0% -> Dificuldade)
    assert memoria.total_atividades_avaliadas == 1
    assert memoria.taxa_acerto_geral == 0.0
    assert "Estruturas de Repetição" in memoria.topicos_dificuldade
    assert memoria.pontos_fortes == []

    # Voltar à atividade depois da janela de retentativa abre uma nova rodada, que passa a valer
    ExecucaoAtividade.objects.filter(pk=exec2.pk).update(
        executado_em=exec1.executado_em + JANELA_RETENTATIVA + timedelta(minutes=1)
    )

    memoria = PedagogicalMemoryService.consolidar_perfil(usuario)

    assert memoria.taxa_acerto_geral == 100.0
    assert "Estruturas de Repetição" in memoria.pontos_fortes
    assert memoria.topicos_dificuldade == []
    assert memoria.topicos_praticar == []


@pytest.mark.django_db
def test_topicos_praticar_aponta_a_atividade_com_menor_acerto_do_modulo(
    usuario, trilha, modulo_repeticao, atividade_repeticao
):
    atividade_pior = Atividade.objects.create(
        modulo=modulo_repeticao,
        titulo="Exercícios While",
        contexto_avaliacao="FORMATIVA",
        ordem=3,
    )
    for atividade, acertos in ((atividade_repeticao, [True, False]), (atividade_pior, [False, False])):
        execucao = ExecucaoAtividade.objects.create(
            usuario=usuario, atividade=atividade, resposta={}, pontuacao_obtida=0, aprovado=False,
        )
        for ordem, correta in enumerate(acertos, start=1):
            questao = Questao.objects.create(
                atividade=atividade,
                tipo_exercicio="MULTIPLA_ESCOLHA",
                enunciado=f"Questão {ordem}",
                gabarito_esperado="A",
                ordem_questao=ordem,
            )
            RespostaQuestao.objects.create(execucao=execucao, questao=questao, correta=correta)

    memoria = PedagogicalMemoryService.consolidar_perfil(usuario)

    assert memoria.topicos_dificuldade == ["Estruturas de Repetição"]
    assert memoria.topicos_praticar == [{
        "topico": "Estruturas de Repetição",
        "trilha_id": str(trilha.id),
        "atividade_id": str(atividade_pior.id),
    }]


@pytest.mark.django_db
def test_ignora_atividades_sem_questoes_no_total_avaliadas(
    usuario, modulo_condicionais, atividade_condicionais
):
    """Atividades de leitura ou conteúdo teórico sem questões não devem contar como avaliadas."""
    # Execução de atividade sem nenhuma RespostaQuestao criada
    ExecucaoAtividade.objects.create(
        usuario=usuario,
        atividade=atividade_condicionais,
        resposta={},
        pontuacao_obtida=0,
        aprovado=True,
    )

    memoria = PedagogicalMemoryService.consolidar_perfil(usuario)
    assert memoria.total_atividades_avaliadas == 0
    assert memoria.taxa_acerto_geral == 0.0
    assert memoria.pontos_fortes == []
    assert memoria.topicos_dificuldade == []


@pytest.mark.django_db
def test_idempotencia_da_consolidacao(usuario, modulo_condicionais, atividade_condicionais):
    q1 = Questao.objects.create(
        atividade=atividade_condicionais,
        tipo_exercicio="MULTIPLA_ESCOLHA",
        enunciado="Questão Única",
        gabarito_esperado="A",
        ordem_questao=1,
    )
    execucao = ExecucaoAtividade.objects.create(
        usuario=usuario,
        atividade=atividade_condicionais,
        resposta={},
        pontuacao_obtida=100,
        aprovado=True,
    )
    RespostaQuestao.objects.create(execucao=execucao, questao=q1, correta=True)

    memoria1 = PedagogicalMemoryService.consolidar_perfil(usuario)
    memoria2 = PedagogicalMemoryService.consolidar_perfil(usuario)

    assert memoria1.id == memoria2.id
    assert MemoriaPedagogicaUsuario.objects.filter(usuario=usuario).count() == 1

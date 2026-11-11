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
)

User = get_user_model()


@pytest.fixture
def usuario(db):
    return User.objects.create_user(
        email="aluno_memoria@teste.com",
        senha_hash="hash_teste",
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
        ordem_atividade=1,
    )


@pytest.fixture
def atividade_repeticao(db, modulo_repeticao):
    return Atividade.objects.create(
        modulo=modulo_repeticao,
        titulo="Exercícios For/While",
        ordem_atividade=2,
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
    # Criar 2 questões no módulo de condicionais
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

    execucao = ExecucaoAtividade.objects.create(
        usuario=usuario,
        atividade=atividade_condicionais,
        nota_obtida=100.0,
        xp_ganho=50,
    )

    # 100% de acertos (>= 80%)
    RespostaQuestao.objects.create(execucao=execucao, questao=q1, correta=True)
    RespostaQuestao.objects.create(execucao=execucao, questao=q2, correta=True)

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
        nota_obtida=0.0,
        xp_ganho=0,
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
def test_considera_apenas_a_ultima_execucao_de_cada_atividade(
    usuario, modulo_repeticao, atividade_repeticao
):
    q1 = Questao.objects.create(
        atividade=atividade_repeticao,
        tipo_exercicio="MULTIPLA_ESCOLHA",
        enunciado="Questão 1",
        gabarito_esperado="A",
        ordem_questao=1,
    )

    # 1ª execução com erro
    exec1 = ExecucaoAtividade.objects.create(
        usuario=usuario,
        atividade=atividade_repeticao,
        nota_obtida=0.0,
        xp_ganho=0,
    )
    RespostaQuestao.objects.create(execucao=exec1, questao=q1, correta=False)

    # 2ª execução (mais recente) com acerto
    exec2 = ExecucaoAtividade.objects.create(
        usuario=usuario,
        atividade=atividade_repeticao,
        nota_obtida=100.0,
        xp_ganho=20,
    )
    RespostaQuestao.objects.create(execucao=exec2, questao=q1, correta=True)

    memoria = PedagogicalMemoryService.consolidar_perfil(usuario)

    # Deve refletir a 2ª execução (100% de acerto -> Ponto Forte)
    assert memoria.total_atividades_avaliadas == 1
    assert memoria.taxa_acerto_geral == 100.0
    assert "Estruturas de Repetição" in memoria.pontos_fortes
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
        nota_obtida=100.0,
        xp_ganho=10,
    )
    RespostaQuestao.objects.create(execucao=execucao, questao=q1, correta=True)

    memoria1 = PedagogicalMemoryService.consolidar_perfil(usuario)
    memoria2 = PedagogicalMemoryService.consolidar_perfil(usuario)

    assert memoria1.id == memoria2.id
    assert MemoriaPedagogicaUsuario.objects.filter(usuario=usuario).count() == 1

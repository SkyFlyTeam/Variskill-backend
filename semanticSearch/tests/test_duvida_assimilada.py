import pytest
from django.db import connection
from model_bakery import baker

from activityManagement.models import Atividade
from semanticSearch.models import DuvidaAssimilada
from trackManagement.models import Modulo

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def test_tabela_usa_o_nome_especificado_na_task():
    assert DuvidaAssimilada._meta.db_table == 'DUVIDA_ASSIMILADA'


def test_cria_duvida_assimilada_com_valores_default():
    duvida = baker.make(DuvidaAssimilada, embedding=[0.1] * 768)
    duvida.refresh_from_db()

    assert duvida.contador_utilizacoes == 1
    assert duvida.feedbacks_positivos == 0
    assert duvida.feedbacks_negativos == 0
    assert duvida.criado_em is not None
    assert duvida.atualizado_em is not None


def test_armazena_e_retorna_embedding_com_768_dimensoes():
    embedding = [0.2] * 768
    duvida = baker.make(DuvidaAssimilada, embedding=embedding)
    duvida.refresh_from_db()

    assert len(duvida.embedding) == 768
    assert list(duvida.embedding) == pytest.approx(embedding)


def test_atividade_e_modulo_sao_opcionais():
    duvida = baker.make(DuvidaAssimilada, atividade=None, modulo=None, embedding=[0.0] * 768)
    duvida.refresh_from_db()

    assert duvida.atividade is None
    assert duvida.modulo is None


def test_related_names_de_atividade_e_modulo():
    atividade = baker.make(Atividade)
    modulo = baker.make(Modulo)
    duvida = baker.make(
        DuvidaAssimilada, atividade=atividade, modulo=modulo, embedding=[0.0] * 768
    )

    assert duvida in atividade.duvidas_assimiladas.all()
    assert duvida in modulo.duvidas_assimiladas.all()


def test_exclusao_da_atividade_apaga_duvida_assimilada_em_cascata():
    atividade = baker.make(Atividade)
    duvida = baker.make(DuvidaAssimilada, atividade=atividade, embedding=[0.0] * 768)

    atividade.delete()

    assert not DuvidaAssimilada.objects.filter(pk=duvida.pk).exists()


def test_exclusao_do_modulo_apaga_duvida_assimilada_em_cascata():
    modulo = baker.make(Modulo)
    duvida = baker.make(DuvidaAssimilada, modulo=modulo, embedding=[0.0] * 768)

    modulo.delete()

    assert not DuvidaAssimilada.objects.filter(pk=duvida.pk).exists()


def test_hnsw_index_existe_na_coluna_embedding():
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT indexdef FROM pg_indexes WHERE tablename = 'DUVIDA_ASSIMILADA' "
            "AND indexname = 'duvida_assimilada_embed_hnsw'",
        )
        row = cursor.fetchone()

    assert row is not None
    assert 'hnsw' in row[0].lower()
    assert 'vector_cosine_ops' in row[0]

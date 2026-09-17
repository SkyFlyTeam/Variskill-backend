import pytest
from django.db import IntegrityError
from django.db import connection
from model_bakery import baker

from intents.models import Intention, IntentionExample, Response


pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def test_intention_code_must_be_unique():
    baker.make(Intention, code='SAUDACAO')

    with pytest.raises(IntegrityError):
        baker.make(Intention, code='SAUDACAO')


def test_intention_example_stores_and_returns_embedding_vector():
    intention = baker.make(Intention)
    embedding = [0.1] * 384

    example = baker.make(IntentionExample, intention=intention, embedding=embedding)
    example.refresh_from_db()

    assert len(example.embedding) == 384
    assert list(example.embedding) == pytest.approx(embedding)


def test_intention_example_related_name():
    intention = baker.make(Intention)
    example = baker.make(IntentionExample, intention=intention, embedding=[0.0] * 384)

    assert example in intention.examples.all()


def test_response_related_name():
    intention = baker.make(Intention)
    response = baker.make(Response, intention=intention)

    assert response in intention.responses.all()


def test_tables_use_the_names_specified_in_the_task():
    assert Intention._meta.db_table == 'INTENCAO'
    assert IntentionExample._meta.db_table == 'EXEMPLO_INTENCAO'
    assert Response._meta.db_table == 'RESPOSTA'


def test_vector_extension_is_enabled():
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
        assert cursor.fetchone() is not None


def test_hnsw_index_exists_on_embedding_column():
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT indexdef FROM pg_indexes WHERE tablename = 'EXEMPLO_INTENCAO' "
            "AND indexname = 'exemplo_intencao_embedding_hnsw'",
        )
        row = cursor.fetchone()

    assert row is not None
    assert 'hnsw' in row[0].lower()
    assert 'vector_cosine_ops' in row[0]

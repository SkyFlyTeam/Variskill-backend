import pytest

from semanticSearch.service.text_embedding_service import TextEmbeddingService


class FakePreprocessor:
    def __init__(self):
        self.received = None

    def processar(self, texto):
        self.received = texto
        return "texto processado"


class FakeEmbeddingService:
    def __init__(self):
        self.received = None

    def gerar_embedding(self, texto):
        self.received = texto
        return [0.25, 0.75]


@pytest.mark.unit
def test_gerar_embedding_executa_preprocessador_antes_do_embedding():
    preprocessor = FakePreprocessor()
    embedding = FakeEmbeddingService()
    service = TextEmbeddingService(preprocessor, embedding)

    result = service.gerar_embedding("texto original")

    assert result == [0.25, 0.75]
    assert preprocessor.received == "texto original"
    assert embedding.received == "texto processado"

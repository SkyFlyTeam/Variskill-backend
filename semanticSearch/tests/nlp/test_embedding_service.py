import pytest

from semanticSearch.service.nlp import embedding_service


class FakeModel:
    calls = 0

    def __init__(self, name):
        self.name = name
        type(self).calls += 1

    def encode(self, text, normalize_embeddings):
        assert text == "texto processado"
        assert normalize_embeddings is True
        return [1.0 / (384 ** 0.5)] * 384


@pytest.mark.unit
def test_embedding_service_is_singleton_and_returns_384_normalized_values(monkeypatch):
    monkeypatch.setattr(embedding_service, "SentenceTransformer", FakeModel)
    embedding_service.EmbeddingService._instance = None
    FakeModel.calls = 0

    first = embedding_service.EmbeddingService.get_instance()
    second = embedding_service.EmbeddingService.get_instance()
    vector = first.gerar_embedding("texto processado")

    assert first is second
    assert FakeModel.calls == 1
    assert len(vector) == 384
    assert sum(value * value for value in vector) == pytest.approx(1.0)

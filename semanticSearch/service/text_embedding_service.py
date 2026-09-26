"""Service that connects text preprocessing to embedding generation."""

from __future__ import annotations

from semanticSearch.service.nlp.embedding_service import EmbeddingService
from semanticSearch.service.nlp.preprocessor import TextPreprocessor
from semanticSearch.service.nlp.intent_classifier import IntentClassifier


class TextEmbeddingService:
    """Preprocess raw student text and generate its embedding."""

    def __init__(
        self,
        preprocessor: TextPreprocessor | None = None,
        embedding_service: EmbeddingService | None = None,
        intent_classifier: IntentClassifier | None = None,
    ) -> None:
        self.preprocessor = preprocessor or TextPreprocessor.get_instance()
        self.embedding_service = embedding_service or EmbeddingService.get_instance()
        self.intent_classifier = intent_classifier or IntentClassifier()

    def gerar_embedding(self, texto: str | None) -> list[float]:
        """Return the embedding generated from the preprocessed text."""
        texto_processado = self.preprocessor.processar(texto)
        return self.embedding_service.gerar_embedding(texto_processado)

    def classificar_intencao(self, texto: str | None, contexto: dict | None = None) -> dict:
        """Return the closest intent for a raw user message."""
        vetor = self.gerar_embedding(texto)
        return self.intent_classifier.classificar(vetor, contexto=contexto)

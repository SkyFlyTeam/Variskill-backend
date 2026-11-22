"""Pipeline único de vetorização de dúvidas do estudante.

Busca (apostila e caderno) e ingestão (caderno) precisam gerar o vetor da mesma forma; caso
contrário, a mesma pergunta produz vetores diferentes e a similaridade cai abaixo do limiar.
Pipeline: higieniza (LGPD) -> pré-processa (lematização/stopwords) -> gera embedding.
"""

from __future__ import annotations

from semanticSearch.service.nlp.embedding_service import EmbeddingService
from semanticSearch.service.nlp.preprocessor import TextPreprocessor
from semanticSearch.service.sanitizer import TextSanitizer


def normalizar_duvida(texto: str | None, preprocessor: TextPreprocessor | None = None) -> str:
    """Texto higienizado e pré-processado que alimenta o embedding da dúvida."""
    if not texto or not isinstance(texto, str):
        return ""
    preprocessor = preprocessor or TextPreprocessor.get_instance()
    texto_limpo = TextSanitizer.sanitizar(texto, remover_saudacao=True) or texto
    return preprocessor.processar(texto_limpo) or texto_limpo


def vetorizar_duvida(
    texto: str | None,
    preprocessor: TextPreprocessor | None = None,
    embedding_service: EmbeddingService | None = None,
) -> tuple[str, list[float]]:
    """Retorna (texto_normalizado, vetor) da dúvida."""
    texto_normalizado = normalizar_duvida(texto, preprocessor)
    embedding_service = embedding_service or EmbeddingService.get_instance()
    return texto_normalizado, embedding_service.gerar_embedding(texto_normalizado)

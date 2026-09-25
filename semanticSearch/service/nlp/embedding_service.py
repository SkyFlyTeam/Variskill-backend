from __future__ import annotations

import threading
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    _instance = None
    _lock = threading.Lock()
    MODEL_NAME = "all-MiniLM-L6-v2"
    DIMENSIONS = 384

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.model = SentenceTransformer(self.MODEL_NAME)

    def gerar_embedding(self, texto: str) -> list[float]:
        if not isinstance(texto, str):
            raise TypeError("texto deve ser uma string")
        vetor = self.model.encode(texto, normalize_embeddings=True)
        if hasattr(vetor, "tolist"):
            vetor = vetor.tolist()
        if len(vetor) != self.DIMENSIONS:
            raise ValueError(f"O modelo retornou {len(vetor)} dimensões; esperado {self.DIMENSIONS}")
        return [float(valor) for valor in vetor]

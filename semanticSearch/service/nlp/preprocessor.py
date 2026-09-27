"""Pre-processing linguístico das mensagens recebidas do estudante."""

from __future__ import annotations

import threading
import unicodedata

import spacy
from nltk.corpus import stopwords

PALAVRAS_PRESERVADAS = {"nao", "como", "onde", "qual", "quais", "oque", "quando", "porque", "ajuda", "quero", "preciso", "sim"}


class TextPreprocessor:
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        self.nlp = spacy.load("pt_core_news_sm", disable=["parser", "ner"])
        self.stopwords_pt = set(stopwords.words("portuguese")) - PALAVRAS_PRESERVADAS

    def processar(self, texto: str | None) -> str:
        if not texto or not isinstance(texto, str):
            return ""
        tokens = self._tokenizar(texto)
        tokens = self._normalizar(tokens)
        tokens = self._remover_stopwords(tokens)
        tokens = self._lematizar(tokens)
        return " ".join(tokens)

    def _tokenizar(self, texto: str) -> list:
        return list(self.nlp(texto))

    @staticmethod
    def _sem_acentos(texto: str) -> str:
        decomposed = unicodedata.normalize("NFKD", texto)
        return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")

    def _normalizar(self, tokens: list) -> list[str]:
        normalizados = []
        for token in tokens:
            if token.is_punct or token.is_space or token.is_digit:
                continue
            valor = self._sem_acentos(token.lower_)
            if valor:
                normalizados.append(valor)
        return normalizados

    def _remover_stopwords(self, tokens: list[str]) -> list[str]:
        return [token for token in tokens if token not in self.stopwords_pt]

    def _lematizar(self, tokens: list[str]) -> list[str]:
        return [token.lemma_ for token in self.nlp(" ".join(tokens)) if not token.is_space]

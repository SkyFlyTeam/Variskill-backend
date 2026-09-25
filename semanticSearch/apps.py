from django.apps import AppConfig


class SemanticsearchConfig(AppConfig):
    name = 'semanticSearch'

    def ready(self):
        from .service.nlp.embedding_service import EmbeddingService
        EmbeddingService.get_instance()

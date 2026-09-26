import math
from django.core.management.base import BaseCommand
from intents.models import Intention, IntentionExample, Response

INTENCOES_CANONICAS = [
    {
        "code": "INICIAR_DIAGNOSTICO",
        "system_action": "DISPARAR_TESTE_DIAGNOSTICO",
        "description": "Estudante opta por realizar o teste de nivelamento/diagnóstico inicial.",
        "examples": [
            "já sei programar, quero testar meu nível",
            "fazer o teste de nivelamento",
            "quero provar que sou intermediário",
            "quero fazer a avaliação diagnóstica",
            "prefiro fazer o teste diagnóstico"
        ],
        "responses": [
            "Excelente desafio! Vamos realizar uma avaliação rápida para calibrar seu nível."
        ]
    }
]


def _get_embedding(text: str):
    try:
        from semanticSearch.service.nlp.embedding_service import EmbeddingService
        service = EmbeddingService.get_instance()
        return service.gerar_embedding(text)
    except Exception:
        # Fallback: gerar vetor não-nulo com norma 1 (unitario) baseado em hash para HNSW cosine distance
        h = hash(text)
        vec = [(math.sin(h + i) + 1.0) / 2.0 for i in range(384)]
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]


class Command(BaseCommand):
    help = "Cadastra a intenção INICIAR_DIAGNOSTICO e intenções canônicas no banco de dados."

    def handle(self, *args, **options):
        self.stdout.write("Iniciando seed de intenções...")

        for item in INTENCOES_CANONICAS:
            intention, created = Intention.objects.get_or_create(
                code=item["code"],
                defaults={
                    "system_action": item["system_action"],
                    "description": item["description"],
                },
            )
            if not created:
                intention.system_action = item["system_action"]
                intention.description = item["description"]
                intention.save(update_fields=["system_action", "description"])

            for text in item["examples"]:
                embedding = _get_embedding(text)
                example, ex_created = IntentionExample.objects.get_or_create(
                    intention=intention,
                    text=text,
                    defaults={"embedding": embedding},
                )
                if not ex_created:
                    example.embedding = embedding
                    example.save(update_fields=["embedding"])

            for resp_text in item["responses"]:
                Response.objects.get_or_create(
                    intention=intention,
                    text=resp_text,
                )

            self.stdout.write(self.style.SUCCESS(f"Intenção '{item['code']}' cadastrada com sucesso!"))

        self.stdout.write(self.style.SUCCESS("Seed de intenções concluído com sucesso."))



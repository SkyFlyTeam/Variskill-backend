import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from semanticSearch.models import EntradaCorpus, PerguntaCorpus
from semanticSearch.service.text_embedding_service import TextEmbeddingService

CORPUS_DIR = Path(__file__).resolve().parents[2] / "corpus"
CAMPOS_OBRIGATORIOS = ("topico", "pergunta", "resposta")


class Command(BaseCommand):
    help = (
        "Recria a base de conhecimento do Coach a partir de todos os arquivos JSON de semanticSearch/corpus/ "
        "(incluindo subpastas). Todas as entradas do corpus no banco são apagadas e cadastradas novamente."
    )

    def handle(self, *args, **options):
        itens = self._ler_corpus()

        # Embeddings são gerados antes de tocar no banco: se o modelo falhar, o corpus atual continua intacto.
        self.stdout.write(f"Gerando embeddings de {len(itens)} entradas...")
        embedding_service = TextEmbeddingService()
        perguntas_por_item = [
            [(texto, embedding_service.gerar_embedding(texto)) for texto in [item["pergunta"], *item.get("variacoes", [])]]
            for item in itens
        ]

        # Apagar e recriar na mesma transação: quem consulta o corpus durante o seed continua vendo a versão antiga.
        with transaction.atomic():
            removidas, _ = EntradaCorpus.objects.all().delete()
            entradas = EntradaCorpus.objects.bulk_create([
                EntradaCorpus(topico=item["topico"], pergunta=item["pergunta"], resposta=item["resposta"])
                for item in itens
            ])
            PerguntaCorpus.objects.bulk_create([
                PerguntaCorpus(entrada=entrada, texto=texto, embedding=embedding)
                for entrada, perguntas in zip(entradas, perguntas_por_item)
                for texto, embedding in perguntas
            ])

        total_perguntas = sum(len(perguntas) for perguntas in perguntas_por_item)
        self.stdout.write(self.style.SUCCESS(
            f"Corpus recriado: {len(entradas)} entradas e {total_perguntas} formulações "
            f"({removidas} registros antigos apagados)."
        ))

    def _ler_corpus(self) -> list[dict]:
        arquivos = sorted(CORPUS_DIR.rglob("*.json"))
        if not arquivos:
            raise CommandError(f"Nenhum arquivo .json encontrado em {CORPUS_DIR}.")

        itens, origem_por_pergunta, erros = [], {}, []
        for arquivo in arquivos:
            nome = arquivo.relative_to(CORPUS_DIR)
            try:
                conteudo = json.loads(arquivo.read_text(encoding="utf-8"))
            except json.JSONDecodeError as erro:
                erros.append(f"{nome}: JSON inválido ({erro})")
                continue
            if not isinstance(conteudo, list):
                erros.append(f"{nome}: o arquivo deve conter uma lista de entradas")
                continue

            self.stdout.write(f"Lendo {nome} ({len(conteudo)} entradas)...")
            for indice, item in enumerate(conteudo):
                faltando = [campo for campo in CAMPOS_OBRIGATORIOS if not str(item.get(campo, "")).strip()]
                if faltando:
                    erros.append(f"{nome} [{indice}]: campos obrigatórios ausentes: {', '.join(faltando)}")
                    continue
                if item["pergunta"] in origem_por_pergunta:
                    erros.append(
                        f"{nome} [{indice}]: pergunta duplicada \"{item['pergunta']}\" "
                        f"(já definida em {origem_por_pergunta[item['pergunta']]})"
                    )
                    continue
                origem_por_pergunta[item["pergunta"]] = nome
                itens.append(item)

        # Com qualquer erro, nada é apagado: melhor manter o corpus antigo do que publicar um corpus incompleto.
        if erros:
            raise CommandError("Corpus inválido, nada foi alterado no banco:\n- " + "\n- ".join(erros))
        return itens

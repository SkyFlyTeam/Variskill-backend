import json

import pytest
from django.core.management import CommandError, call_command

from semanticSearch.management.commands.seed_corpus import CORPUS_DIR
from semanticSearch.models import EntradaCorpus, PerguntaCorpus
from semanticSearch.service.corpus_search import CorpusSearch

DIM = 384


def _vetor(indice: int) -> list[float]:
    """Vetor unitário no eixo `indice`: vetores de eixos diferentes têm similaridade 0."""
    vetor = [0.0] * DIM
    vetor[indice] = 1.0
    return vetor


def _entrada(pergunta: str, indice: int, ativo: bool = True) -> EntradaCorpus:
    entrada = EntradaCorpus.objects.create(topico="Teste", pergunta=pergunta, resposta=f"Resposta: {pergunta}", ativo=ativo)
    PerguntaCorpus.objects.create(entrada=entrada, texto=pergunta, embedding=_vetor(indice))
    return entrada


@pytest.mark.django_db
def test_buscar_retorna_entrada_acima_do_limiar():
    variavel = _entrada("Como definir uma variável?", 0)
    _entrada("O que é uma lista?", 1)

    resultado = CorpusSearch().buscar(_vetor(0))

    assert resultado.entrada == variavel
    assert resultado.similaridade == pytest.approx(1.0)


@pytest.mark.django_db
def test_buscar_abaixo_do_limiar_sugere_relacionadas():
    variavel = _entrada("Como definir uma variável?", 0)
    consulta = [0.0] * DIM
    consulta[0], consulta[1] = 0.7, 0.714  # similaridade ~0.70 com o eixo 0

    resultado = CorpusSearch(similarity_threshold=0.8, related_threshold=0.6).buscar(consulta)

    assert resultado.entrada is None
    assert resultado.relacionadas == [variavel]


@pytest.mark.django_db
def test_buscar_ignora_entradas_inativas():
    _entrada("Entrada desativada", 0, ativo=False)

    resultado = CorpusSearch().buscar(_vetor(0))

    assert resultado.entrada is None
    assert resultado.relacionadas == []


def test_corpus_json_tem_campos_obrigatorios_e_perguntas_unicas():
    itens = [item for arquivo in CORPUS_DIR.glob("*.json") for item in json.loads(arquivo.read_text(encoding="utf-8"))]

    assert itens
    for item in itens:
        assert item["topico"] and item["pergunta"] and item["resposta"]
    perguntas = [item["pergunta"] for item in itens]
    assert len(perguntas) == len(set(perguntas))


@pytest.fixture
def embedding_falso(monkeypatch):
    monkeypatch.setattr(
        "semanticSearch.management.commands.seed_corpus.TextEmbeddingService",
        lambda: type("Fake", (), {"gerar_embedding": staticmethod(lambda texto: _vetor(0))})(),
    )


def _escrever(caminho, itens):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(itens), encoding="utf-8")


@pytest.mark.django_db
def test_seed_corpus_sincroniza_e_remove_entradas_ausentes(embedding_falso):
    _entrada("Entrada antiga fora do JSON", 5)

    call_command("seed_corpus")

    assert not EntradaCorpus.objects.filter(pergunta="Entrada antiga fora do JSON").exists()
    entrada = EntradaCorpus.objects.get(pergunta="Como definir uma variável em Python?")
    assert entrada.perguntas.filter(texto="Como criar uma variável em Python?").exists()


@pytest.mark.django_db
def test_seed_corpus_le_todos_os_arquivos_e_subpastas_e_recria_tudo(embedding_falso, monkeypatch, tmp_path):
    monkeypatch.setattr("semanticSearch.management.commands.seed_corpus.CORPUS_DIR", tmp_path)
    _escrever(tmp_path / "python.json", [
        {"topico": "Variáveis", "pergunta": "O que é variável?", "variacoes": ["Como criar variável?"], "resposta": "R1"},
    ])
    _escrever(tmp_path / "web" / "fastapi.json", [
        {"topico": "APIs", "pergunta": "O que é FastAPI?", "resposta": "R2"},
    ])
    antiga = _entrada("O que é variável?", 3)

    call_command("seed_corpus")

    assert set(EntradaCorpus.objects.values_list("pergunta", flat=True)) == {"O que é variável?", "O que é FastAPI?"}
    assert not EntradaCorpus.objects.filter(pk=antiga.pk).exists()
    assert PerguntaCorpus.objects.count() == 3


@pytest.mark.django_db
@pytest.mark.parametrize("arquivos", [
    {"a.json": [{"topico": "T", "pergunta": "Repetida?", "resposta": "R"}],
     "b.json": [{"topico": "T", "pergunta": "Repetida?", "resposta": "R"}]},
    {"a.json": [{"topico": "T", "pergunta": "Sem resposta?"}]},
    {"a.json": {"topico": "T"}},
])
def test_seed_corpus_invalido_nao_altera_o_banco(embedding_falso, monkeypatch, tmp_path, arquivos):
    monkeypatch.setattr("semanticSearch.management.commands.seed_corpus.CORPUS_DIR", tmp_path)
    for nome, itens in arquivos.items():
        _escrever(tmp_path / nome, itens)
    existente = _entrada("Entrada existente", 0)

    with pytest.raises(CommandError, match="nada foi alterado"):
        call_command("seed_corpus")

    assert EntradaCorpus.objects.filter(pk=existente.pk).exists()

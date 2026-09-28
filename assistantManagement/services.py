import re
import unicodedata
import uuid
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Optional

from django.db import transaction
from rest_framework.exceptions import NotFound, ValidationError
from assistantManagement.models import Mensagem, Sessao
from trackManagement.models import Trilha, Modulo, Matricula, ProgressoModulo
from trackManagement.services import efetivar_matricula
from activityManagement.models import Atividade
from intents.models import Intention
from learning.hint_service import CONTINGENCY_RESPONSE, HintService
from questionsManagement.models import Questao
from semanticSearch.service.nlp.preprocessor import TextPreprocessor
from semanticSearch.service.nlp.embedding_service import EmbeddingService
from semanticSearch.models import EntradaCorpus
from semanticSearch.service.corpus_search import CorpusSearch
from semanticSearch.service.nlp.intent_classifier import IntentClassifier

SUGESTOES_INICIAIS = [
    "Ver trilhas disponíveis",
    "Como funciona a plataforma?",
    "Quero me matricular em uma trilha",
]

SUGESTOES_AJUDA = [
    "Quais trilhas estão disponíveis?",
    "Quero me matricular em uma trilha",
    "Quero fazer o teste de nivelamento",
    "Quero começar do zero",
    "Pode me dar uma dica?",
    "Como definir uma variável em Python?",
]

SUGESTOES_NIVELAMENTO = [
    "Quero fazer o teste de nivelamento",
    "Quero começar do zero",
]

SUGESTOES_FALLBACK = [
    "Como funciona o Coach?",
    "Ver trilhas disponíveis",
]

# Palavras que não ajudam a distinguir uma trilha de outra na mensagem do estudante.
PALAVRAS_IGNORADAS = {
    "a", "o", "as", "os", "de", "da", "do", "das", "dos", "e", "em", "na", "no",
    "com", "para", "por", "um", "uma", "trilha", "trilhas", "curso", "cursos",
}


@dataclass
class RespostaIntencao:
    conteudo: str
    opcoes_trilhas: list = field(default_factory=list)
    sugestoes_rapidas: list = field(default_factory=list)
    acao: Optional[str] = None
    redirecionar_para: Optional[str] = None
    dados_acao: dict = field(default_factory=dict)
    # Permite ao handler corrigir a intenção reportada (ex.: FALLBACK respondido pelo corpus).
    intencao: Optional[str] = None


@dataclass
class ContextoConversa:
    usuario: Any
    sessao: Sessao
    conteudo: str
    resposta_base: str
    trilhas_ativas: list
    lista_trilhas: str
    vetor: Optional[list] = None
    trilha_id: Optional[uuid.UUID] = None
    atividade_id: Optional[uuid.UUID] = None
    questao_id: Optional[uuid.UUID] = None

    def resolver_trilha(self) -> Optional[Trilha]:
        """
        Descobre a trilha a que o estudante se refere: id explícito enviado pelo cliente,
        menção à trilha no texto ou, por último, a trilha já em discussão na sessão.
        """
        if self.trilha_id:
            trilha = next((t for t in self.trilhas_ativas if t.id == self.trilha_id), None)
            if trilha is None:
                raise NotFound("Trilha não encontrada.")
            return trilha

        trilha = identificar_trilha_no_texto(self.conteudo, self.trilhas_ativas)
        if trilha:
            return trilha

        contexto = self.sessao.trilha_contexto
        if contexto and contexto.ativo:
            return contexto
        return None

    def definir_trilha(self, trilha: Trilha):
        if self.sessao.trilha_contexto_id != trilha.id:
            self.sessao.trilha_contexto = trilha
            self.sessao.save(update_fields=["trilha_contexto", "atualizada_em"])


def _normalizar(texto: str) -> str:
    decomposto = unicodedata.normalize("NFKD", texto.lower())
    sem_acento = "".join(c for c in decomposto if unicodedata.category(c) != "Mn")
    return " ".join(re.findall(r"[a-z0-9]+", sem_acento))


def _palavras_chave(trilha: Trilha) -> set:
    texto = _normalizar(f"{trilha.titulo} {trilha.habilidade}")
    return {p for p in texto.split() if len(p) >= 3 and p not in PALAVRAS_IGNORADAS}


def _frases_trilha(trilha: Trilha) -> set:
    return {
        _normalizar(trilha.titulo),
        _normalizar(trilha.titulo.split(":", 1)[-1]),
        _normalizar(trilha.habilidade),
    }


def identificar_trilha_no_texto(texto: str, trilhas: list) -> Optional[Trilha]:
    """
    Procura a trilha citada na mensagem comparando título, subtítulo e habilidade.
    Palavras compartilhadas por várias trilhas (ex.: "python") não identificam nenhuma delas;
    em caso de empate, retorna None para que o Coach peça ao estudante que escolha.
    """
    texto_norm = f" {_normalizar(texto)} "
    frequencia = Counter(p for t in trilhas for p in _palavras_chave(t))

    melhor, melhor_pontuacao, empate = None, 0, False
    for trilha in trilhas:
        frases = _frases_trilha(trilha) | {p for p in _palavras_chave(trilha) if frequencia[p] == 1}
        pontuacao = max((len(f) for f in frases if f and f" {f} " in texto_norm), default=0)

        if pontuacao > melhor_pontuacao:
            melhor, melhor_pontuacao, empate = trilha, pontuacao, False
        elif pontuacao and pontuacao == melhor_pontuacao:
            empate = True

    return None if empate else melhor


def texto_para_classificacao(preprocessor, conteudo: str, trilhas: list) -> str:
    """
    Pré-processa a mensagem para o classificador. Quando o estudante cita uma trilha pelo nome,
    os termos dela são removidos: o nome é resolvido à parte e, se mantido, domina o embedding
    (ex.: "começar do zero na trilha Python: Analise de Dados" deixaria de soar como INICIAR_DO_ZERO).
    """
    texto = conteudo
    trilha = identificar_trilha_no_texto(conteudo, trilhas)
    if trilha:
        # A remoção ocorre antes do pré-processamento: a lematização depende do contexto da frase,
        # então os termos lematizados do título não coincidem com os da mensagem.
        sem_trilha = f" {_normalizar(conteudo)} "
        for frase in sorted(_frases_trilha(trilha) | _palavras_chave(trilha), key=len, reverse=True):
            while f" {frase} " in sem_trilha:
                sem_trilha = sem_trilha.replace(f" {frase} ", " ")
        if sem_trilha.strip():
            texto = sem_trilha.strip()

    texto_processado = preprocessor.processar(texto)
    # Se o texto processado estiver vazio (ex: pontuação pura), usa o texto original
    return texto_processado if texto_processado.strip() else conteudo


def _preencher(texto: str, **valores) -> str:
    for chave, valor in valores.items():
        texto = texto.replace("{" + chave + "}", str(valor))
    return texto


def _opcoes_trilhas(trilhas) -> list:
    return [
        {
            "id": str(trilha.id),
            "titulo": trilha.titulo,
            "habilidade": trilha.habilidade,
        }
        for trilha in trilhas
    ]


def _rota_trilha(trilha: Trilha) -> str:
    return f"/trilhas/{trilha.id}"


def _rota_atividade(atividade: Atividade) -> str:
    tipo = "licao" if atividade.conteudo_id else "atividade"
    return f"/trilhas/{atividade.modulo.trilha_id}/{tipo}/{atividade.id}"


def _buscar_atividade_diagnostica(trilha: Trilha) -> Optional[Atividade]:
    return Atividade.objects.filter(
        modulo__trilha=trilha,
        contexto_avaliacao="DIAGNOSTICO_INICIAL",
        ativo=True
    ).select_related("modulo").first()


@transaction.atomic
def _matricular_no_nivel_basico(usuario, trilha: Trilha):
    """
    Garante a matrícula EM_ANDAMENTO com o primeiro módulo liberado e os demais bloqueados.
    Retorna a matrícula e a primeira atividade regular (não diagnóstica) da trilha.
    """
    matricula, _ = Matricula.objects.get_or_create(
        usuario=usuario,
        trilha=trilha,
        defaults={"status": "EM_ANDAMENTO"}
    )
    if matricula.status != "EM_ANDAMENTO":
        matricula.status = "EM_ANDAMENTO"
        matricula.save()

    modulos = Modulo.objects.filter(trilha=trilha).order_by("ordem_modulo")
    for index, modulo in enumerate(modulos):
        status_modulo = "EM_ANDAMENTO" if index == 0 else "BLOQUEADO"
        progresso, created = ProgressoModulo.objects.get_or_create(
            matricula=matricula,
            modulo=modulo,
            defaults={"status": status_modulo}
        )
        if not created and index == 0 and progresso.status == "BLOQUEADO":
            progresso.status = "EM_ANDAMENTO"
            progresso.save()

    primeiro_modulo = modulos.first()
    primeira_atividade = None
    if primeiro_modulo:
        primeira_atividade = Atividade.objects.filter(
            modulo=primeiro_modulo,
            ativo=True
        ).exclude(
            contexto_avaliacao="DIAGNOSTICO_INICIAL"
        ).select_related("modulo").order_by("ordem").first()

    return matricula, primeira_atividade


def _pedir_escolha_de_trilha(ctx: ContextoConversa, pergunta: str, modelo_sugestao: str) -> RespostaIntencao:
    if not ctx.trilhas_ativas:
        return RespostaIntencao("No momento não há trilhas ativas disponíveis. Volte em breve!")
    return RespostaIntencao(
        conteudo=f"{pergunta}\n{ctx.lista_trilhas}",
        opcoes_trilhas=_opcoes_trilhas(ctx.trilhas_ativas),
        sugestoes_rapidas=[modelo_sugestao.format(titulo=t.titulo) for t in ctx.trilhas_ativas],
        acao="SELECIONAR_TRILHA",
    )


# --- Handlers das intenções canônicas (intents/management/commands/seed_intencoes.py) ---

def _tratar_saudacao(ctx: ContextoConversa) -> RespostaIntencao:
    return RespostaIntencao(ctx.resposta_base, sugestoes_rapidas=SUGESTOES_INICIAIS)


def _tratar_ajuda(ctx: ContextoConversa) -> RespostaIntencao:
    return RespostaIntencao(ctx.resposta_base, sugestoes_rapidas=SUGESTOES_AJUDA)


def _tratar_listar_trilhas(ctx: ContextoConversa) -> RespostaIntencao:
    if not ctx.trilhas_ativas:
        return RespostaIntencao("No momento não há trilhas ativas disponíveis. Volte em breve!")
    return RespostaIntencao(
        conteudo=ctx.resposta_base,
        opcoes_trilhas=_opcoes_trilhas(ctx.trilhas_ativas),
        sugestoes_rapidas=[f"Quero me matricular na trilha {t.titulo}" for t in ctx.trilhas_ativas],
    )


def _tratar_matricular_trilha(ctx: ContextoConversa) -> RespostaIntencao:
    trilha = ctx.resolver_trilha()
    if trilha is None:
        return _pedir_escolha_de_trilha(
            ctx,
            "Claro! Em qual trilha você quer se matricular?",
            "Quero me matricular na trilha {titulo}",
        )

    ctx.definir_trilha(trilha)
    dados = {"trilha_id": str(trilha.id)}

    matricula = Matricula.objects.filter(usuario=ctx.usuario, trilha=trilha).first()
    if matricula:
        return RespostaIntencao(
            conteudo=f"Você já está matriculado na trilha {trilha.titulo}. Vamos continuar de onde você parou?",
            acao="MATRICULA_EXISTENTE",
            redirecionar_para=_rota_trilha(trilha),
            dados_acao={**dados, "matricula_id": str(matricula.id)},
        )

    # Primeiro passo do diálogo (RFN02): apresenta a trilha e pede confirmação explícita.
    if "confirm" not in _normalizar(ctx.conteudo):
        return RespostaIntencao(
            conteudo=_preencher(ctx.resposta_base, titulo_trilha=trilha.titulo),
            sugestoes_rapidas=[f"Confirmo minha matrícula na trilha {trilha.titulo}", "Ver trilhas disponíveis"],
            acao="CONFIRMAR_MATRICULA",
            dados_acao=dados,
        )

    try:
        matricula = efetivar_matricula(ctx.usuario, trilha)
    except ValidationError:
        return RespostaIntencao(
            conteudo=f"A trilha {trilha.titulo} ainda não possui módulos disponíveis para matrícula. Que tal escolher outra?",
            opcoes_trilhas=_opcoes_trilhas(ctx.trilhas_ativas),
        )

    return RespostaIntencao(
        conteudo=(
            f"Matrícula confirmada na trilha {trilha.titulo}! Agora escolha como quer começar: "
            f"fazer o teste de nivelamento para calibrar seu nível ou começar do zero pelo nível básico."
        ),
        sugestoes_rapidas=SUGESTOES_NIVELAMENTO,
        acao="MATRICULA_EFETIVADA",
        dados_acao={**dados, "matricula_id": str(matricula.id)},
    )


def _tratar_iniciar_diagnostico(ctx: ContextoConversa) -> RespostaIntencao:
    trilha = ctx.resolver_trilha()
    if trilha is None:
        return _pedir_escolha_de_trilha(
            ctx,
            "Vamos lá! Para qual trilha você quer fazer o teste de nivelamento?",
            "Quero fazer o teste de nivelamento da trilha {titulo}",
        )

    ctx.definir_trilha(trilha)
    atividade = _buscar_atividade_diagnostica(trilha)
    if atividade is None:
        return RespostaIntencao(
            conteudo=(
                f"A trilha {trilha.titulo} ainda não possui um teste de nivelamento disponível. "
                f"Que tal começar pelo nível básico?"
            ),
            sugestoes_rapidas=["Quero começar do zero"],
            dados_acao={"trilha_id": str(trilha.id)},
        )

    # O posicionamento pós-diagnóstico exige matrícula; ela é criada no nível básico e reajustada depois.
    matricula, _ = _matricular_no_nivel_basico(ctx.usuario, trilha)

    return RespostaIntencao(
        conteudo=_preencher(ctx.resposta_base, titulo_trilha=trilha.titulo),
        acao="INICIAR_TESTE_DIAGNOSTICO",
        redirecionar_para=_rota_atividade(atividade),
        dados_acao={
            "trilha_id": str(trilha.id),
            "matricula_id": str(matricula.id),
            "atividade_diagnostica_id": str(atividade.id),
        },
    )


def _tratar_iniciar_do_zero(ctx: ContextoConversa) -> RespostaIntencao:
    trilha = ctx.resolver_trilha()
    if trilha is None:
        return _pedir_escolha_de_trilha(
            ctx,
            "Tudo bem! Em qual trilha você quer começar do zero?",
            "Quero começar do zero na trilha {titulo}",
        )

    ctx.definir_trilha(trilha)
    matricula, primeira_atividade = _matricular_no_nivel_basico(ctx.usuario, trilha)

    dados = {"trilha_id": str(trilha.id), "matricula_id": str(matricula.id)}
    if primeira_atividade:
        dados["primeira_atividade_id"] = str(primeira_atividade.id)

    return RespostaIntencao(
        conteudo=_preencher(ctx.resposta_base, titulo_trilha=trilha.titulo),
        acao="INICIAR_DO_INICIO",
        redirecionar_para=_rota_atividade(primeira_atividade) if primeira_atividade else _rota_trilha(trilha),
        dados_acao=dados,
    )


def _buscar_questao_para_dica(ctx: ContextoConversa) -> Optional[Questao]:
    questoes = Questao.objects.filter(atividade__ativo=True)
    if ctx.atividade_id:
        questoes = questoes.filter(atividade_id=ctx.atividade_id)

    if ctx.questao_id:
        questao = questoes.filter(pk=ctx.questao_id).first()
        if questao is None:
            raise NotFound("Questão não encontrada nesta atividade.")
        return questao

    if ctx.atividade_id:
        questoes = list(questoes.order_by("ordem_questao"))
        return next((q for q in questoes if q.dica_conceitual.strip()), questoes[0] if questoes else None)

    return None


def _tratar_pedir_dica(ctx: ContextoConversa) -> RespostaIntencao:
    questao = _buscar_questao_para_dica(ctx)
    if questao is None:
        return RespostaIntencao(
            "Para te dar uma dica, preciso saber em qual atividade você está. "
            "Abra a atividade e peça a dica por lá, que eu te ajudo sem entregar o gabarito!"
        )

    dados = {"questao_id": str(questao.id), "atividade_id": str(questao.atividade_id)}

    dica_local = questao.dica_conceitual.strip()
    if dica_local:
        return RespostaIntencao(
            conteudo=_preencher(ctx.resposta_base, texto_dica=dica_local.rstrip(".")),
            acao="DICA_FORNECIDA",
            dados_acao={**dados, "origem_resposta": "PLN_LOCAL"},
        )

    dica_externa = HintService._call_external_ai(questao, ctx.conteudo)
    if dica_externa:
        return RespostaIntencao(
            conteudo=dica_externa,
            acao="DICA_FORNECIDA",
            dados_acao={**dados, "origem_resposta": "IA_EXTERNA"},
        )

    return RespostaIntencao(CONTINGENCY_RESPONSE, dados_acao={**dados, "origem_resposta": "CONTINGENCIA"})


def _resposta_do_corpus(ctx: ContextoConversa, entrada: EntradaCorpus, similaridade: float) -> RespostaIntencao:
    modelo = ctx.resposta_base if "{resposta_corpus}" in ctx.resposta_base else "{resposta_corpus}"
    mesmo_topico = (EntradaCorpus.objects.filter(topico=entrada.topico, ativo=True)
                    .exclude(pk=entrada.pk).values_list("pergunta", flat=True)[:3])
    return RespostaIntencao(
        conteudo=_preencher(modelo, resposta_corpus=entrada.resposta),
        sugestoes_rapidas=list(mesmo_topico),
        acao="RESPOSTA_CORPUS",
        dados_acao={
            "entrada_corpus_id": str(entrada.id),
            "topico": entrada.topico,
            "similaridade": round(similaridade, 4),
        },
        intencao="DUVIDA_CONTEUDO",
    )


def _tratar_duvida_conteudo(ctx: ContextoConversa) -> RespostaIntencao:
    resultado = CorpusSearch().buscar(ctx.vetor)
    if resultado.entrada:
        return _resposta_do_corpus(ctx, resultado.entrada, resultado.similaridade)

    if resultado.relacionadas:
        return RespostaIntencao(
            "Não encontrei exatamente essa dúvida na minha base de conhecimento. Você quis perguntar alguma destas?",
            sugestoes_rapidas=[e.pergunta for e in resultado.relacionadas],
        )
    return RespostaIntencao(
        "Ainda não tenho esse assunto na minha base de conhecimento. "
        "Tente reformular a pergunta ou pergunte sobre outro tema de Python.",
        sugestoes_rapidas=SUGESTOES_FALLBACK,
    )


def _tratar_fallback(ctx: ContextoConversa) -> RespostaIntencao:
    # Perguntas conceituais com formulação distante dos exemplos da intenção ainda podem estar no corpus.
    resultado = CorpusSearch().buscar(ctx.vetor)
    if resultado.entrada:
        return _resposta_do_corpus(ctx, resultado.entrada, resultado.similaridade)
    if resultado.relacionadas:
        return RespostaIntencao(
            f"{ctx.resposta_base} Talvez você queira perguntar:",
            sugestoes_rapidas=[e.pergunta for e in resultado.relacionadas],
        )
    return RespostaIntencao(ctx.resposta_base, sugestoes_rapidas=SUGESTOES_FALLBACK)


HANDLERS_INTENCAO = {
    "SAUDACAO": _tratar_saudacao,
    "AJUDA_COMANDOS": _tratar_ajuda,
    "LISTAR_TRILHAS": _tratar_listar_trilhas,
    "MATRICULAR_TRILHA": _tratar_matricular_trilha,
    "INICIAR_DIAGNOSTICO": _tratar_iniciar_diagnostico,
    "INICIAR_DO_ZERO": _tratar_iniciar_do_zero,
    "PEDIR_DICA": _tratar_pedir_dica,
    "DUVIDA_CONTEUDO": _tratar_duvida_conteudo,
}


def iniciar_sessao_chat(usuario):
    """
    Cria uma sessão ativa para o estudante e retorna a mensagem de abertura do Coach
    com sugestões rápidas de diálogo.
    """
    sessao = Sessao.objects.create(usuario=usuario)
    nome_usuario = usuario.nome or usuario.apelido or "Estudante"

    conteudo_abertura = (
        f"Olá, {nome_usuario}! Seja muito bem-vindo ao VariSkill! "
        f"Eu sou o seu Coach de aprendizagem. Qual área você gostaria de dominar hoje?"
    )

    mensagem_inicial = Mensagem.objects.create(
        sessao=sessao,
        remetente=Mensagem.Remetente.ASSISTENTE,
        conteudo=conteudo_abertura,
    )

    return {
        "sessao_id": sessao.id,
        "mensagem_inicial": {
            "id": mensagem_inicial.id,
            "remetente": mensagem_inicial.remetente,
            "conteudo": mensagem_inicial.conteudo,
            "sugestoes_rapidas": SUGESTOES_INICIAIS,
            "criada_em": mensagem_inicial.criada_em,
        },
    }


def enviar_mensagem_chat(usuario, sessao_id, conteudo, trilha_id=None, atividade_id=None, questao_id=None):
    """
    Recebe a mensagem do usuário, pré-processa o texto, gera embedding,
    classifica a intenção via pgvector, executa a ação de sistema correspondente
    (listar trilhas, matricular, diagnóstico, nível básico, dica) e salva ambas as mensagens.
    """
    sessao = Sessao.objects.select_related("trilha_contexto").filter(id=sessao_id, usuario=usuario).first()
    if not sessao:
        raise NotFound("Sessão do assistente não encontrada para este usuário.")

    # Pré-carrega trilhas ativas para enriquecer contexto se necessário
    trilhas_ativas = list(Trilha.objects.filter(ativo=True))

    # 1. Pipeline local de PLN
    preprocessor = TextPreprocessor.get_instance()
    texto_para_embedding = texto_para_classificacao(preprocessor, conteudo, trilhas_ativas)

    embedding_service = EmbeddingService.get_instance()
    vetor = embedding_service.gerar_embedding(texto_para_embedding)
    lista_trilhas_formatada = "\n".join(
        f"{idx}. **{t.titulo}** ({t.habilidade})"
        for idx, t in enumerate(trilhas_ativas, start=1)
    )

    classifier = IntentClassifier()
    contexto = {
        "nome": usuario.nome or usuario.apelido or "Estudante",
        "lista_trilhas": lista_trilhas_formatada,
    }
    classificacao = classifier.classificar(vetor, contexto=contexto)

    intencao_codigo = classificacao.get("intencao", "FALLBACK")
    similaridade = classificacao.get("similaridade", 0.0)
    resposta_texto = classificacao.get("resposta_texto", "")

    # Se a resposta contiver {lista_trilhas} por ventura não substituída
    if "{lista_trilhas}" in resposta_texto:
        resposta_texto = resposta_texto.replace("{lista_trilhas}", lista_trilhas_formatada)

    # Distância = 1.0 - similaridade
    distancia = max(0.0, 1.0 - similaridade)

    intencao_obj = None
    if intencao_codigo and intencao_codigo != "FALLBACK":
        intencao_obj = Intention.objects.filter(code=intencao_codigo).first()

    # 2. Execução da ação de sistema associada à intenção
    ctx = ContextoConversa(
        usuario=usuario,
        sessao=sessao,
        conteudo=conteudo,
        resposta_base=resposta_texto,
        trilhas_ativas=trilhas_ativas,
        lista_trilhas=lista_trilhas_formatada,
        vetor=vetor,
        trilha_id=trilha_id,
        atividade_id=atividade_id,
        questao_id=questao_id,
    )
    handler = HANDLERS_INTENCAO.get(intencao_codigo, _tratar_fallback)
    resposta = handler(ctx)
    if resposta.intencao and resposta.intencao != intencao_codigo:
        intencao_codigo = resposta.intencao
        intencao_obj = Intention.objects.filter(code=intencao_codigo).first()

    # 3. Persistência atômica das mensagens (usuário e assistente juntas para evitar mensagens órfãs)
    with transaction.atomic():
        Mensagem.objects.create(
            sessao=sessao,
            remetente=Mensagem.Remetente.USUARIO,
            conteudo=conteudo,
        )

        mensagem_assistente = Mensagem.objects.create(
            sessao=sessao,
            remetente=Mensagem.Remetente.ASSISTENTE,
            conteudo=resposta.conteudo,
            intencao=intencao_obj,
            distancia=distancia,
        )

    return {
        "resposta_assistente": {
            "id": mensagem_assistente.id,
            "remetente": mensagem_assistente.remetente,
            "conteudo": mensagem_assistente.conteudo,
            "intencao_detectada": intencao_codigo,
            "opcoes_trilhas": resposta.opcoes_trilhas,
            "sugestoes_rapidas": resposta.sugestoes_rapidas,
            "acao": resposta.acao,
            "redirecionar_para": resposta.redirecionar_para,
            "dados_acao": resposta.dados_acao,
            "criada_em": mensagem_assistente.criada_em,
        }
    }


def obter_historico_chat(usuario, sessao_id):
    """
    Retorna o histórico sequencial de balões trocados na sessão.
    """
    sessao = Sessao.objects.filter(id=sessao_id, usuario=usuario).first()
    if not sessao:
        raise NotFound("Sessão do assistente não encontrada para este usuário.")

    mensagens = sessao.mensagens.all().order_by("criada_em")

    historico = []
    for msg in mensagens:
        intencao_codigo = msg.intencao.code if msg.intencao else None
        item = {
            "id": msg.id,
            "remetente": msg.remetente,
            "conteudo": msg.conteudo,
            "intencao_detectada": intencao_codigo,
            "criada_em": msg.criada_em,
        }
        if intencao_codigo == "LISTAR_TRILHAS":
            item["opcoes_trilhas"] = _opcoes_trilhas(Trilha.objects.filter(ativo=True))
        historico.append(item)

    return {
        "sessao_id": sessao.id,
        "total_mensagens": len(historico),
        "mensagens": historico,
    }


def decidir_nivel_trilha(usuario, sessao_id, trilha_id, opcao):
    sessao = Sessao.objects.filter(id=sessao_id, usuario=usuario).first()
    if not sessao:
        raise NotFound("Sessão do assistente não encontrada para este usuário.")

    trilha = Trilha.objects.filter(id=trilha_id).first()
    if not trilha:
        raise NotFound("Trilha não encontrada.")

    if opcao == "TESTE_DIAGNOSTICO":
        atividade_diagnostica = _buscar_atividade_diagnostica(trilha)

        if not atividade_diagnostica:
            raise ValidationError({
                "trilha_id": "Nenhuma atividade diagnóstica encontrada para esta trilha."
            })

        return {
            "acao": "INICIAR_TESTE_DIAGNOSTICO",
            "mensagem_assistente": f"Excelente desafio! Preparei uma bateria rápida para calibrarmos seu nível em {trilha.titulo}. Clique no botão abaixo para começar:",
            "atividade_diagnostica_id": str(atividade_diagnostica.id),
            "redirecionar_para": f"/atividades/{atividade_diagnostica.id}"
        }

    # Opções 'INICIO', 'INICIAR_DO_INICIO' ou 'INICIAR_DO_ZERO'
    _, primeira_atividade = _matricular_no_nivel_basico(usuario, trilha)

    primeira_atividade_id = str(primeira_atividade.id) if primeira_atividade else None
    redirecionar_para = f"/atividades/{primeira_atividade_id}" if primeira_atividade_id else f"/trilhas/{trilha.id}"

    response_data = {
        "acao": "INICIAR_DO_INICIO",
        "mensagem_assistente": f"Ótima escolha! Sua matrícula na trilha '{trilha.titulo}' foi efetuada e você já pode começar a primeira atividade.",
        "redirecionar_para": redirecionar_para
    }
    if primeira_atividade_id:
        response_data["primeira_atividade_id"] = primeira_atividade_id

    return response_data

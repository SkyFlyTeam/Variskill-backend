from rest_framework.exceptions import NotFound, ValidationError
from assistantManagement.models import Mensagem, Sessao
from trackManagement.models import Trilha, Modulo, Matricula, ProgressoModulo
from activityManagement.models import Atividade
from intents.models import Intention
from semanticSearch.service.nlp.preprocessor import TextPreprocessor
from semanticSearch.service.nlp.embedding_service import EmbeddingService
from semanticSearch.service.nlp.intent_classifier import IntentClassifier

SUGESTOES_INICIAIS = [
    "Ver trilhas disponíveis",
    "Como funciona a plataforma?",
    "Quero aprender Javascript",
]


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


def enviar_mensagem_chat(usuario, sessao_id, conteudo):
    """
    Recebe a mensagem do usuário, pré-processa o texto, gera embedding,
    classifica a intenção via pgvector e salva ambas as mensagens.
    Se a intenção for LISTAR_TRILHAS, inclui as opções de trilhas abertas.
    """
    sessao = Sessao.objects.filter(id=sessao_id, usuario=usuario).first()
    if not sessao:
        raise NotFound("Sessão do assistente não encontrada para este usuário.")

    # 1. Salva mensagem do usuário
    Mensagem.objects.create(
        sessao=sessao,
        remetente=Mensagem.Remetente.USUARIO,
        conteudo=conteudo,
    )

    # 2. Pipeline local de PLN
    preprocessor = TextPreprocessor.get_instance()
    texto_processado = preprocessor.processar(conteudo)

    embedding_service = EmbeddingService.get_instance()
    # Se o texto processado estiver vazio (ex: pontuação pura), gera embedding do texto original
    texto_para_embedding = texto_processado if texto_processado.strip() else conteudo
    vetor = embedding_service.gerar_embedding(texto_para_embedding)

    classifier = IntentClassifier()
    contexto = {"nome": usuario.nome or usuario.apelido or "Estudante"}
    classificacao = classifier.classificar(vetor, contexto=contexto)

    intencao_codigo = classificacao.get("intencao", "FALLBACK")
    similaridade = classificacao.get("similaridade", 0.0)
    resposta_texto = classificacao.get("resposta_texto", "")

    # Distância = 1.0 - similaridade
    distancia = max(0.0, 1.0 - similaridade)

    intencao_obj = None
    if intencao_codigo and intencao_codigo != "FALLBACK":
        intencao_obj = Intention.objects.filter(code=intencao_codigo).first()

    opcoes_trilhas = []
    if intencao_codigo == "LISTAR_TRILHAS":
        trilhas = Trilha.objects.filter(ativo=True)
        opcoes_trilhas = [
            {
                "id": str(trilha.id),
                "titulo": trilha.titulo,
                "habilidade": trilha.habilidade,
            }
            for trilha in trilhas
        ]

    # 3. Salva mensagem de resposta do assistente
    mensagem_assistente = Mensagem.objects.create(
        sessao=sessao,
        remetente=Mensagem.Remetente.ASSISTENTE,
        conteudo=resposta_texto,
        intencao=intencao_obj,
        distancia=distancia,
    )

    return {
        "resposta_assistente": {
            "id": mensagem_assistente.id,
            "remetente": mensagem_assistente.remetente,
            "conteudo": mensagem_assistente.conteudo,
            "intencao_detectada": intencao_codigo,
            "opcoes_trilhas": opcoes_trilhas,
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
            trilhas = Trilha.objects.filter(ativo=True)
            item["opcoes_trilhas"] = [
                {
                    "id": str(trilha.id),
                    "titulo": trilha.titulo,
                    "habilidade": trilha.habilidade,
                }
                for trilha in trilhas
            ]
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
        atividade_diagnostica = Atividade.objects.filter(
            modulo__trilha=trilha,
            contexto_avaliacao="DIAGNOSTICO_INICIAL",
            ativo=True
        ).first()

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

    # Opções 'INICIO' ou 'INICIAR_DO_INICIO'
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
        ).order_by("ordem").first()

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



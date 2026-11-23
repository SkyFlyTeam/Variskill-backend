from django.core.management.base import BaseCommand

from intents.models import Intention, IntentionExample, Response
from semanticSearch.service.text_embedding_service import TextEmbeddingService

INTENCOES_CANONICAS = [
    {"code": "SAUDACAO", "system_action": "ACOLHER_ESTUDANTE", "description": "Acolhimento e saudação ao estudante, incluindo retomada de estudos e reconhecimento de dificuldade.", "examples": ["Olá", "Oi", "Oi, tudo bem?", "Bom dia, Coach", "Quero começar meus estudos", "Olá, estou chegando agora", "Boa tarde", "Estou de volta", "Voltei para estudar", "Quero retomar os estudos", "Estou aqui de novo", "Pode me ajudar?"], "responses": ["Olá, {nome}! Que bom ter você aqui.", "Boas-vindas, {nome}! Vamos aprender juntos.", "Que bom te ver de novo, {nome}! Pronto para continuar?"]},
    # Catálogos contextuais de saudação (Pilares A, B e C). Não têm exemplos: o classificador nunca as
    # retorna; o handler de SAUDACAO e a abertura de sessão escolhem a categoria pelo estado do estudante
    # e usam só os templates cujos slots estão disponíveis ({nome}, {streak_dias}, {nome_atividade},
    # {nome_modulo}, {topico_dificuldade}, {ponto_forte}).
    {
        "code": "SAUDACAO_BOAS_VINDAS",
        "system_action": "ACOLHER_ESTUDANTE_NOVATO",
        "description": "Acolhimento e apresentação do Coach para estudante novato ou sem pendências.",
        "examples": [],
        "responses": [
            "Olá, {nome}! Boas-vindas ao VariSkill! Eu sou o seu Coach de aprendizagem. Qual área você gostaria de dominar hoje?",
            "Olá, {nome}! Eu sou o Coach do VariSkill e vou te acompanhar nos estudos. Por onde você quer começar?",
            "Olá, {nome}! Que bom ter você aqui. Posso recomendar uma trilha ou mostrar as opções disponíveis. O que prefere?",
        ],
    },
    {
        "code": "SAUDACAO_STREAK",
        "system_action": "RECONHECER_STREAK",
        "description": "Pilar A: reconhece a sequência ativa de dias de estudo (streak >= 3).",
        "examples": [],
        "responses": [
            "Olá, {nome}! Você está há {streak_dias} dias seguidos estudando. Que sequência incrível!",
            "{nome}, são {streak_dias} dias de ofensiva! Bora manter o ritmo com {nome_atividade}?",
            "{streak_dias} dias seguidos, {nome}! Seu domínio em {ponto_forte} mostra que a constância funciona. Vamos continuar?",
        ],
    },
    {
        "code": "SAUDACAO_RETORNO",
        "system_action": "REENGAJAR_ESTUDANTE",
        "description": "Pilar A: acolhe o estudante que retorna após dias sem estudar.",
        "examples": [],
        "responses": [
            "Que bom ter você de volta, {nome}! Que tal recomeçar sua sequência de estudos hoje?",
            "Que bom ter você de volta, {nome}! Sua próxima atividade, {nome_atividade}, está esperando por você.",
            "Olá de novo, {nome}! Sua trilha te espera no módulo {nome_modulo}. Bora reacender essa ofensiva?",
        ],
    },
    {
        "code": "SAUDACAO_RETOMADA",
        "system_action": "SUGERIR_CONTINUIDADE",
        "description": "Pilar B: sugere a continuidade da próxima atividade pendente da trilha matriculada.",
        "examples": [],
        "responses": [
            "Olá, {nome}! Vamos continuar de onde você parou? Sua próxima atividade é {nome_atividade}, no módulo {nome_modulo}.",
            "Que bom te ver, {nome}! {nome_atividade} ({nome_modulo}) está esperando por você.",
            "Pronto para avançar em {nome_modulo}, {nome}? A próxima atividade é {nome_atividade}.",
        ],
    },
    {
        "code": "SAUDACAO_REFORCO",
        "system_action": "OFERECER_REFORCO",
        "description": "Pilar C: oferece reforço no tópico vulnerável mapeado pela memória pedagógica.",
        "examples": [],
        "responses": [
            "Que bom ter você de volta, {nome}! Notei que questões sobre '{topico_dificuldade}' foram desafiadoras na última atividade. Quer revisar esse conceito?",
            "Olá, {nome}! Você já manda bem em {ponto_forte}. Que tal reforçarmos '{topico_dificuldade}' juntos?",
            "Olá, {nome}! '{topico_dificuldade}' merece uma revisão rápida. Vamos reforçar esse conceito antes de seguir com {nome_atividade}?",
        ],
    },
    {"code": "AJUDA_COMANDOS", "system_action": "APRESENTAR_RECURSOS", "description": "Apresentação dos recursos do Coach e de como ele funciona.", "examples": ["O que você pode fazer?", "Como funciona o Coach?", "Preciso de ajuda para usar a plataforma", "Quais comandos estão disponíveis?", "Pode me explicar como estudar aqui?", "Como funciona a plataforma?"], "responses": ["Posso ajudar você a listar trilhas, escolher uma trilha, fazer o nivelamento e pedir dicas.", "Você pode perguntar pelas trilhas, iniciar seu diagnóstico, começar do zero ou pedir uma dica durante a atividade."]},
    {"code": "LISTAR_TRILHAS", "system_action": "LISTAR_TRILHAS_ATIVAS", "description": "Listagem das trilhas ativas disponíveis para matrícula.", "examples": ["Quais trilhas estão disponíveis?", "Quero ver as trilhas", "Me mostre as opções de cursos", "Que trilhas posso fazer?", "Listar trilhas ativas", "Me mostre as trilhas disponíveis", "Quais cursos existem na plataforma?", "Ver o catálogo de trilhas"], "responses": ["Estas são as trilhas disponíveis para você: {lista_trilhas}.", "Encontrei estas trilhas ativas: {lista_trilhas}. Qual delas você quer conhecer?"]},
    {"code": "MATRICULAR_TRILHA", "system_action": "MATRICULAR_EM_TRILHA", "description": "Escolha e confirmação da trilha pelo diálogo de matrícula (RFN02).", "examples": ["Quero me matricular em uma trilha", "Pode me inscrever nessa trilha", "Quero escolher a trilha de Python", "Como faço minha matrícula?", "Confirmo minha matrícula na trilha", "Quero me inscrever na trilha"], "responses": ["Vamos confirmar sua matrícula na trilha {titulo_trilha}.", "Ótima escolha! Posso matricular você na trilha {titulo_trilha}. Confirma?"]},
    {
        "code": "INICIAR_DIAGNOSTICO",
        "system_action": "DISPARAR_TESTE_DIAGNOSTICO",
        "description": "Estudante opta por realizar o teste de nivelamento/diagnóstico inicial.",
        "examples": [
            "já sei programar, quero testar meu nível",
            "fazer o teste de nivelamento",
            "quero provar que sou intermediário",
            "quero fazer a avaliação diagnóstica",
            "prefiro fazer o teste diagnóstico",
            "quero fazer o teste de nivelamento da trilha",
        ],
        "responses": [
            "Excelente! Vamos realizar uma avaliação rápida para calibrar seu nível.",
            "Vamos começar seu diagnóstico para encontrar o melhor ponto de partida.",
        ]
    },
    {"code": "INICIAR_DO_ZERO", "system_action": "INICIAR_NO_NIVEL_BASICO", "description": "Matrícula direta do estudante no nível básico (RFN03).", "examples": ["Quero começar do zero", "Sou iniciante, pode me colocar no básico", "Não tenho experiência e quero começar", "Quero iniciar pelo nível básico", "Prefiro não fazer o teste e começar do zero", "Quero começar do zero na trilha"], "responses": ["Tudo bem, {nome}! Vamos começar pelo nível básico.", "Você será matriculado no nível inicial da trilha {titulo_trilha}."]},
    {
        "code": "DUVIDA_CONTEUDO",
        "system_action": "RESPONDER_COM_CORPUS",
        "description": "Dúvida conceitual livre (ex.: como definir uma variável em Python), respondida pela base de conhecimento (semanticSearch/corpus).",
        "examples": [
            "Como definir uma variável em Python?",
            "O que é uma lista em Python?",
            "Me explica como funciona uma função",
            "Qual a diferença entre lista e tupla?",
            "Como funciona o laço for?",
            "Tenho uma dúvida sobre Python",
            "Para que serve esse comando em Python?",
            "Quero tirar uma dúvida",
            # Revisão de conteúdo (chip "Quero revisar <módulo>" e card Meu Raio-X): o corpus indexa
            # "Quero revisar <módulo>", então a revisão é respondida como dúvida de conteúdo.
            "Quero revisar",
            "Revisar conteúdo",
            "Quero revisar esse conteúdo",
            "Preciso revisar a matéria",
            "Me ajude a revisar esse tema",
            "Revisão do conteúdo",
            "Quero reforçar esse conceito",
            "Tenho dificuldade nesse assunto",
            "Quero revisar. Me dá uma dica de estudo?",
        ],
        "responses": [
            "{resposta_corpus}",
            "Boa pergunta! {resposta_corpus}",
        ],
    },
    {"code": "PEDIR_DICA", "system_action": "FORNECER_DICA_PEDAGOGICA", "description": "Orientação pedagógica durante a atividade, sem entregar o gabarito (RFN06).", "examples": ["Pode me dar uma dica?", "Preciso de uma orientação para resolver", "Não entendi, me ajude sem dar a resposta", "Tem alguma pista para esta atividade?", "Como posso pensar nessa questão?", "Me dá uma dica", "Preciso de uma dica para resolver a questão", "Estou travado nesse exercício"], "responses": ["Claro! Pense no primeiro passo e observe as informações mais importantes: {texto_dica}.", "Aqui vai uma pista, sem entregar o gabarito: {texto_dica}."]},
    {
        "code": "RECOMENDAR_TRILHA",
        "system_action": "RECOMENDAR_TRILHAS_CONTEXTUAL",
        "description": "Recomendação de trilhas pelo tema que o estudante quer aprender ou, sem tema, pelos interesses e histórico dele.",
        # O tema citado (ex.: "python", "devops", "variaveis") é removido da mensagem antes da classificação
        # quando identifica uma trilha ou um módulo, por isso há exemplos com e sem o tema.
        "examples": [
            "Qual trilha você me recomenda?",
            "Me recomende uma trilha",
            "Qual trilha devo estudar?",
            "Me sugira uma trilha",
            "Qual curso combina comigo?",
            "Recomende uma trilha complementar",
            "Não sei por onde começar, me indique um caminho",
            "Quais trilhas combinam com os meus interesses?",
            "Me dê uma sugestão de trilha de estudo",
            "O que você sugere que eu aprenda?",
            "Quero aprender",
            "Quero estudar",
            "Quero entender",
            "Quero aprender, por onde começo?",
            "Quero entender, qual trilha faço?",
            "Qual trilha faço?",
            "Tenho interesse, o que faço?",
            "Me indica uma trilha",
            "Quero aprender programação, por onde começo?",
            # Temas fora do catálogo também são pedidos de recomendação: o Coach gera a trilha com IA.
            "Quero aprender culinária, por onde começo?",
            "Quero aprender violão, qual trilha faço?",
            "Qual trilha faço para aprender esse assunto?",
            "Tenho interesse nessa área, qual trilha você indica?",
            "Quero aprender, o nível bem básico, sabe? Por onde começo?",
            "Quero aprender do básico, por onde começo?",
            "Sou iniciante nesse assunto, por onde começo?",
            "Como aprendo isso?",
            "Como aprendo a usar?",
        ],
        "responses": [
            "Com base no seu perfil e interesses, selecionei estas recomendações para você:",
            "Preparei uma recomendação especial de trilhas com base no que você mais gosta e no seu progresso:",
        ],
    },
    {
        "code": "CONSULTAR_NIVEL",
        "system_action": "INFORMAR_NIVEL_XP",
        "description": "Consulta do nível de gamificação do estudante e do XP restante para o próximo nível.",
        "examples": [
            "qual meu nível",
            "em que nível estou",
            "quanto falta pro próximo nível",
            "quanto XP eu tenho?",
            "quantos pontos de experiência faltam para subir de nível?",
            "qual é o meu nível atual?",
            "quero ver meu XP",
            "quanto XP falta para subir de nível?",
            "Ver meu progresso",
            "Como estou indo nos estudos?",
            "Como anda meu progresso?",
        ],
        "responses": [
            "Você está no nível {nivel}, com {xp_atual} XP. Faltam {xp_restante} XP para o nível {proximo_nivel}!",
            "{nome}, seu nível atual é {nivel} ({progresso_pct}% da faixa concluída). Mais {xp_restante} XP e você chega ao nível {proximo_nivel}.",
        ],
    },
    {
        "code": "PROXIMA_ATIVIDADE",
        "system_action": "ABRIR_PROXIMA_ATIVIDADE",
        "description": "Indicação e abertura da próxima atividade pendente da trilha ativa do estudante.",
        "examples": [
            "o que estudar agora",
            "qual minha próxima lição",
            "abrir próximo exercício",
            "qual a próxima atividade?",
            "o que eu faço agora na trilha?",
            "me leva para o próximo exercício",
            "quero seguir para a próxima lição",
            "Continuar a atividade",
            "Continuar a lição",
            # Chip "Continuar <atividade>": o título da atividade é removido antes da classificação.
            "Continuar",
            "Quero continuar",
            "Continuar minha trilha",
            "Quero continuar a trilha",
            "Continuar meu curso",
            "Continuar de onde parei",
            "Posso continuar de onde parei?",
            "Continuar estudando",
            "Retomar minha trilha",
            "Seguir na minha trilha",
        ],
        "responses": [
            "Sua próxima atividade é {titulo_atividade}, no módulo {titulo_modulo}. Bora lá!",
            "Próximo passo na trilha {titulo_trilha}: {titulo_atividade} ({titulo_modulo}). Vou te levar até lá.",
        ],
    },
]


def _get_embedding(text: str):
    return TextEmbeddingService().gerar_embedding(text)


class Command(BaseCommand):
    help = "Cadastra as intenções canônicas (exemplos com embeddings e respostas) no banco de dados."

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

            # Exemplos removidos do catálogo deixam de existir no banco (ex.: frase movida de intenção).
            intention.examples.exclude(text__in=item["examples"]).delete()

            for resp_text in item["responses"]:
                Response.objects.get_or_create(
                    intention=intention,
                    text=resp_text,
                )

            self.stdout.write(self.style.SUCCESS(f"Intenção '{item['code']}' cadastrada com sucesso!"))

        self.stdout.write(self.style.SUCCESS("Seed de intenções concluído com sucesso."))

from django.core.management.base import BaseCommand

from intents.models import Intention, IntentionExample, Response
from semanticSearch.service.text_embedding_service import TextEmbeddingService

INTENCOES_CANONICAS = [
    {"code": "SAUDACAO", "system_action": "ACOLHER_ESTUDANTE", "description": "Acolhimento e saudação ao estudante.", "examples": ["Olá", "Oi, tudo bem?", "Bom dia, Coach", "Quero começar meus estudos", "Olá, estou chegando agora"], "responses": ["Olá, {nome}! Que bom ter você aqui.", "Boas-vindas, {nome}! Vamos aprender juntos."]},
    {"code": "AJUDA_COMANDOS", "system_action": "APRESENTAR_RECURSOS", "description": "Apresentação dos recursos do Coach e de como ele funciona.", "examples": ["O que você pode fazer?", "Como funciona o Coach?", "Preciso de ajuda para usar a plataforma", "Quais comandos estão disponíveis?", "Pode me explicar como estudar aqui?", "Como funciona a plataforma?"], "responses": ["Posso ajudar você a listar trilhas, escolher uma trilha, fazer o nivelamento e pedir dicas.", "Você pode perguntar pelas trilhas, iniciar seu diagnóstico, começar do zero ou pedir uma dica durante a atividade."]},
    {"code": "LISTAR_TRILHAS", "system_action": "LISTAR_TRILHAS_ATIVAS", "description": "Listagem das trilhas ativas disponíveis para matrícula.", "examples": ["Quais trilhas estão disponíveis?", "Quero ver as trilhas", "Me mostre as opções de cursos", "Que trilhas posso fazer?", "Listar trilhas ativas"], "responses": ["Estas são as trilhas disponíveis para você: {lista_trilhas}.", "Encontrei estas trilhas ativas: {lista_trilhas}. Qual delas você quer conhecer?"]},
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
        ],
        "responses": [
            "{resposta_corpus}",
            "Boa pergunta! {resposta_corpus}",
        ],
    },
    {"code": "PEDIR_DICA", "system_action": "FORNECER_DICA_PEDAGOGICA", "description": "Orientação pedagógica durante a atividade, sem entregar o gabarito (RFN06).", "examples": ["Pode me dar uma dica?", "Preciso de uma orientação para resolver", "Não entendi, me ajude sem dar a resposta", "Tem alguma pista para esta atividade?", "Como posso pensar nessa questão?"], "responses": ["Claro! Pense no primeiro passo e observe as informações mais importantes: {texto_dica}.", "Aqui vai uma pista, sem entregar o gabarito: {texto_dica}."]},
]


def _get_embedding(text: str):
    return TextEmbeddingService().gerar_embedding(text)


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

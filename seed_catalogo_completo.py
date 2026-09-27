import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings')
django.setup()

from trackManagement.models import Trilha, Modulo
from activityManagement.models import Atividade, Conteudo
from questionsManagement.models import Questao, QuestaoOpcao

print("Iniciando seed do catalogo completo...")

# Limpar dados pedagogicos anteriores caso existam
QuestaoOpcao.objects.all().delete()
Questao.objects.all().delete()
Atividade.objects.all().delete()
Conteudo.objects.all().delete()
Modulo.objects.all().delete()
Trilha.objects.all().delete()

# ==========================================
# TRILHA 1: Javascript (Frontend)
# ==========================================
trilha_js = Trilha.objects.create(
    titulo="Javascript",
    descricao="Aprenda a linguagem essencial da web moderna, do basico ao assincrono.",
    habilidade="Frontend",
    ativo=True
)

modulos_js_data = [
    {
        "titulo": "Fundamentos da Linguagem",
        "descricao": "Variaveis, tipos primitivos, operadores e estruturas de controle.",
        "nivel": "INICIANTE",
        "ordem_modulo": 1,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "Declaracao de Variaveis no JS Moderno",
                "descricao": "Diferencas fundamentais entre const, let e var.",
                "xp": 50,
                "texto": (
                    "### Variaveis no JavaScript Moderno (ES6+)\n\n"
                    "No JavaScript moderno, evitamos o uso de `var` devido ao escopo de funcao e hoisting imprevisivel.\n\n"
                    "```javascript\n"
                    "const pi = 3.14159; // Imutavel por reatribuicao\n"
                    "let contador = 0;   // Mutavel, escopo de bloco\n"
                    "contador += 1;\n"
                    "```\n\n"
                    "Use sempre `const` por padrao e `let` apenas quando a variavel precisar ser reatribuida."
                )
            },
            {
                "tipo": "QUESTAO",
                "titulo": "Exercicio: Declaracao Imutavel",
                "descricao": "Teste seu conhecimento sobre variaveis imutaveis no JS.",
                "xp": 100,
                "enunciado": "Qual palavra-chave deve ser utilizada para declarar uma variavel que nao pode sofrer reatribuicao?",
                "opcoes": ["var", "const", "let", "def"],
                "gabarito_idx": 1, # const
                "dica": "Lembre-se da palavra em ingles que remete a algo fixo e 'constante'."
            },
            {
                "tipo": "CONTEUDO",
                "titulo": "Tipos Primitivos e Operadores",
                "descricao": "Entenda string, number, boolean, null, undefined e operadores de comparacao estrita.",
                "xp": 50,
                "texto": (
                    "### Comparacao Estrita (===)\n\n"
                    "O operador `===` compara valor e tipo sem realizar coercao implicita:\n\n"
                    "```javascript\n"
                    "console.log(5 === '5'); // false\n"
                    "console.log(5 == '5');  // true (evite!)\n"
                    "```"
                )
            },
            {
                "tipo": "QUESTAO",
                "titulo": "Exercicio: Igualdade Estrita",
                "descricao": "Avalie o resultado da comparacao estrita entre tipos distintos.",
                "xp": 100,
                "enunciado": "Qual e o resultado da expressao: 10 === '10' em JavaScript?",
                "opcoes": ["true", "false", "undefined", "TypeError"],
                "gabarito_idx": 1, # false
                "dica": "O operador === verifica tanto o valor quanto o tipo de dado de cada operando."
            },
            {
                "tipo": "QUESTAO",
                "titulo": "Desafio do Modulo: Controle de Fluxo",
                "descricao": "Aplique condicionais para validar regras de negocio.",
                "xp": 150,
                "enunciado": "Qual estrutura condicional e recomendada para verificar multiplas condicoes com valores discretos exatos?",
                "opcoes": ["switch / case", "while", "for in", "try / catch"],
                "gabarito_idx": 0, # switch / case
                "dica": "Essa estrutura avalia uma expressao comparando o resultado com clausulas 'case'."
            }
        ]
    },
    {
        "titulo": "Manipulacao do DOM & Eventos",
        "descricao": "Interacao dinamica com elementos HTML e manipuladores de eventos.",
        "nivel": "INTERMEDIARIO",
        "ordem_modulo": 2,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "Selecao de Elementos com querySelector",
                "descricao": "Como buscar elementos HTML utilizando seletores CSS.",
                "xp": 50,
                "texto": (
                    "### Selecionando Elementos\n\n"
                    "O metodo `document.querySelector` permite selecionar qualquer elemento usando seletores CSS:\n\n"
                    "```javascript\n"
                    "const botao = document.querySelector('.btn-primary');\n"
                    "const titulo = document.querySelector('#titulo-principal');\n"
                    "```"
                )
            },
            {
                "tipo": "QUESTAO",
                "titulo": "Exercicio: Seletores no DOM",
                "descricao": "Identifique o metodo correto para capturar elementos pela classe CSS.",
                "xp": 100,
                "enunciado": "Para selecionar o primeiro elemento que possui a classe 'destaque', qual comando e o mais moderno e recomendado?",
                "opcoes": [
                    "document.querySelector('.destaque')",
                    "document.getElementById('destaque')",
                    "document.selectClass('destaque')",
                    "document.find('.destaque')"
                ],
                "gabarito_idx": 0,
                "dica": "Utilize o metodo padrao que aceita seletores no mesmo formato do CSS com ponto para classe."
            },
            {
                "tipo": "CONTEUDO",
                "titulo": "Escuta de Eventos com addEventListener",
                "descricao": "Como escutar cliques e interacoes do usuario de forma desacoplada.",
                "xp": 50,
                "texto": (
                    "### addEventListener\n\n"
                    "Adicione comportamentos aos elementos sem poluir o HTML inline:\n\n"
                    "```javascript\n"
                    "botao.addEventListener('click', (evento) => {\n"
                    "  console.log('Botao clicado!');\n"
                    "});\n"
                    "```"
                )
            },
            {
                "tipo": "QUESTAO",
                "titulo": "Exercicio: Manipulador de Eventos",
                "descricao": "Fixacao da sintaxe de registro de eventos.",
                "xp": 100,
                "enunciado": "Qual metodo do elemento HTML e utilizado para vincular uma funcao ou callback de clique?",
                "opcoes": [
                    "element.addEventListener('click', callback)",
                    "element.attachEvent('click', callback)",
                    "element.onClick(callback)",
                    "element.bind('click', callback)"
                ],
                "gabarito_idx": 0,
                "dica": "O nome do metodo comeca com 'add' e se refere a um 'EventListener'."
            },
            {
                "tipo": "QUESTAO",
                "titulo": "Desafio do Modulo: Prevenindo Comportamento Padrao",
                "descricao": "Evite o recarregamento padrao em submits de formulario.",
                "xp": 150,
                "enunciado": "Qual metodo do objeto de evento cancela o comportamento nativo de envio de um formulario?",
                "opcoes": [
                    "event.preventDefault()",
                    "event.stopPropagation()",
                    "event.cancel()",
                    "event.stop()"
                ],
                "gabarito_idx": 0,
                "dica": "Pense no termo em ingles para 'prevenir a acao padrao (default)'."
            }
        ]
    },
    {
        "titulo": "Assincronismo & Promises",
        "descricao": "Consumo de APIs REST, Promises e sintaxe async/await.",
        "nivel": "AVANCADO",
        "ordem_modulo": 3,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "O que sao Promises e Estados",
                "descricao": "Pending, Fulfilled e Rejected explicados em detalhes.",
                "xp": 50,
                "texto": (
                    "### Ciclo de Vida de uma Promise\n\n"
                    "Uma Promise representa uma operacao que ainda nao foi concluida, podendo assumir tres estados:\n"
                    "- `pending`: Em processamento.\n"
                    "- `fulfilled`: Concluida com sucesso (resolvida).\n"
                    "- `rejected`: Falhou com erro."
                )
            },
            {
                "tipo": "QUESTAO",
                "titulo": "Exercicio: Estados de Promises",
                "descricao": "Identifique o estado de uma Promise que finalizou com sucesso.",
                "xp": 100,
                "enunciado": "Quando uma operacao assincrona e bem-sucedida, a Promise passa para qual estado?",
                "opcoes": ["fulfilled (resolvida)", "pending (pendente)", "rejected (rejeitada)", "halted (interrompida)"],
                "gabarito_idx": 0,
                "dica": "O termo em ingles 'fulfilled' significa que a promessa foi cumprida."
            },
            {
                "tipo": "CONTEUDO",
                "titulo": "Sintaxe Async / Await",
                "descricao": "Trabalhando com codigo assincrono com aparencia sincronica e legivel.",
                "xp": 50,
                "texto": (
                    "### Async e Await\n\n"
                    "Utilize `await` para aguardar a resolucao de uma Promise dentro de funcoes `async`:\n\n"
                    "```javascript\n"
                    "async function buscarDados() {\n"
                    "  const resposta = await fetch('/api/trilhas/');\n"
                    "  const dados = await resposta.json();\n"
                    "  return dados;\n"
                    "}\n"
                    "```"
                )
            },
            {
                "tipo": "QUESTAO",
                "titulo": "Exercicio: Tratamento de Erros com Async/Await",
                "descricao": "Como capturar excecoes em funcoes assincronas.",
                "xp": 100,
                "enunciado": "Qual bloco e utilizado no JavaScript moderno para capturar erros ao usar await?",
                "opcoes": ["try ... catch", "then ... catch", "if ... else", "onError ... retry"],
                "gabarito_idx": 0,
                "dica": "E o mesmo bloco padrao de captura de excecoes sincronicas da linguagem."
            },
            {
                "tipo": "QUESTAO",
                "titulo": "Desafio do Modulo: Execucao Paralela",
                "descricao": "Dispare multiplas requisicoes simultaneas com seguranca.",
                "xp": 150,
                "enunciado": "Qual metodo estatico da classe Promise executa um conjunto de promises em paralelo e aguarda todas?",
                "opcoes": ["Promise.all()", "Promise.race()", "Promise.any()", "Promise.concat()"],
                "gabarito_idx": 0,
                "dica": "O metodo contem a palavra 'all' pois precisa que todas sejam resolvidas."
            }
        ]
    }
]

# ==========================================
# TRILHA 2: Python para Backend (Backend)
# ==========================================
trilha_py = Trilha.objects.create(
    titulo="Python para Backend",
    descricao="Domine Python do zero ao desenvolvimento de APIs e boas praticas backend.",
    habilidade="Backend",
    ativo=True
)

modulos_py_data = [
    {
        "titulo": "Primeiros Passos em Python",
        "descricao": "Sintaxe basica, tipos de dados, indentacao e funcoes de entrada/saida.",
        "nivel": "INICIANTE",
        "ordem_modulo": 1,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "Filosofia do Python & Indentacao",
                "descricao": "A importancia dos blocos delimitados por espacos e legibilidade.",
                "xp": 50,
                "texto": (
                    "### A Filosofia do Python (PEP 8)\n\n"
                    "Em Python, blocos de codigo nao usam chaves `{ }`, e sim indentacao consistente (4 espacos):\n\n"
                    "```python\n"
                    "if idade >= 18:\n"
                    "    print('Maior de idade')\n"
                    "else:\n"
                    "    print('Menor de idade')\n"
                    "```"
                )
            },
            {
                "tipo": "QUESTAO",
                "titulo": "Exercicio: Saida de Dados",
                "descricao": "Fixacao da funcao basica de impressao no terminal.",
                "xp": 100,
                "enunciado": "Qual funcao nativa do Python e utilizada para exibir informacoes no console?",
                "opcoes": ["print()", "echo()", "console.log()", "System.out.println()"],
                "gabarito_idx": 0,
                "dica": "Funcao simples com o verbo 'imprimir' em ingles."
            },
            {
                "tipo": "CONTEUDO",
                "titulo": "Tipagem Dinamica e Fortemente Tipada",
                "descricao": "Como Python lida com tipos sem conversao automatica silenciosa.",
                "xp": 50,
                "texto": (
                    "### Tipagem em Python\n\n"
                    "Python infere o tipo na atribuicao, mas nao soma numero e texto sem conversao explicita:\n\n"
                    "```python\n"
                    "total = 10 + int('5') # 15\n"
                    "```"
                )
            },
            {
                "tipo": "QUESTAO",
                "titulo": "Exercicio: Conversao de Tipos",
                "descricao": "Conversao explicita de tipos primitivos.",
                "xp": 100,
                "enunciado": "Como converter a string '42' em um numero inteiro?",
                "opcoes": ["int('42')", "Integer.parse('42')", "toInt('42')", "cast<int>('42')"],
                "gabarito_idx": 0,
                "dica": "Utilize a funcao com o nome do tipo primitivo 'int'."
            },
            {
                "tipo": "QUESTAO",
                "titulo": "Desafio do Modulo: Operador Logico",
                "descricao": "Avaliacao de condicionais compostas.",
                "xp": 150,
                "enunciado": "Qual operador logico deve ser utilizado para garantir que DUAS condicoes sejam simultaneamente verdadeiras?",
                "opcoes": ["and", "&&", "both", "&="],
                "gabarito_idx": 0,
                "dica": "Em Python, os operadores logicos sao palavras em ingles por extenso, como 'and' e 'or'."
            }
        ]
    },
    {
        "titulo": "Estruturas de Dados & Funcoes",
        "descricao": "Listas, tuplas, dicionarios, loops e criacao de funcoes reutilizaveis.",
        "nivel": "INTERMEDIARIO",
        "ordem_modulo": 2,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "Listas e Dicionarios em Python",
                "descricao": "Colecoes ordenadas mutaveis e pares de chave/valor.",
                "xp": 50,
                "texto": (
                    "### Dicionarios (dict)\n\n"
                    "Dicionarios armazenam dados em pares chave/valor de forma muito eficiente:\n\n"
                    "```python\n"
                    "usuario = {\n"
                    "    'nome': 'Alice',\n"
                    "    'xp': 1200,\n"
                    "    'ativo': True\n"
                    "}\n"
                    "print(usuario['nome'])\n"
                    "```"
                )
            },
            {
                "tipo": "QUESTAO",
                "titulo": "Exercicio: Acesso a Dicionario Seguro",
                "descricao": "Como evitar KeyError ao acessar chaves opcionais.",
                "xp": 100,
                "enunciado": "Qual metodo de dicionario permite buscar um valor retornando None ou um valor padrao caso a chave nao exista?",
                "opcoes": ["dict.get('chave')", "dict.find('chave')", "dict.search('chave')", "dict.lookup('chave')"],
                "gabarito_idx": 0,
                "dica": "O nome do metodo significa 'obter' em ingles."
            },
            {
                "tipo": "CONTEUDO",
                "titulo": "Definindo Funcoes com def",
                "descricao": "Parametros, retorno e docstrings explicativas.",
                "xp": 50,
                "texto": (
                    "### Declarando Funcoes\n\n"
                    "```python\n"
                    "def calcular_bonus(xp: int, multiplicador: float = 1.1) -> float:\n"
                    "    \"\"\"Calcula a pontuacao de bonus com base no multiplicador.\"\"\"\n"
                    "    return xp * multiplicador\n"
                    "```"
                )
            },
            {
                "tipo": "QUESTAO",
                "titulo": "Exercicio: Parametros Padrao",
                "descricao": "Uso de argumentos com valores default.",
                "xp": 100,
                "enunciado": "O que acontece ao chamar uma funcao omitindo um parametro que possui valor padrao definido?",
                "opcoes": [
                    "A funcao assume automaticamente o valor padrao pre-definido",
                    "Gera erro de TypeError por argumento faltante",
                    "Retorna None obrigatoriamente",
                    "Interrompe o interpretador"
                ],
                "gabarito_idx": 0,
                "dica": "O proposito do parametro default e permitir que o chamador nao precise envia-lo."
            },
            {
                "tipo": "QUESTAO",
                "titulo": "Desafio do Modulo: List Comprehension",
                "descricao": "Construcao elegante e idiomatica de colecoes.",
                "xp": 150,
                "enunciado": "Qual expressao gera uma lista com o dobro dos numeros de [1, 2, 3] usando List Comprehension?",
                "opcoes": [
                    "[x * 2 for x in [1, 2, 3]]",
                    "map(x * 2, [1, 2, 3])",
                    "list(for x in [1, 2, 3]: x * 2)",
                    "[1, 2, 3].map(x => x * 2)"
                ],
                "gabarito_idx": 0,
                "dica": "A sintaxe comeca com a expressao do elemento, seguida por 'for variavel in iteravel'."
            }
        ]
    },
    {
        "titulo": "POO & Manipulacao de Arquivos",
        "descricao": "Classes, heranca, encapsulamento e context managers com with.",
        "nivel": "AVANCADO",
        "ordem_modulo": 3,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "Classes e Metodo __init__",
                "descricao": "O construtor e o parametro self na Programacao Orientada a Objetos.",
                "xp": 50,
                "texto": (
                    "### Classes em Python\n\n"
                    "```python\n"
                    "class Usuario:\n"
                    "    def __init__(self, nome: str, email: str):\n"
                    "        self.nome = nome\n"
                    "        self.email = email\n"
                    "```"
                )
            },
            {
                "tipo": "QUESTAO",
                "titulo": "Exercicio: O Parametro self",
                "descricao": "Papel da referencia a instancia em metodos de classe.",
                "xp": 100,
                "enunciado": "Em metodos de instancia do Python, o que representa o primeiro parametro convencionalmente chamado de self?",
                "opcoes": [
                    "A propria instancia do objeto sendo manipulada",
                    "A classe pai (superclasse)",
                    "O modulo em que a classe esta declarada",
                    "Uma copia imutavel do objeto"
                ],
                "gabarito_idx": 0,
                "dica": "Ele aponta para o proprio objeto criado que esta executando o metodo."
            },
            {
                "tipo": "CONTEUDO",
                "titulo": "Context Managers e o comando with",
                "descricao": "Gerenciamento seguro de recursos como arquivos e conexoes de banco.",
                "xp": 50,
                "texto": (
                    "### Fechamento Automatico com with\n\n"
                    "```python\n"
                    "with open('relatorio.txt', 'r') as arquivo:\n"
                    "    conteudo = arquivo.read()\n"
                    "# O arquivo e fechado automaticamente ao sair do bloco with!\n"
                    "```"
                )
            },
            {
                "tipo": "QUESTAO",
                "titulo": "Exercicio: Context Manager",
                "descricao": "Vantagem do uso de with na leitura/escrita de arquivos.",
                "xp": 100,
                "enunciado": "Qual e o principal beneficio do uso da clausula with ao abrir arquivos?",
                "opcoes": [
                    "Garante o fechamento seguro do arquivo mesmo em caso de excecao",
                    "Aumenta a velocidade do disco em 200%",
                    "Converte automaticamente texto em binario",
                    "Evita a necessidade de permissoes no sistema operacional"
                ],
                "gabarito_idx": 0,
                "dica": "O context manager garante que recursos abertos sejam liberados ao final."
            },
            {
                "tipo": "QUESTAO",
                "titulo": "Desafio do Modulo: Metodos Magicos (Dunder)",
                "descricao": "Representacao legivel de objetos para desenvolvedores.",
                "xp": 150,
                "enunciado": "Qual metodo especial define a representacao em string de um objeto quando chamado por str() ou print()?",
                "opcoes": ["__str__", "__repr__", "__toString__", "__print__"],
                "gabarito_idx": 0,
                "dica": "Metodo magico que comeca e termina com dois underscores com o nome 'str'."
            }
        ]
    }
]

def popular_trilha(trilha, modulos_data):
    for m_data in modulos_data:
        modulo = Modulo.objects.create(
            trilha=trilha,
            titulo=m_data["titulo"],
            descricao=m_data["descricao"],
            nivel=m_data["nivel"],
            ordem_modulo=m_data["ordem_modulo"]
        )
        print(f"  + Modulo: {modulo.titulo} ({modulo.nivel})")
        for idx, ativ_data in enumerate(m_data["atividades"], start=1):
            if ativ_data["tipo"] == "CONTEUDO":
                conteudo = Conteudo.objects.create(
                    titulo=ativ_data["titulo"],
                    texto_explicativo=ativ_data["texto"],
                    tempo_estimado_minutos=5
                )
                atividade = Atividade.objects.create(
                    modulo=modulo,
                    conteudo=conteudo,
                    titulo=ativ_data["titulo"],
                    descricao=ativ_data["descricao"],
                    contexto_avaliacao="FORMATIVA",
                    xp_recompensa=ativ_data["xp"],
                    ordem=idx,
                    ativo=True
                )
                print(f"    - Atividade {idx} (Conteudo): {atividade.titulo}")
            else: # QUESTAO
                atividade = Atividade.objects.create(
                    modulo=modulo,
                    conteudo=None,
                    titulo=ativ_data["titulo"],
                    descricao=ativ_data["descricao"],
                    contexto_avaliacao="FORMATIVA",
                    xp_recompensa=ativ_data["xp"],
                    ordem=idx,
                    ativo=True
                )
                gabarito_idx = ativ_data["gabarito_idx"]
                gabarito_texto = ativ_data["opcoes"][gabarito_idx]
                questao = Questao.objects.create(
                    atividade=atividade,
                    tipo_exercicio="MULTIPLA_ESCOLHA",
                    enunciado=ativ_data["enunciado"],
                    codigo_snippet="",
                    gabarito_esperado="", # Atualizaremos com o ID da opcao apos criacao
                    explicacao=f"A resposta correta e: {gabarito_texto}",
                    dica_conceitual=ativ_data["dica"],
                    ordem_questao=1,
                    peso_pontuacao=ativ_data["xp"]
                )
                # Criar as opcoes
                opcao_correta_id = None
                for op_idx, op_texto in enumerate(ativ_data["opcoes"]):
                    opcao = QuestaoOpcao.objects.create(
                        questao=questao,
                        texto_opcao=op_texto,
                        ordem=op_idx + 1
                    )
                    if op_idx == gabarito_idx:
                        opcao_correta_id = str(opcao.id)
                
                # Salvar o ID da opcao correta no gabarito_esperado
                questao.gabarito_esperado = opcao_correta_id
                questao.save(update_fields=["gabarito_esperado"])
                print(f"    - Atividade {idx} (Questao): {atividade.titulo}")

popular_trilha(trilha_js, modulos_js_data)
popular_trilha(trilha_py, modulos_py_data)

print("\n--- RESUMO DO SEED ---")
print(f"Total Trilhas: {Trilha.objects.count()}")
print(f"Total Modulos: {Modulo.objects.count()}")
print(f"Total Atividades: {Atividade.objects.count()}")
print(f"Total Conteudos: {Conteudo.objects.count()}")
print(f"Total Questoes: {Questao.objects.count()}")
print(f"Total Opcoes: {QuestaoOpcao.objects.count()}")
print("Seed completo com sucesso!")

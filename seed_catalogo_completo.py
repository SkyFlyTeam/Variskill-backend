"""
Script para popular o banco de dados pedagógico com 10 Trilhas, uma para cada interesse
de userManagement/management/commands/seed_interesses.py (o campo habilidade usa o nome
exato do interesse). As 3 Trilhas Python têm 5 Módulos e as demais têm 2 Módulos;
todo Módulo tem exatamente 5 Atividades:
  1. CONTEUDO (Teórico em Markdown)
  2. MULTIPLA_ESCOLHA (Conceitual, 4 opções)
  3. COMPLETE_CODIGO (Sintaxe básica, __BLANK_0__)
  4. ORDENAR_BLOCOS (Algoritmo e estrutura, __SLOT_X__)
  5. COMPLETE_CODIGO (Desafio prático do módulo, __BLANK_0__)

Cada Atividade de exercício (2 a 5) tem uma lista "questoes" com 3 Questoes. Cada
questão declara o próprio "tipo" (MULTIPLA_ESCOLHA, COMPLETE_CODIGO ou ORDENAR_BLOCOS)
e o XP da atividade é dividido entre elas (a soma dos pesos = xp_recompensa).
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings')
django.setup()

from trackManagement.models import Trilha, Modulo, Matricula, ProgressoModulo
from activityManagement.models import Atividade, Conteudo, ExecucaoAtividade
from questionsManagement.models import Questao, QuestaoOpcao

print("Iniciando seed do catalogo completo...")

# Limpar dados anteriores
ExecucaoAtividade.objects.all().delete()
ProgressoModulo.objects.all().delete()
Matricula.objects.all().delete()
QuestaoOpcao.objects.all().delete()
Questao.objects.all().delete()
Atividade.objects.all().delete()
Conteudo.objects.all().delete()
Modulo.objects.all().delete()
Trilha.objects.all().delete()

# ==============================================================================
# TRILHA 1: Python: Fundamentos
# ==============================================================================
trilha_fundamentos = Trilha.objects.create(
    titulo="Python: Fundamentos",
    descricao="Aprenda a sintaxe basica, estruturas de controle, tipos de dados e funcoes essenciais em Python.",
    habilidade="Python",
    ativo=True
)

modulos_fundamentos = [
    {
        "titulo": "Variaveis, Tipos de Dados e Operadores",
        "descricao": "Tipos primitivos (int, float, str, bool), atribuicao dinamica e operadores aritmeticos.",
        "nivel": "INICIANTE",
        "ordem_modulo": 1,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "Tipos Primitivos, Mutabilidade e Atribuicao",
                "descricao": "Entenda a tipagem dinamica e forte do Python, tipos primitivos, mutabilidade e boas praticas da PEP 8.",
                "xp": 50,
                "texto": (
                    "### Variaveis e Tipagem em Python\n\n"
                    "Python e amplamente conhecido por sua sintaxe limpa e expressiva. Duas caracteristicas fundamentais definem como o Python lida com dados:\n\n"
                    "1. **Tipagem Dinamica**: Voce nao precisa declarar o tipo de uma variavel explicitamente. O interpretador infere o tipo em tempo de execucao com base no valor atribuido.\n"
                    "2. **Tipagem Forte**: O interpretador nao realiza conversoes implicitas arriscadas entre tipos incompativeis. Por exemplo, tentar somar um numero inteiro com uma string (`10 + '5'`) gerara um erro `TypeError` imediato, em vez de concatenar silenciosamente.\n\n"
                    "### Tipos Primitivos Fundamentais\n\n"
                    "- **`int`**: Numeros inteiros de precisao arbitraria (ex: `42`, `-7`, `1_000_000`).\n"
                    "- **`float`**: Numeros de ponto flutuante com casas decimais (ex: `3.14159`, `19.90`).\n"
                    "- **`str`**: Sequencias de caracteres de texto imutaveis (ex: `'Python'`, `\"Fatec\"`).\n"
                    "- **`bool`**: Valores booleanos logicos (`True` ou `False`).\n\n"
                    "### Boas Praticas (PEP 8) e Coersao de Tipos\n\n"
                    "- **Nomes de Variaveis**: Utilize nomes descritivos em `snake_case` (ex: `total_pontos`, `preco_unitario`). Evite letras soltas ou caracteres especiais.\n"
                    "- **Type Casting (Conversao)**: Conversoes explicitas devem ser feitas utilizando funcoes construtoras como `int()`, `float()`, `str()` e `bool()`.\n"
                    "- **Identidade vs Igualdade**: Em Python, o operador `==` compara o valor do conteudo, enquanto `is` verifica se dois identificadores apontam para o mesmo endereco de memoria.\n\n"
                    "```python\n"
                    "# 1. Declaracao de tipos primitivos (inferencia automatica)\n"
                    "idade_usuario = 25              # int\n"
                    "preco_produto = 49.90           # float\n"
                    "usuario_ativo = True            # bool\n"
                    "nome_curso = 'Engenharia'       # str\n"
                    "\n"
                    "# 2. Conversao explicita de tipos (Type Casting)\n"
                    "entrada_texto = '150'\n"
                    "quantidade = int(entrada_texto) # Converte '150' para 150 (int)\n"
                    "fator_ajuste = float(quantidade) * 1.05\n"
                    "\n"
                    "# 3. Formatacao moderna de texto com f-strings\n"
                    "resumo = f'Curso: {nome_curso} | Total: R$ {fator_ajuste:.2f}'\n"
                    "print(resumo)\n"
                    "```\n\n"
                    "> **Dica Pro**: Strings e inteiros sao imutaveis em Python. Toda operacao que parece modificar uma string na verdade cria um novo objeto na memoria."
                )
            },
            {
                "tipo": "MULTIPLA_ESCOLHA",
                "titulo": "Exercicio: Tipos Primitivos",
                "descricao": "Identifique a funcao nativa correta para conversao de tipos.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual funcao nativa do Python e utilizada para converter a string '42' em um numero inteiro?",
                        "opcoes": ["int('42')", "Integer.parse('42')", "toInt('42')", "cast<int>('42')"],
                        "gabarito_idx": 0,
                        "dica": "Utilize a funcao nativa cujo nome e exatamente a abreviacao do tipo inteiro."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual e o resultado de type(3.0) em Python?",
                        "opcoes": ["<class 'int'>", "<class 'float'>", "<class 'str'>", "<class 'double'>"],
                        "gabarito_idx": 1,
                        "dica": "Numeros escritos com ponto decimal pertencem ao tipo de ponto flutuante."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "O que acontece ao executar a expressao 10 + '5' em Python?",
                        "opcoes": ["Retorna '105'", "Retorna 15", "Lanca um TypeError", "Retorna None"],
                        "gabarito_idx": 2,
                        "dica": "Lembre-se: Python tem tipagem forte e nao converte tipos incompativeis implicitamente."
                    }
                ]
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Conversao de Tipos",
                "descricao": "Complete a conversao de entrada de dados para float.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a lacuna para converter o valor monetario recebido como texto em numero decimal (float).",
                        "codigo_snippet": (
                            "preco_texto = '19.90'\n"
                            "valor_final = __BLANK_0__(preco_texto)\n"
                            "print(valor_final)"
                        ),
                        "gabarito": "float",
                        "dica": "Use a funcao nativa para numeros de ponto flutuante."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a lacuna para converter a idade (int) em texto e concatena-la a mensagem:",
                        "codigo_snippet": (
                            "idade = 30\n"
                            "mensagem = 'Idade: ' + __BLANK_0__(idade)\n"
                            "print(mensagem)"
                        ),
                        "gabarito": "str",
                        "dica": "Use a funcao construtora do tipo texto."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a funcao nativa que exibe o tipo de uma variavel:",
                        "codigo_snippet": (
                            "valor = 42\n"
                            "print(__BLANK_0__(valor))  # <class 'int'>"
                        ),
                        "gabarito": "type",
                        "dica": "A funcao tem o mesmo nome do conceito que queremos descobrir: o tipo."
                    }
                ]
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Calculo de Media",
                "descricao": "Ordene as instrucoes para calcular e exibir a media aritmetica de duas notas.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as linhas de codigo para declarar as notas, calcular a media e imprimir o resultado:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__"
                        ),
                        "blocos": [
                            "nota1, nota2 = 8.0, 6.0",
                            "media = (nota1 + nota2) / 2",
                            "print(f'Media: {media}')"
                        ],
                        "dica": "Primeiro declare os valores, depois faca a operacao matematica e por fim exiba o resultado."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as linhas para ler o preco em texto, converte-lo, aplicar 10% de desconto e exibir o valor final:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "preco_texto = '80.00'",
                            "preco = float(preco_texto)",
                            "preco_final = preco * 0.9",
                            "print(f'Preco final: {preco_final:.2f}')"
                        ],
                        "dica": "Cada linha depende do valor calculado na linha anterior."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as linhas para converter 3725 segundos em horas e minutos:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "segundos_totais = 3725",
                            "horas = segundos_totais // 3600",
                            "restante = segundos_totais - horas * 3600",
                            "minutos = restante // 60"
                        ],
                        "dica": "Primeiro descubra as horas inteiras; o que sobra vira minutos."
                    }
                ]
            },
            {
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Resto da Divisao",
                "descricao": "Descubra se um numero e par ou impar utilizando o operador adequado.",
                "xp": 150,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o operador aritmetico que calcula o resto da divisao inteira (modulo) para validar paridade:",
                        "codigo_snippet": (
                            "numero = 14\n"
                            "resto = numero __BLANK_0__ 2\n"
                            "eh_par = (resto == 0)"
                        ),
                        "gabarito": "%",
                        "dica": "O operador de resto da divisao em Python e representado pelo caractere de porcentagem."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o operador que calcula quantos grupos completos de 5 alunos podem ser formados (divisao inteira):",
                        "codigo_snippet": (
                            "total_alunos = 47\n"
                            "grupos = total_alunos __BLANK_0__ 5\n"
                            "print(grupos)  # 9"
                        ),
                        "gabarito": "//",
                        "dica": "E o operador de divisao que descarta a parte decimal."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o operador de potenciacao para calcular a area de um quadrado:",
                        "codigo_snippet": (
                            "lado = 4\n"
                            "area = lado __BLANK_0__ 2\n"
                            "print(area)  # 16"
                        ),
                        "gabarito": "**",
                        "dica": "Em Python, a potencia usa dois asteriscos."
                    }
                ]
            }
        ]
    },
    {
        "titulo": "Controle de Fluxo e Condicionais",
        "descricao": "Tomada de decisao com if, elif, else e operadores logicos (and, or, not).",
        "nivel": "INICIANTE",
        "ordem_modulo": 2,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "Estruturas Condicionais, Logica Booleana e PEP 8",
                "descricao": "Como estruturar decisoes complexas com if, elif, else, avaliacao de curto-circuito e expressoes ternarias.",
                "xp": 50,
                "texto": (
                    "### Tomada de Decisao e Estruturas Condicionais\n\n"
                    "O fluxo de execucao de um programa e guiado por decisoes condicionais. Em Python, a sintaxe dispensa o uso de chaves `{}` ou palavras como `then`: os blocos de codigo sao definidos exclusivamente pela **indentacao obrigatoria de 4 espacos** (regra central da PEP 8) e pelo terminador de clausula `:`.\n\n"
                    "### Valores Verdadeiros e Falsos (Truthy e Falsy)\n\n"
                    "Em Python, qualquer objeto pode ser testado em uma condicao booleana sem necessidade de comparacao explicita com `True` ou `False`:\n"
                    "- **Valores Falsy**: `0`, `0.0`, `''` (string vazia), `[]` (lista vazia), `{}` (dicionario vazio), `None` e `False`.\n"
                    "- **Valores Truthy**: Qualquer numero diferente de zero, strings com conteudo e colecoes preenchidas.\n\n"
                    "### Operadores Logicos e Curto-Circuito (Short-Circuit)\n\n"
                    "- **`and`**: Retorna verdadeiro apenas se ambos os operandos forem verdadeiros. Caso o primeiro seja falso, o segundo operando sequer e avaliado (otimizacao por curto-circuito).\n"
                    "- **`or`**: Retorna verdadeiro se pelo menos um dos operandos for verdadeiro.\n"
                    "- **`not`**: Inverte o valor logico booleano do operando.\n"
                    "- **Operador Ternario**: Permite atribuicoes concisas em uma unica linha: `resultado = valor_se_verdade if condicao else valor_se_falso`.\n\n"
                    "```python\n"
                    "# 1. Tomada de decisao com if, elif e else\n"
                    "pontuacao = 85\n"
                    "\n"
                    "if pontuacao >= 90:\n"
                    "    conceito = 'A - Excelente'\n"
                    "elif pontuacao >= 75:\n"
                    "    conceito = 'B - Muito Bom'\n"
                    "elif pontuacao >= 60:\n"
                    "    conceito = 'C - Regular'\n"
                    "else:\n"
                    "    conceito = 'D - Insuficiente'\n"
                    "\n"
                    "# 2. Aproveitando valores Truthy/Falsy de forma pythonica\n"
                    "carrinho_compras = ['Notebook', 'Mouse']\n"
                    "if carrinho_compras:  # Mais elegante que len(carrinho_compras) > 0\n"
                    "    print(f'Itens a processar: {len(carrinho_compras)}')\n"
                    "\n"
                    "# 3. Expressao condicional ternaria\n"
                    "idade = 19\n"
                    "status_eleitor = 'Obrigatorio' if 18 <= idade <= 70 else 'Facultativo'\n"
                    "print(f'Status de Votacao: {status_eleitor}')\n"
                    "```\n\n"
                    "> **Boa Pratica PEP 8**: Evite comparar booleanos explicitamente com `== True`. Prefira `if usuario_ativo:` em vez de `if usuario_ativo == True:`."
                )
            },
            {
                "tipo": "MULTIPLA_ESCOLHA",
                "titulo": "Exercicio: Operadores Logicos",
                "descricao": "Avalie o operador logico que exige que ambas as condicoes sejam verdadeiras.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual operador logico deve ser utilizado quando precisamos que duas condicoes sejam simultaneamente verdadeiras?",
                        "opcoes": ["and", "&&", "both", "all"],
                        "gabarito_idx": 0,
                        "dica": "Em Python usamos a palavra em ingles 'and', e nao simbolos como '&&'."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual e o valor da expressao not (True and False)?",
                        "opcoes": ["False", "None", "True", "Erro de sintaxe"],
                        "gabarito_idx": 2,
                        "dica": "Resolva primeiro o que esta entre parenteses e depois aplique a negacao."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Em Python, o que define quais instrucoes pertencem ao bloco de um if?",
                        "opcoes": [
                            "Chaves { }",
                            "A indentacao (recuo) das linhas",
                            "A palavra-chave end",
                            "Parenteses ao redor do bloco"
                        ],
                        "gabarito_idx": 1,
                        "dica": "Python nao usa chaves para delimitar blocos."
                    }
                ]
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Condicional Intermediaria",
                "descricao": "Complete a clausula intermediaria entre o if e o else.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a palavra-chave utilizada em Python para testar uma condicao alternativa caso o primeiro if falhe:",
                        "codigo_snippet": (
                            "nota = 6.5\n"
                            "if nota >= 7.0:\n"
                            "    resultado = 'Aprovado'\n"
                            "__BLANK_0__ nota >= 5.0:\n"
                            "    resultado = 'Recuperacao'\n"
                            "else:\n"
                            "    resultado = 'Reprovado'"
                        ),
                        "gabarito": "elif",
                        "dica": "Juncao de 'else' com 'if' tipica do Python."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a palavra-chave executada quando nenhuma condicao anterior for verdadeira:",
                        "codigo_snippet": (
                            "idade = 15\n"
                            "if idade >= 18:\n"
                            "    print('Voto obrigatorio')\n"
                            "__BLANK_0__:\n"
                            "    print('Voto nao obrigatorio')"
                        ),
                        "gabarito": "else",
                        "dica": "E o bloco 'caso contrario', que nao recebe condicao."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o operador logico para que a mensagem apareca se for sabado OU domingo:",
                        "codigo_snippet": (
                            "dia = 'sabado'\n"
                            "if dia == 'sabado' __BLANK_0__ dia == 'domingo':\n"
                            "    print('Fim de semana!')"
                        ),
                        "gabarito": "or",
                        "dica": "Basta que uma das condicoes seja verdadeira."
                    }
                ]
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Validacao de Acesso",
                "descricao": "Ordene a checagem de permissao de usuario ativo e autenticado.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Ordene o bloco condicional para validar se o usuario tem acesso ao painel:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "    __SLOT_1__\n"
                            "__SLOT_2__\n"
                            "    __SLOT_3__"
                        ),
                        "blocos": [
                            "if usuario_logado and perfil_admin:",
                            "liberar_acesso_total()",
                            "else:",
                            "redirecionar_login()"
                        ],
                        "dica": "Primeiro a checagem if, em seguida sua acao indentada, depois o else e o redirecionamento."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize a estrutura condicional que classifica a temperatura em Calor (>= 30), Agradavel (>= 18) ou Frio:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "    __SLOT_1__\n"
                            "__SLOT_2__\n"
                            "    __SLOT_3__\n"
                            "__SLOT_4__\n"
                            "    __SLOT_5__"
                        ),
                        "blocos": [
                            "if temperatura >= 30:",
                            "print('Calor')",
                            "elif temperatura >= 18:",
                            "print('Agradavel')",
                            "else:",
                            "print('Frio')"
                        ],
                        "dica": "Teste primeiro a condicao mais restritiva; o else sempre fica por ultimo."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize o codigo que le um numero e informa se ele e par ou impar:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "    __SLOT_2__\n"
                            "__SLOT_3__\n"
                            "    __SLOT_4__"
                        ),
                        "blocos": [
                            "numero = int(input('Digite um numero: '))",
                            "if numero % 2 == 0:",
                            "print('Par')",
                            "else:",
                            "print('Impar')"
                        ],
                        "dica": "A variavel precisa existir antes de ser testada."
                    }
                ]
            },
            {
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Negacao Logica",
                "descricao": "Aplique o operador de inversao de valor booleano.",
                "xp": 150,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a lacuna com a palavra-chave que inverte o valor logico da expressao:",
                        "codigo_snippet": (
                            "bloqueado = False\n"
                            "if __BLANK_0__ bloqueado:\n"
                            "    print('Usuario liberado')"
                        ),
                        "gabarito": "not",
                        "dica": "Palavra em ingles para negacao logica."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o operador que verifica se um item pertence a lista de permissoes:",
                        "codigo_snippet": (
                            "permissoes = ['ler', 'editar']\n"
                            "if 'editar' __BLANK_0__ permissoes:\n"
                            "    print('Pode editar')"
                        ),
                        "gabarito": "in",
                        "dica": "E o operador de pertencimento do Python."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o operador de comparacao que detecta quando as senhas NAO sao iguais:",
                        "codigo_snippet": (
                            "senha = 'abc123'\n"
                            "confirmacao = 'abc124'\n"
                            "if senha __BLANK_0__ confirmacao:\n"
                            "    print('As senhas nao conferem')"
                        ),
                        "gabarito": "!=",
                        "dica": "E o oposto do operador ==."
                    }
                ]
            }
        ]
    },
    {
        "titulo": "Estruturas de Repeticao (For e While)",
        "descricao": "Iteracao com o laco for, funcao range() e controle com while, break e continue.",
        "nivel": "INICIANTE",
        "ordem_modulo": 3,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "Lacos de Repeticao, Intervalos e Controle de Fluxo",
                "descricao": "Dominando a iteracao com for, geracao de sequencias com range, repeticao condicional com while, break, continue e for-else.",
                "xp": 50,
                "texto": (
                    "### Dominando Lacos de Repeticao em Python\n\n"
                    "Lacos de repeticao automatizam tarefas repetitivas. Em Python, a iteracao e orientada a objetos: o comando `for` itera diretamente sobre os elementos de qualquer objeto iteravel (listas, strings, tuplas, dicionarios e geradores).\n\n"
                    "### A Funcao Nativa `range()`\n\n"
                    "Para repetir acoes um numero fixo de vezes ou percorrer indices numericos, utilizamos a funcao `range(start, stop, step)`:\n"
                    "- `start` (opcional, padrao 0): Inicio do intervalo inclusivo.\n"
                    "- `stop` (obrigatorio): Limite final **exclusivo** (o valor informado nao entra no laco).\n"
                    "- `step` (opcional, padrao 1): Incremento ou decremento a cada passo.\n\n"
                    "### Repeticao Baseada em Condicao: `while`\n\n"
                    "O laco `while` continua sua execucao enquanto a expressao condicional for verdadeira. E ideal quando o numero exato de repeticoes nao e conhecido previamente (ex: ler linhas de um arquivo ate o fim ou aguardar resposta de rede).\n\n"
                    "### Controle Avancado: `break`, `continue` e Clausula `else`\n\n"
                    "- **`break`**: Interrompe imediatamente o laco mais interno e passa o controle para a instrucao seguinte.\n"
                    "- **`continue`**: Pula o restante do corpo do loop na iteracao atual e avanca para o proximo ciclo.\n"
                    "- **`for ... else` / `while ... else`**: O bloco `else` associado a um laco so e executado se o laco terminar normalmente (ou seja, se **nao** foi interrompido por um `break`).\n\n"
                    "```python\n"
                    "# 1. Iterando com range(start, stop, step)\n"
                    "for numero in range(2, 11, 2):  # Pares de 2 a 10\n"
                    "    print(f'Par encontrado: {numero}')\n"
                    "\n"
                    "# 2. Iteracao sobre colecao com indice usando enumerate()\n"
                    "linguagens = ['Python', 'SQL', 'FastAPI']\n"
                    "for rank, lang in enumerate(linguagens, start=1):\n"
                    "    print(f'{rank}. {lang}')\n"
                    "\n"
                    "# 3. Busca com flag via clausula 'for ... else'\n"
                    "alvo = 'FastAPI'\n"
                    "for lang in linguagens:\n"
                    "    if lang == alvo:\n"
                    "        print(f'Tecnologia {alvo} localizada!')\n"
                    "        break\n"
                    "else:\n"
                    "    print(f'{alvo} nao encontrada na lista.')\n"
                    "```\n\n"
                    "> **Dica Pro**: Prefira sempre iterar diretamente sobre os itens com `for item in colecao:` em vez de indexar manualmente com `for i in range(len(colecao)):`."
                )
            },
            {
                "tipo": "MULTIPLA_ESCOLHA",
                "titulo": "Exercicio: Controle de Laco",
                "descricao": "Comando para interromper imediatamente a execucao de um loop.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual palavra-chave e utilizada para encerrar imediatamente a execucao de um laco for ou while?",
                        "opcoes": ["break", "stop", "exit", "terminate"],
                        "gabarito_idx": 0,
                        "dica": "Comando classico em linguagens de programacao que significa 'quebrar' o loop."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Quantas vezes o corpo do laco for i in range(2, 8, 2) e executado?",
                        "opcoes": ["4", "3", "6", "2"],
                        "gabarito_idx": 1,
                        "dica": "Liste os valores gerados: comeca em 2, soma 2 a cada passo e para antes de 8."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual cenario e mais adequado para o uso do laco while?",
                        "opcoes": [
                            "Percorrer todos os itens de uma lista conhecida",
                            "Declarar funcoes anonimas",
                            "Importar modulos externos",
                            "Repetir enquanto uma condicao for verdadeira, sem saber quantas iteracoes serao necessarias"
                        ],
                        "gabarito_idx": 3,
                        "dica": "O while e controlado por uma condicao, nao por uma colecao."
                    }
                ]
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Gerador de Intervalos",
                "descricao": "Preencha a funcao nativa que gera sequencias numericas.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Complete a lacuna com a funcao nativa que gera a sequencia de 1 a 10 (excluindo 11):",
                        "codigo_snippet": (
                            "soma = 0\n"
                            "for valor in __BLANK_0__(1, 11):\n"
                            "    soma += valor"
                        ),
                        "gabarito": "range",
                        "dica": "Funcao nativa com o significado de 'alcance' ou 'intervalo'."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a funcao nativa que entrega o indice e o valor de cada item durante o laco:",
                        "codigo_snippet": (
                            "frutas = ['maca', 'uva', 'pera']\n"
                            "for indice, fruta in __BLANK_0__(frutas):\n"
                            "    print(indice, fruta)"
                        ),
                        "gabarito": "enumerate",
                        "dica": "O nome da funcao lembra 'enumerar' os itens."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a palavra-chave do laco que repete enquanto ainda houver tentativas:",
                        "codigo_snippet": (
                            "tentativas = 3\n"
                            "__BLANK_0__ tentativas > 0:\n"
                            "    print(f'Restam {tentativas} tentativas')\n"
                            "    tentativas -= 1"
                        ),
                        "gabarito": "while",
                        "dica": "E o laco controlado por condicao."
                    }
                ]
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Contador com While",
                "descricao": "Ordene a inicializacao e o incremento de uma variavel em loop.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize o loop while para imprimir os numeros de 0 ate 2:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "    __SLOT_2__\n"
                            "    __SLOT_3__"
                        ),
                        "blocos": [
                            "i = 0",
                            "while i < 3:",
                            "print(i)",
                            "i += 1"
                        ],
                        "dica": "Inicialize a variavel antes do loop e incremente dentro do corpo do while."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize o codigo para imprimir 5, 4, 3, 2, 1 e, ao final, a mensagem 'Fim!':",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "    __SLOT_2__\n"
                            "    __SLOT_3__\n"
                            "__SLOT_4__"
                        ),
                        "blocos": [
                            "contador = 5",
                            "while contador > 0:",
                            "print(contador)",
                            "contador -= 1",
                            "print('Fim!')"
                        ],
                        "dica": "Imprima o valor antes de decrementa-lo; a mensagem final fica fora do laco."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize o laco que percorre a lista e para ao encontrar o primeiro numero negativo:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "    __SLOT_1__\n"
                            "        __SLOT_2__\n"
                            "    __SLOT_3__"
                        ),
                        "blocos": ["for valor in [4, 7, -2, 9]:", "if valor < 0:", "break", "print(valor)"],
                        "dica": "A verificacao de parada deve acontecer antes de imprimir o valor."
                    }
                ]
            },
            {
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Pular Iteracao",
                "descricao": "Pule para a proxima iteracao sem executar o restante do corpo do loop.",
                "xp": 150,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a palavra-chave que ignora a iteracao atual quando o numero for par e continua o loop:",
                        "codigo_snippet": (
                            "for num in range(10):\n"
                            "    if num % 2 == 0:\n"
                            "        __BLANK_0__\n"
                            "    print(num)"
                        ),
                        "gabarito": "continue",
                        "dica": "Palavra em ingles que diz ao loop para prosseguir para o proximo ciclo."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o passo do range para imprimir 10, 8, 6, 4, 2:",
                        "codigo_snippet": (
                            "for n in range(10, 0, __BLANK_0__):\n"
                            "    print(n)"
                        ),
                        "gabarito": "-2",
                        "dica": "Um passo negativo faz o range contar de tras para frente."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a palavra-chave que completa a sintaxe do laco for:",
                        "codigo_snippet": (
                            "for letra __BLANK_0__ 'Python':\n"
                            "    print(letra)"
                        ),
                        "gabarito": "in",
                        "dica": "O for percorre cada item 'dentro' do iteravel."
                    }
                ]
            }
        ]
    },
    {
        "titulo": "Colecoes de Dados (Listas, Tuplas e Dicionarios)",
        "descricao": "Manipulacao de listas, mutabilidade, tuplas e dicionarios com mapeamento chave-valor.",
        "nivel": "INICIANTE",
        "ordem_modulo": 4,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "Colecoes de Dados: Listas, Tuplas, Dicionarios e Sets",
                "descricao": "Estruturas de dados fundamentais em Python, mutabilidade, complexidade de busca e list comprehensions.",
                "xp": 50,
                "texto": (
                    "### Estruturas de Dados Essenciais no Python\n\n"
                    "O dominio das colecoes nativas e o coracao do desenvolvimento eficiente em Python. Cada estrutura possui caracteristicas proprias de mutabilidade e desempenho:\n\n"
                    "1. **Listas (`list` - `[]`)**: Sequencias ordenadas e **mutaveis**. Permitem adicionar, remover e reordenar elementos a qualquer momento. Ideais para colecoes homogeneas ou ordenadas.\n"
                    "2. **Tuplas (`tuple` - `()`)**: Sequencias ordenadas e **imutaveis**. Uma vez criadas, seus elementos nao podem ser alterados, o que garante integridade referencial e menor consumo de memoria.\n"
                    "3. **Dicionarios (`dict` - `{}`)**: Mapeamentos associativos de pares **chave-valor**. Implementados internamente via Hash Tables, garantem tempo de busca medio instantaneo `O(1)` por chave.\n"
                    "4. **Conjuntos (`set` - `set()` ou `{elem}`)**: Colecoes nao ordenadas de itens unicos, com suporte a operacoes matematicas de uniao, intersecao e diferenca.\n\n"
                    "### Metodos Defensivos e List Comprehensions\n\n"
                    "- **Acesso Seguro em Dicionarios**: O metodo `dicionario.get(chave, valor_padrao)` evita excecoes `KeyError` quando uma chave nao existe.\n"
                    "- **List Comprehension**: Sintaxe elegante e veloz para criar novas listas a partir de iteraveis: `[expressao for item in colecao if condicao]`.\n\n"
                    "```python\n"
                    "# 1. Manipulacao de Listas\n"
                    "linguagens = ['Python', 'SQL', 'JavaScript']\n"
                    "linguagens.append('TypeScript')   # Insere no final\n"
                    "linguagens.sort()                 # Ordena in-place alfabeticamente\n"
                    "\n"
                    "# 2. Dicionarios com acesso defensivo (.get)\n"
                    "desenvolvedor = {'nome': 'Guilherme', 'nivel': 'Pleno'}\n"
                    "cargo = desenvolvedor.get('cargo', 'Engenheiro de Software') # Valor default\n"
                    "print(f'{desenvolvedor[\"nome\"]} atua como {cargo}')\n"
                    "\n"
                    "# 3. List Comprehension com filtragem\n"
                    "numeros = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]\n"
                    "pares_ao_quadrado = [n ** 2 for n in numeros if n % 2 == 0]\n"
                    "print(f'Quadrados pares: {pares_ao_quadrado}')\n"
                    "```\n\n"
                    "> **Dica Pro**: Usar `chave in meu_dict` ou `item in meu_set` e infinitamente mais rapido (`O(1)`) do que `item in minha_lista` (`O(n)`) para verificar a existencia de dados."
                )
            },
            {
                "tipo": "MULTIPLA_ESCOLHA",
                "titulo": "Exercicio: Insercao em Listas",
                "descricao": "Metodo para adicionar um elemento ao final de uma lista.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual metodo de lista adiciona um novo item ao final da colecao?",
                        "opcoes": ["append()", "push()", "add()", "insertLast()"],
                        "gabarito_idx": 0,
                        "dica": "No Python o termo utilizado e 'append', ao contrario de linguagens que usam 'push'."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual estrutura de dados nativa do Python e imutavel?",
                        "opcoes": ["list", "dict", "set", "tuple"],
                        "gabarito_idx": 3,
                        "dica": "E a estrutura declarada com parenteses."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "O que a expressao {1, 2, 2, 3} produz em Python?",
                        "opcoes": [
                            "Uma lista com 4 elementos",
                            "Um set com 3 elementos: {1, 2, 3}",
                            "Um dicionario",
                            "Um erro por valores duplicados"
                        ],
                        "gabarito_idx": 1,
                        "dica": "Chaves sem pares chave:valor criam um conjunto, que nao aceita duplicados."
                    }
                ]
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Busca Segura em Dicionarios",
                "descricao": "Utilize o metodo que nao dispara KeyError caso a chave nao exista.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Complete a lacuna com o metodo de dicionario que busca uma chave com retorno padrao seguro:",
                        "codigo_snippet": (
                            "perfil = {'nome': 'Guilherme'}\n"
                            "cargo = perfil.__BLANK_0__('cargo', 'Estudante')\n"
                            "print(cargo)"
                        ),
                        "gabarito": "get",
                        "dica": "Metodo de tres letras que significa 'obter'."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o metodo que devolve os pares (chave, valor) do dicionario:",
                        "codigo_snippet": (
                            "precos = {'cafe': 5.0, 'pao': 1.5}\n"
                            "for produto, valor in precos.__BLANK_0__():\n"
                            "    print(produto, valor)"
                        ),
                        "gabarito": "items",
                        "dica": "O metodo retorna os 'itens' do dicionario."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o indice que acessa o ultimo elemento da lista:",
                        "codigo_snippet": (
                            "numeros = [10, 20, 30, 40, 50]\n"
                            "ultimo = numeros[__BLANK_0__]\n"
                            "print(ultimo)  # 50"
                        ),
                        "gabarito": "-1",
                        "dica": "Indices negativos contam a partir do final da lista."
                    }
                ]
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Filtragem com List Comprehension",
                "descricao": "Ordene a criacao de uma nova lista contendo apenas numeros pares.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Ordene a expressao de list comprehension para dobrar apenas numeros pares:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__"
                        ),
                        "blocos": [
                            "numeros = [1, 2, 3, 4, 5, 6]",
                            "pares_dobrados = [x * 2 for x in numeros if x % 2 == 0]",
                            "print(pares_dobrados)"
                        ],
                        "dica": "Declare a lista inicial, aplique a list comprehension e imprima."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as linhas para criar o estoque, cadastrar 10 canetas, vender 3 e exibir o saldo:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "estoque = {}",
                            "estoque['caneta'] = 10",
                            "estoque['caneta'] -= 3",
                            "print(estoque['caneta'])  # 7"
                        ],
                        "dica": "A chave precisa existir antes de ser decrementada."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as linhas para que a variavel ultima receba a string 'revisar':",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "tarefas = ['estudar']",
                            "tarefas.append('revisar')",
                            "ultima = tarefas.pop()",
                            "print(ultima)  # revisar"
                        ],
                        "dica": "pop() sem argumentos remove o ultimo item adicionado."
                    }
                ]
            },
            {
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Tamanho de Colecoes",
                "descricao": "Obtenha a quantidade total de itens de qualquer sequencia.",
                "xp": 150,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a funcao nativa que retorna o numero de elementos de uma lista:",
                        "codigo_snippet": (
                            "linguagens = ['Python', 'SQL', 'FastAPI']\n"
                            "total = __BLANK_0__(linguagens)\n"
                            "print(f'Total: {total}')"
                        ),
                        "gabarito": "len",
                        "dica": "Abreviacao de 'length' (comprimento/tamanho)."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a funcao nativa que retorna uma NOVA lista ordenada, sem alterar a original:",
                        "codigo_snippet": (
                            "notas = [7, 3, 9, 5]\n"
                            "ordenadas = __BLANK_0__(notas)\n"
                            "print(ordenadas)  # [3, 5, 7, 9]"
                        ),
                        "gabarito": "sorted",
                        "dica": "Diferente do metodo .sort(), esta funcao devolve uma copia ordenada."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a funcao que remove e-mails duplicados convertendo a lista em conjunto:",
                        "codigo_snippet": (
                            "emails = ['a@x.com', 'b@x.com', 'a@x.com']\n"
                            "unicos = __BLANK_0__(emails)\n"
                            "print(len(unicos))  # 2"
                        ),
                        "gabarito": "set",
                        "dica": "Conjuntos guardam apenas valores unicos."
                    }
                ]
            }
        ]
    },
    {
        "titulo": "Funcoes, Parametros e Escopo",
        "descricao": "Definicao com def, argumentos posicionais, nomeados, valores padrao e retorno.",
        "nivel": "INICIANTE",
        "ordem_modulo": 5,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "Funcoes, Parametros, *args, **kwargs e Escopo",
                "descricao": "Como modularizar codigo com def, docstrings, parametros posicionais, nomeados e armadilhas de mutabilidade.",
                "xp": 50,
                "texto": (
                    "### Modularizacao e Funcoes em Python\n\n"
                    "Funcoes sao blocos de construcao essenciais para reaproveitamento de codigo, clareza e manutencao. Sao declaradas com a palavra reservada `def` seguida do nome e dos parenteses com os parametros.\n\n"
                    "### Parametros Posicionais, Nomeados e Default\n\n"
                    "- **Valores Padrao (Default)**: Voce pode definir valores default para parametros. Chamadores podem omitir esses argumentos.\n"
                    "- **Argumentos Arbitrarios (`*args` e `**kwargs`)**:\n"
                    "  - `*args`: Empacota multiplos argumentos posicionais em uma **tupla**.\n"
                    "  - `**kwargs`: Empacota multiplos argumentos nomeados em um **dicionario**.\n\n"
                    "### A Grande Armadilha: Argumentos Default Mutaveis\n\n"
                    "Em Python, argumentos default sao avaliados **uma unica vez** quando a funcao e definida, e nao a cada chamada! Se voce usar uma lista ou dicionario mutavel como default (`def fn(x=[])`), a mesma lista sera compartilhada entre todas as chamadas futuras. A solucao correta e usar `None` como padrao.\n\n"
                    "```python\n"
                    "# 1. Definicao com docstrings e Type Hints (PEP 484)\n"
                    "def calcular_desconto(preco: float, percentual: float = 0.1) -> float:\n"
                    "    \"\"\"Calcula o preco final apos aplicar o percentual de desconto.\"\"\"\n"
                    "    return preco * (1 - percentual)\n"
                    "\n"
                    "# 2. Funcao flexivel com *args e **kwargs\n"
                    "def registrar_evento(evento: str, *tags, **detalhes):\n"
                    "    print(f'Evento: {evento} | Tags: {tags}')\n"
                    "    for chave, valor in detalhes.items():\n"
                    "        print(f'  -> {chave}: {valor}')\n"
                    "\n"
                    "# Chamando a funcao flexivel\n"
                    "registrar_evento('login_sucesso', 'auth', 'seguranca', usuario='guilherme', ip='192.168.1.1')\n"
                    "\n"
                    "# 3. Padrao defensivo para defaults mutaveis\n"
                    "def adicionar_tarefa(tarefa: str, lista=None):\n"
                    "    if lista is None:\n"
                    "        lista = []  # Nova lista para cada chamada\n"
                    "    lista.append(tarefa)\n"
                    "    return lista\n"
                    "```\n\n"
                    "> **Dica Pro**: Se uma funcao nao contiver uma declaracao `return` explicita, ou apenas `return` sem argumentos, ela retornara implicitamente o objeto `None`."
                )
            },
            {
                "tipo": "MULTIPLA_ESCOLHA",
                "titulo": "Exercicio: Declaracao de Funcoes",
                "descricao": "Palavra-chave nativa para definicao de funcoes.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual palavra-chave e utilizada em Python para declarar uma funcao?",
                        "opcoes": ["def", "function", "fn", "fun"],
                        "gabarito_idx": 0,
                        "dica": "Abreviacao de 'define' com 3 letras."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "O que uma funcao Python retorna quando nao possui a instrucao return?",
                        "opcoes": ["0", "None", "False", "Uma string vazia"],
                        "gabarito_idx": 1,
                        "dica": "Python devolve automaticamente o valor que representa 'ausencia de valor'."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Na assinatura def registrar(*args, **kwargs), o que o parametro kwargs recebe?",
                        "opcoes": [
                            "Uma tupla com argumentos posicionais",
                            "Uma lista de strings",
                            "Um dicionario com os argumentos nomeados",
                            "O numero total de argumentos"
                        ],
                        "gabarito_idx": 2,
                        "dica": "Dois asteriscos agrupam argumentos do tipo chave=valor."
                    }
                ]
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Retorno de Valores",
                "descricao": "Preencha a instrucao que devolve o resultado calculado para quem chamou a funcao.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Complete a instrucao que retorna o valor calculado na funcao:",
                        "codigo_snippet": (
                            "def calcular_imposto(valor, taxa=0.1):\n"
                            "    total_imposto = valor * taxa\n"
                            "    __BLANK_0__ total_imposto"
                        ),
                        "gabarito": "return",
                        "dica": "Palavra-chave em ingles para retornar."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o simbolo que permite a funcao receber uma quantidade variavel de argumentos posicionais:",
                        "codigo_snippet": (
                            "def somar_todos(__BLANK_0__numeros):\n"
                            "    return sum(numeros)\n"
                            "\n"
                            "print(somar_todos(1, 2, 3))  # 6"
                        ),
                        "gabarito": "*",
                        "dica": "Um unico asterisco agrupa os argumentos posicionais em uma tupla."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o nome do argumento nomeado para criar o usuario inativo:",
                        "codigo_snippet": (
                            "def criar_usuario(nome, ativo=True):\n"
                            "    return {'nome': nome, 'ativo': ativo}\n"
                            "\n"
                            "usuario = criar_usuario('Leo', __BLANK_0__=False)"
                        ),
                        "gabarito": "ativo",
                        "dica": "Use exatamente o nome do parametro declarado na funcao."
                    }
                ]
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Funcao Completa",
                "descricao": "Ordene a definicao, o calculo e a chamada de uma funcao que calcula a area de retangulos.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize a definicao e o consumo da funcao de calculo de area:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "    __SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "def calcular_area(largura, altura):",
                            "return largura * altura",
                            "area = calcular_area(5, 4)",
                            "print(f'Area: {area}')"
                        ],
                        "dica": "Primeiro declare a assinatura da funcao, depois seu retorno indentado, seguida da chamada e exibicao."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize a funcao que usa None como padrao seguro para a lista mutavel:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "    __SLOT_1__\n"
                            "        __SLOT_2__\n"
                            "    __SLOT_3__\n"
                            "    __SLOT_4__"
                        ),
                        "blocos": [
                            "def adicionar_tarefa(tarefa, lista=None):",
                            "if lista is None:",
                            "lista = []",
                            "lista.append(tarefa)",
                            "return lista"
                        ],
                        "dica": "Crie a lista nova apenas quando nenhuma for informada; o return encerra a funcao."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as linhas para ordenar os alunos pela nota usando uma funcao lambda:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__"
                        ),
                        "blocos": [
                            "alunos = [('Ana', 9), ('Rui', 7)]",
                            "ordenados = sorted(alunos, key=lambda a: a[1])",
                            "print(ordenados[0][0])  # Rui"
                        ],
                        "dica": "O parametro key recebe a funcao que extrai o criterio de ordenacao."
                    }
                ]
            },
            {
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Funcoes Lambda",
                "descricao": "Utilize a expressao anonima de uma unica linha.",
                "xp": 150,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a palavra reservada para criar uma pequena funcao anonima em Python:",
                        "codigo_snippet": (
                            "dobro = __BLANK_0__ x: x * 2\n"
                            "print(dobro(5))"
                        ),
                        "gabarito": "lambda",
                        "dica": "Nome de letra grega que denomina funcoes anonimas em programacao funcional."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a funcao nativa que aplica a lambda a cada preco da lista:",
                        "codigo_snippet": (
                            "precos = [10, 20, 30]\n"
                            "com_taxa = list(__BLANK_0__(lambda p: p * 1.1, precos))"
                        ),
                        "gabarito": "map",
                        "dica": "Essa funcao 'mapeia' cada elemento para um novo valor."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a funcao nativa que mantem apenas as idades que satisfazem a condicao:",
                        "codigo_snippet": (
                            "idades = [12, 18, 25, 15]\n"
                            "adultos = list(__BLANK_0__(lambda i: i >= 18, idades))\n"
                            "print(adultos)  # [18, 25]"
                        ),
                        "gabarito": "filter",
                        "dica": "Essa funcao 'filtra' os elementos pela condicao da lambda."
                    }
                ]
            }
        ]
    }
]

# ==============================================================================
# TRILHA 2: Python: Desenvolvimento Web
# ==============================================================================
trilha_web = Trilha.objects.create(
    titulo="Python: Desenvolvimento Web",
    descricao="Construa APIs modernas de alta performance com FastAPI, Pydantic, SQLAlchemy e autenticacao JWT.",
    habilidade="Backend",
    ativo=True
)

modulos_web = [
    {
        "titulo": "Fundamentos da Web, Protocolo HTTP e APIs",
        "descricao": "Metodos HTTP (GET, POST, PUT, DELETE), codigos de status e arquitetura RESTful.",
        "nivel": "INTERMEDIARIO",
        "ordem_modulo": 1,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "O Protocolo HTTP, Arquitetura RESTful e Status Codes",
                "descricao": "Anatomia de requisicoes e respostas HTTP, idempotencia de verbos, codigos de status e padroes REST.",
                "xp": 50,
                "texto": (
                    "### A Web e a Arquitetura RESTful\n\n"
                    "O protocolo HTTP (Hypertext Transfer Protocol) e a base de comunicacao da World Wide Web. Em uma arquitetura REST (Representational State Transfer), clientes e servidores trocam representacoes de recursos (geralmente serializadas no formato JSON) de forma desacoplada e sem estado (stateless).\n\n"
                    "### Anatomia de uma Requisicao e Resposta HTTP\n\n"
                    "1. **Requisicao (Request)**:\n"
                    "   - **Metodo / Verbo**: Indica a acao desejada (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`).\n"
                    "   - **Endpoint / Path**: A URL do recurso (ex: `/api/v1/usuarios/42`).\n"
                    "   - **Cabecalhos (Headers)**: Metadados como `Content-Type: application/json` e `Authorization`.\n"
                    "   - **Corpo (Payload/Body)**: Dados transmitidos (obrigatorio em POST/PUT).\n"
                    "2. **Idempotencia**:\n"
                    "   - Metodos idempotentes (`GET`, `PUT`, `DELETE`): executa-los multiplas vezes produz o mesmo efeito no estado do servidor que executa-los uma unica vez.\n"
                    "   - Metodos nao idempotentes (`POST`): chamadas repetidas podem criar recursos duplicados.\n\n"
                    "### Taxonomia dos Codigos de Status (Status Codes)\n\n"
                    "- **2xx (Sucesso)**: `200 OK` (sucesso geral), `201 Created` (recurso criado com sucesso), `204 No Content` (sucesso sem conteudo de resposta, comum em deletes).\n"
                    "- **4xx (Erro do Cliente)**: `400 Bad Request` (payload invalido), `401 Unauthorized` (sem credenciais), `403 Forbidden` (sem permissao), `404 Not Found` (recurso inexistente), `422 Unprocessable Entity` (falha na validacao semantica).\n"
                    "- **5xx (Erro do Servidor)**: `500 Internal Server Error`, `502 Bad Gateway`, `503 Service Unavailable`.\n\n"
                    "```python\n"
                    "# Exemplo de representacao em Python do ciclo de requisicao/resposta\n"
                    "import json\n"
                    "\n"
                    "requisicao_exemplo = {\n"
                    "    'metodo': 'POST',\n"
                    "    'endpoint': '/api/v1/pedidos',\n"
                    "    'headers': {'Content-Type': 'application/json', 'Accept': 'application/json'},\n"
                    "    'payload': {'cliente_id': 101, 'itens': [{'produto': 'Teclado Mecanico', 'qtd': 1}]}\n"
                    "}\n"
                    "\n"
                    "resposta_servidor = {\n"
                    "    'status_code': 201,\n"
                    "    'status_texto': 'Created',\n"
                    "    'headers': {'Location': '/api/v1/pedidos/9842'},\n"
                    "    'body': json.dumps({'id': 9842, 'status': 'aprovado', 'total': 350.0})\n"
                    "}\n"
                    "\n"
                    "print(f'Status retornado: {resposta_servidor[\"status_code\"]} {resposta_servidor[\"status_texto\"]}')\n"
                    "```\n\n"
                    "> **Regra de Ouro REST**: Use URIs substantivas no plural (ex: `/produtos` em vez de `/obterProdutos`). A intencao da operacao deve vir expressa pelo verbo HTTP (`GET /produtos`, `POST /produtos`)."
                )
            },
            {
                "tipo": "MULTIPLA_ESCOLHA",
                "titulo": "Exercicio: Codigo de Status HTTP",
                "descricao": "Identifique o status code padrao para criacao bem-sucedida de recurso.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual codigo de status HTTP padrao deve ser retornado quando uma requisicao POST cria um recurso com sucesso?",
                        "opcoes": ["201 Created", "200 OK", "204 No Content", "302 Found"],
                        "gabarito_idx": 0,
                        "dica": "Codigo da familia 2xx especifico para itens 'Created' (criados)."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual faixa de codigos de status HTTP indica erros causados pelo cliente?",
                        "opcoes": ["2xx", "3xx", "4xx", "5xx"],
                        "gabarito_idx": 2,
                        "dica": "A familia 5xx indica falhas do servidor; a do cliente vem logo antes."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual metodo HTTP e utilizado para remover um recurso no servidor?",
                        "opcoes": ["PATCH", "REMOVE", "POST", "DELETE"],
                        "gabarito_idx": 3,
                        "dica": "O nome do metodo significa 'apagar' em ingles."
                    }
                ]
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Metodo HTTP Sem Efeito Colateral",
                "descricao": "Preencha o metodo HTTP idenpotente para consulta de dados.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Complete o metodo HTTP padrao utilizado para consultar informacoes sem alterar dados no servidor:",
                        "codigo_snippet": (
                            "# Requisicao HTTP para listar produtos\n"
                            "__BLANK_0__ /api/produtos HTTP/1.1\n"
                            "Host: api.exemplo.com"
                        ),
                        "gabarito": "GET",
                        "dica": "Verbo HTTP de tres letras para buscar/pegar."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o codigo de status retornado quando o recurso solicitado nao existe:",
                        "codigo_snippet": (
                            "HTTP/1.1 __BLANK_0__ Not Found\n"
                            "Content-Type: application/json\n"
                            "\n"
                            "{\"detail\": \"Produto nao encontrado\"}"
                        ),
                        "gabarito": "404",
                        "dica": "E o codigo de erro mais famoso da web."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o metodo HTTP que substitui completamente os dados de um recurso existente:",
                        "codigo_snippet": (
                            "# Substitui todos os dados do produto 7\n"
                            "__BLANK_0__ /api/produtos/7 HTTP/1.1\n"
                            "Content-Type: application/json"
                        ),
                        "gabarito": "PUT",
                        "dica": "Diferente do PATCH, esse metodo envia a representacao completa do recurso."
                    }
                ]
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Ciclo de Requisicao e Resposta",
                "descricao": "Ordene as etapas fundamentais de uma requisicao HTTP.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Ordene as etapas do ciclo de vida de uma chamada a uma API REST:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "Cliente envia requisicao HTTP com Headers e Payload",
                            "Servidor roteia para o endpoint correspondente",
                            "Regras de negocio processam os dados",
                            "Servidor retorna Response com Status Code e JSON"
                        ],
                        "dica": "Comece no envio do cliente, passe pelo roteamento, regras de negocio e finalize na resposta."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Ordene as etapas de autenticacao baseada em token em uma API REST:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "Cliente envia as credenciais para POST /login",
                            "Servidor valida as credenciais e emite um token",
                            "Cliente envia o token no cabecalho Authorization",
                            "Servidor libera o acesso ao recurso protegido"
                        ],
                        "dica": "O token so pode ser usado depois de ter sido emitido."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize o codigo que consome uma API com a biblioteca requests, verificando erros antes de ler o JSON:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "import requests",
                            "resposta = requests.get('https://api.exemplo.com/produtos')",
                            "resposta.raise_for_status()",
                            "produtos = resposta.json()"
                        ],
                        "dica": "Valide o status da resposta antes de interpretar o corpo."
                    }
                ]
            },
            {
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Cabecalho de Conteudo",
                "descricao": "Informe ao servidor o formato dos dados enviados no corpo da requisicao.",
                "xp": 150,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o tipo de midia padrao para payloads de dados em APIs REST modernas:",
                        "codigo_snippet": (
                            "POST /api/usuarios HTTP/1.1\n"
                            "Content-Type: application/__BLANK_0__\n\n"
                            "{\"nome\": \"Lucas\"}"
                        ),
                        "gabarito": "json",
                        "dica": "Formato de texto leve baseado em notacao de objetos JavaScript amplamente usado em APIs."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o codigo de status para um usuario NAO autenticado tentando acessar um recurso protegido:",
                        "codigo_snippet": (
                            "# Requisicao sem token para /perfil\n"
                            "HTTP/1.1 __BLANK_0__ Unauthorized"
                        ),
                        "gabarito": "401",
                        "dica": "Nao confunda com 403, usado quando o usuario esta autenticado mas sem permissao."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o caractere que inicia a query string na URL:",
                        "codigo_snippet": "GET /api/produtos__BLANK_0__categoria=livros&pagina=2 HTTP/1.1",
                        "gabarito": "?",
                        "dica": "Os parametros de consulta comecam apos um sinal de interrogacao."
                    }
                ]
            }
        ]
    },
    {
        "titulo": "FastAPI: Rotas, Path e Query Parameters",
        "descricao": "Criacao de aplicacoes com FastAPI, decorators de rota e passagem de parametros.",
        "nivel": "INTERMEDIARIO",
        "ordem_modulo": 2,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "FastAPI: Arquitetura ASGI, Rotas e Parametros",
                "descricao": "Como o FastAPI aproveita tipagem estatica, servidores ASGI, funcoes assincronas e gera documentacao OpenAPI automatica.",
                "xp": 50,
                "texto": (
                    "### Por Que o FastAPI e Tao Rapido?\n\n"
                    "O FastAPI e um framework web moderno construido sobre duas bases robustas: **Starlette** (para a camada de rede web de altissima performance) e **Pydantic** (para a camada de validacao e parsing de dados). Ele opera sobre a interface padrao **ASGI** (Asynchronous Server Gateway Interface), permitindo lidar com milhares de conexoes simultaneas por meio do mecanismo assincrono `async/await` do Python.\n\n"
                    "### Path Parameters vs Query Parameters\n\n"
                    "- **Path Parameters**: Variaveis embutidas diretamente na estrutura da URL (ex: `/produtos/{produto_id}`). Sao obrigatorias para identificar um recurso especifico.\n"
                    "- **Query Parameters**: Pares chave-valor apos a interrogacao `?` na URL (ex: `/produtos?categoria=eletronicos&limite=10`). O FastAPI os detecta automaticamente para qualquer argumento de funcao que nao conste na rota.\n\n"
                    "### Documentacao Interativa Automatica\n\n"
                    "Ao iniciar a aplicacao com um servidor ASGI como o `uvicorn`, o FastAPI gera em tempo real:\n"
                    "- **/docs**: Interface grafica interativa do **Swagger UI**, onde voce pode testar requisicoes diretamente pelo navegador.\n"
                    "- **/redoc**: Documentacao alternativa detalhada orientada a especificacao OpenAPI.\n\n"
                    "```python\n"
                    "from typing import Optional\n"
                    "from fastapi import FastAPI, HTTPException, status\n"
                    "\n"
                    "app = FastAPI(title='Catalogo API', version='1.0.0')\n"
                    "\n"
                    "# 1. Rota com Path Parameter e Query Parameter tipados\n"
                    "@app.get('/cursos/{curso_id}', status_code=status.HTTP_200_OK)\n"
                    "async def buscar_curso(curso_id: int, ativo: bool = True, busca: Optional[str] = None):\n"
                    "    if curso_id <= 0:\n"
                    "        raise HTTPException(status_code=400, detail='ID do curso deve ser positivo')\n"
                    "    return {\n"
                    "        'curso_id': curso_id,\n"
                    "        'ativo': ativo,\n"
                    "        'termo_busca': busca,\n"
                    "        'formato': 'Graduacao'\n"
                    "    }\n"
                    "```\n\n"
                    "> **Dica Pro**: Se sua rota executa operacoes bloqueantes tradicionais (como chamadas síncronas a banco), declare a funcao apenas com `def`. O FastAPI a executara em uma threadpool separada para nao travar o event loop principal."
                )
            },
            {
                "tipo": "MULTIPLA_ESCOLHA",
                "titulo": "Exercicio: Parametros de Rota",
                "descricao": "Identifique como o FastAPI reconhece Path Parameters na rota.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Como um Path Parameter deve ser declarado no caminho da rota no FastAPI?",
                        "opcoes": ["{item_id}", ":item_id", "<item_id>", "$item_id"],
                        "gabarito_idx": 0,
                        "dica": "O FastAPI utiliza chaves `{parametro}` para mapear variaveis na URL."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "No FastAPI, um parametro simples (int, str) da funcao que NAO aparece no caminho da rota e interpretado como:",
                        "opcoes": ["Path Parameter", "Request Body", "Query Parameter", "Header"],
                        "gabarito_idx": 2,
                        "dica": "Ele sera lido da parte da URL que vem depois do '?'."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual URL o FastAPI disponibiliza por padrao com a documentacao interativa (Swagger UI)?",
                        "opcoes": ["/swagger", "/api-docs", "/help", "/docs"],
                        "gabarito_idx": 3,
                        "dica": "E uma abreviacao de 'documentation'."
                    }
                ]
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Rota de Criacao",
                "descricao": "Complete o decorator do FastAPI para endpoints de cadastro.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o metodo do app FastAPI utilizado para rotas de inclusao de dados:",
                        "codigo_snippet": (
                            "from fastapi import FastAPI\n"
                            "app = FastAPI()\n\n"
                            "@app.__BLANK_0__('/itens', status_code=201)\n"
                            "def criar_item(nome: str):\n"
                            "    return {'item': nome}"
                        ),
                        "gabarito": "post",
                        "dica": "O metodo HTTP associado a criacao de recursos em caixa baixa."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o tipo do parametro para que o FastAPI converta e valide o id como numero inteiro:",
                        "codigo_snippet": (
                            "@app.get('/cursos/{curso_id}')\n"
                            "def buscar_curso(curso_id: __BLANK_0__):\n"
                            "    return {'id': curso_id}"
                        ),
                        "gabarito": "int",
                        "dica": "O FastAPI usa as type hints para validar os parametros."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o metodo do app utilizado para rotas de exclusao:",
                        "codigo_snippet": (
                            "@app.__BLANK_0__('/itens/{item_id}', status_code=204)\n"
                            "def remover_item(item_id: int):\n"
                            "    repositorio.remover(item_id)"
                        ),
                        "gabarito": "delete",
                        "dica": "O decorator tem o mesmo nome do metodo HTTP, em minusculas."
                    }
                ]
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Aplicacao FastAPI Basica",
                "descricao": "Ordene a importacao, instanciacao e rota raiz de um projeto FastAPI.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize o codigo para criar e expor um endpoint raiz com FastAPI:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "    __SLOT_3__"
                        ),
                        "blocos": [
                            "from fastapi import FastAPI",
                            "app = FastAPI()",
                            "@app.get('/')",
                            "def raiz(): return {'status': 'online'}"
                        ],
                        "dica": "Importe o FastAPI, instancie o app e entao decore a funcao raiz."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize o endpoint que retorna 404 quando o item nao existe:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "    __SLOT_2__\n"
                            "        __SLOT_3__\n"
                            "    __SLOT_4__"
                        ),
                        "blocos": [
                            "@app.get('/itens/{item_id}')",
                            "def buscar(item_id: int):",
                            "if item_id not in itens:",
                            "raise HTTPException(status_code=404)",
                            "return itens[item_id]"
                        ],
                        "dica": "O decorator vem antes da funcao; o retorno normal so acontece se o item existir."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize o codigo para criar um APIRouter, registrar uma rota e inclui-lo na aplicacao:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "router = APIRouter(prefix='/usuarios')",
                            "@router.get('/')",
                            "def listar(): return []",
                            "app.include_router(router)"
                        ],
                        "dica": "O router precisa ter suas rotas definidas antes de ser incluido no app."
                    }
                ]
            },
            {
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Servidor ASGI",
                "descricao": "Comando para executar aplicacoes FastAPI em modo de desenvolvimento.",
                "xp": 150,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o nome do servidor ASGI padrao mais popular para rodar aplicacoes FastAPI:",
                        "codigo_snippet": (
                            "# Execucao no terminal:\n"
                            "__BLANK_0__ main:app --reload"
                        ),
                        "gabarito": "uvicorn",
                        "dica": "Servidor ultrarrapido para Python cujo nome comeca com 'uv'."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a palavra-chave que transforma o endpoint em uma corrotina assincrona:",
                        "codigo_snippet": (
                            "@app.get('/status')\n"
                            "__BLANK_0__ def status():\n"
                            "    return {'ok': True}"
                        ),
                        "gabarito": "async",
                        "dica": "E a palavra usada junto de await na programacao assincrona."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a excecao do FastAPI que interrompe a requisicao com um status de erro:",
                        "codigo_snippet": (
                            "if not item:\n"
                            "    raise __BLANK_0__(status_code=404, detail='Item nao encontrado')"
                        ),
                        "gabarito": "HTTPException",
                        "dica": "O nome combina o protocolo com a palavra 'Exception'."
                    }
                ]
            }
        ]
    },
    {
        "titulo": "Modelos e Validacao de Dados com Pydantic",
        "descricao": "Definicao de schemas, tipagem estrita, validadores customizados e sanitizacao.",
        "nivel": "INTERMEDIARIO",
        "ordem_modulo": 3,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "Modelos, Validacao e Sanitizacao com Pydantic",
                "descricao": "Como o Pydantic realiza parsing seguro, validacao de contratos com Field e serializacao automatica.",
                "xp": 50,
                "texto": (
                    "### O Papel do Pydantic no Ecossistema Python\n\n"
                    "O Pydantic e uma biblioteca de **parsing de dados com validacao em tempo de execucao** orientada por Type Hints do Python. Diferente de validadores tradicionais que apenas checam se o dado esta correto, o Pydantic tenta **converter (coagir)** os dados de entrada para os tipos especificados (por exemplo, a string `'42'` sera convertida automaticamente para o inteiro `42`).\n\n"
                    "### BaseModel e Constraints com `Field`\n\n"
                    "Ao herdar de `BaseModel`, sua classe ganha suporte imediato a validacoes rigorosas atraves da funcao `Field`:\n\n"
                    "- **Restricoes Numericas**: `gt` (greater than), `ge` (greater or equal), `lt` (less than), `le` (less or equal).\n"
                    "- **Restricoes de Texto**: `min_length`, `max_length`, `regex` (expressoes regulares).\n"
                    "- **Campos Opcionais**: Marcados com `Optional[T] = None`.\n\n"
                    "### Resposta Automatica de Erro: 422 Unprocessable Entity\n\n"
                    "Se um cliente enviar um payload violando os tipos ou restricoes declaradas no schema, o FastAPI intercepta a requisicao antes de atingir sua logica de negocio e retorna um JSON estruturado detalhando exatamente qual campo falhou e o motivo.\n\n"
                    "```python\n"
                    "from typing import Optional\n"
                    "from pydantic import BaseModel, Field, EmailStr\n"
                    "\n"
                    "class ProdutoCreate(BaseModel):\n"
                    "    titulo: str = Field(..., min_length=3, max_length=100, description='Nome comercial do item')\n"
                    "    preco: float = Field(..., gt=0.0, description='Preco deve ser estritamente positivo')\n"
                    "    em_estoque: bool = True\n"
                    "    email_fornecedor: Optional[EmailStr] = None\n"
                    "\n"
                    "# Instanciacao e serializacao\n"
                    "novo_produto = ProdutoCreate(titulo='Teclado Mecanico', preco=299.90)\n"
                    "dicionario_dados = novo_produto.model_dump()     # Converte para dict Python\n"
                    "json_dados = novo_produto.model_dump_json()      # Converte para string JSON\n"
                    "print(json_dados)\n"
                    "```\n\n"
                    "> **Dica Pro**: Em Pydantic V2, utilize `.model_dump()` e `.model_dump_json()` em vez dos metodos legados `.dict()` e `.json()` da versao 1."
                )
            },
            {
                "tipo": "MULTIPLA_ESCOLHA",
                "titulo": "Exercicio: Classe Base Pydantic",
                "descricao": "Identifique a classe essencial para declaracao de schemas no Pydantic.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual classe base do Pydantic deve ser herdada para criar modelos de validacao de dados?",
                        "opcoes": ["BaseModel", "SchemaModel", "DataModel", "Entity"],
                        "gabarito_idx": 0,
                        "dica": "Classe fundamental do Pydantic composta pelas palavras 'Base' e 'Model'."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "O que o Pydantic faz por padrao ao receber a string '42' para um campo declarado como int?",
                        "opcoes": [
                            "Lanca erro sempre",
                            "Converte para o inteiro 42 (coercao)",
                            "Ignora o campo",
                            "Armazena como string"
                        ],
                        "gabarito_idx": 1,
                        "dica": "No modo padrao (lax), o Pydantic tenta converter valores compativeis."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual excecao o Pydantic lanca quando os dados nao respeitam o schema?",
                        "opcoes": ["TypeError", "ValueError", "ValidationError", "SchemaError"],
                        "gabarito_idx": 2,
                        "dica": "O nome da excecao descreve a etapa que falhou: a validacao."
                    }
                ]
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Heranca do Modelo",
                "descricao": "Complete a definicao de classe herdando do BaseModel.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o nome da classe base do Pydantic na definicao do schema:",
                        "codigo_snippet": (
                            "from pydantic import BaseModel\n\n"
                            "class Produto( __BLANK_0__ ):\n"
                            "    titulo: str\n"
                            "    preco: float"
                        ),
                        "gabarito": "BaseModel",
                        "dica": "Mesmo nome da classe importada do modulo pydantic."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a funcao do Pydantic usada para adicionar restricoes ao campo (preco maior que zero):",
                        "codigo_snippet": (
                            "from pydantic import BaseModel, Field\n"
                            "\n"
                            "class Produto(BaseModel):\n"
                            "    preco: float = __BLANK_0__(gt=0)"
                        ),
                        "gabarito": "Field",
                        "dica": "A funcao foi importada na primeira linha junto com BaseModel."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o tipo do Pydantic que valida automaticamente o formato de e-mail:",
                        "codigo_snippet": (
                            "from pydantic import BaseModel, EmailStr\n"
                            "\n"
                            "class Cadastro(BaseModel):\n"
                            "    email: __BLANK_0__"
                        ),
                        "gabarito": "EmailStr",
                        "dica": "O tipo especial foi importado na primeira linha."
                    }
                ]
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Endpoint com Body Validado",
                "descricao": "Ordene a criacao do schema Pydantic e a rota que o consome no FastAPI.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize o schema de cliente e o endpoint POST que o recebe como parametro:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "    __SLOT_1__\n"
                            "__SLOT_2__\n"
                            "    __SLOT_3__"
                        ),
                        "blocos": [
                            "class ClienteCreate(BaseModel):",
                            "nome: str; email: str",
                            "@app.post('/clientes')",
                            "def cadastrar(cliente: ClienteCreate): return cliente"
                        ],
                        "dica": "Defina a classe do schema primeiro e use-a como type annotation na rota."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize o modelo com um validador customizado que padroniza o nome:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "    __SLOT_1__\n"
                            "    __SLOT_2__\n"
                            "    __SLOT_3__\n"
                            "    __SLOT_4__\n"
                            "        __SLOT_5__"
                        ),
                        "blocos": [
                            "class Usuario(BaseModel):",
                            "nome: str",
                            "@field_validator('nome')",
                            "@classmethod",
                            "def validar_nome(cls, v):",
                            "return v.strip().title()"
                        ],
                        "dica": "Declare o campo antes do validador; @field_validator fica acima de @classmethod."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize o tratamento de erro ao instanciar um modelo com dados invalidos:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "    __SLOT_1__\n"
                            "__SLOT_2__\n"
                            "    __SLOT_3__"
                        ),
                        "blocos": [
                            "try:",
                            "usuario = Usuario(nome='Ana', idade='abc')",
                            "except ValidationError as erro:",
                            "print(erro.errors())"
                        ],
                        "dica": "A instanciacao arriscada fica dentro do bloco try."
                    }
                ]
            },
            {
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Campos Opcionais",
                "descricao": "Declare campos nao-obrigatorios utilizando Optional da biblioteca typing.",
                "xp": 150,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a lacuna com o tipo que permite que o campo receba None como valor padrao:",
                        "codigo_snippet": (
                            "from typing import Optional\n"
                            "from pydantic import BaseModel\n\n"
                            "class Item(BaseModel):\n"
                            "    nome: str\n"
                            "    descricao: __BLANK_0__[str] = None"
                        ),
                        "gabarito": "Optional",
                        "dica": "Tipo generico em ingles para 'opcional'."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o metodo do Pydantic v2 que converte a instancia em dicionario:",
                        "codigo_snippet": (
                            "produto = Produto(titulo='Livro', preco=59.9)\n"
                            "dados = produto.__BLANK_0__()\n"
                            "print(dados)  # {'titulo': 'Livro', 'preco': 59.9}"
                        ),
                        "gabarito": "model_dump",
                        "dica": "No Pydantic v2, os metodos do modelo comecam com o prefixo model_."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o argumento do decorator que define o schema da resposta do endpoint:",
                        "codigo_snippet": (
                            "@app.post('/produtos', __BLANK_0__=ProdutoPublico)\n"
                            "def criar(produto: ProdutoCreate):\n"
                            "    return salvar(produto)"
                        ),
                        "gabarito": "response_model",
                        "dica": "O argumento indica o 'modelo da resposta'."
                    }
                ]
            }
        ]
    },
    {
        "titulo": "Persistencia e Modelos com SQLAlchemy ORM",
        "descricao": "Conexao com bancos de dados relacionais, sessoes, migrations e consultas.",
        "nivel": "INTERMEDIARIO",
        "ordem_modulo": 4,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "Persistencia de Dados e Mapeamento ORM com SQLAlchemy",
                "descricao": "Modelagem relacional, ciclo de vida da Session, Foreign Keys, relacionamentos e transacoes seguras.",
                "xp": 50,
                "texto": (
                    "### Mapeamento Objeto-Relacional (ORM)\n\n"
                    "O SQLAlchemy e o toolkit SQL e ORM mais respeitado do ecossistema Python. Ele abstrai diferencas de dialetos SQL (PostgreSQL, SQLite, MySQL) permitindo representar tabelas do banco como classes Python e registros como instancias dessas classes.\n\n"
                    "### Modelos Declarativos e Chaves\n\n"
                    "Todo modelo herda de uma base declarativa (`DeclarativeBase`) e especifica:\n"
                    "- `__tablename__`: O nome exato da tabela no banco de dados.\n"
                    "- Colunas com tipos estritos: `Integer`, `String`, `Boolean`, `DateTime`, etc.\n"
                    "- Restricoes relacionais: `primary_key=True`, `unique=True`, `nullable=False` e `ForeignKey('outra_tabela.id')`.\n\n"
                    "### O Ciclo de Vida da Sessao (Session)\n\n"
                    "A `Session` gerencia as transacoes com o banco de dados atraves do padrao **Unit of Work**:\n"
                    "1. `db.add(objeto)`: Registra a nova entidade no rastreador da sessao.\n"
                    "2. `db.commit()`: Efetiva a transacao no banco (executa `INSERT`/`UPDATE` atomicos).\n"
                    "3. `db.rollback()`: Em caso de falha/excecao, desfaz todas as alteracoes pendentes preservando a integridade dos dados.\n"
                    "4. `db.refresh(objeto)`: Recarrega o objeto com dados gerados pelo banco (ex: ID autoincrementado).\n\n"
                    "```python\n"
                    "from sqlalchemy import Column, Integer, String, Float, Boolean\n"
                    "from sqlalchemy.orm import declarative_base, Session\n"
                    "\n"
                    "Base = declarative_base()\n"
                    "\n"
                    "class ProdutoModel(Base):\n"
                    "    __tablename__ = 'produtos'\n"
                    "    \n"
                    "    id = Column(Integer, primary_key=True, index=True)\n"
                    "    nome = Column(String(100), nullable=False)\n"
                    "    preco = Column(Float, nullable=False)\n"
                    "    disponivel = Column(Boolean, default=True)\n"
                    "\n"
                    "# Operacao transacional segura\n"
                    "def salvar_produto(db: Session, nome: str, preco: float):\n"
                    "    item = ProdutoModel(nome=nome, preco=preco)\n"
                    "    try:\n"
                    "        db.add(item)\n"
                    "        db.commit()\n"
                    "        db.refresh(item)\n"
                    "        return item\n"
                    "    except Exception:\n"
                    "        db.rollback()\n"
                    "        raise\n"
                    "```\n\n"
                    "> **Boa Pratica**: Sempre utilize gerenciadores de contexto (`with`) ou dependencias do FastAPI (`yield db`) para garantir que as conexoes de sessao sejam fechadas apos cada requisicao."
                )
            },
            {
                "tipo": "MULTIPLA_ESCOLHA",
                "titulo": "Exercicio: Chave Primaria",
                "descricao": "Identifique o argumento que define a chave primaria da tabela.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "No SQLAlchemy, qual argumento do Column define que uma coluna e a chave primaria da tabela?",
                        "opcoes": ["primary_key=True", "is_primary=True", "id_key=True", "unique_key=True"],
                        "gabarito_idx": 0,
                        "dica": "O argumento em ingles e 'primary_key' atribuido com True."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual metodo da Session confirma (persiste) definitivamente as alteracoes no banco?",
                        "opcoes": ["save()", "flush()", "commit()", "persist()"],
                        "gabarito_idx": 2,
                        "dica": "E o mesmo termo usado para confirmar uma transacao em SQL."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Para que serve a funcao relationship() no SQLAlchemy?",
                        "opcoes": [
                            "Criar indices na tabela",
                            "Declarar a navegacao entre objetos relacionados (ex: usuario.pedidos)",
                            "Abrir a conexao com o banco",
                            "Executar migrations"
                        ],
                        "gabarito_idx": 1,
                        "dica": "Ela atua no nivel dos objetos Python, nao das colunas."
                    }
                ]
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Nome da Tabela",
                "descricao": "Complete o atributo especial que especifica o nome da tabela no banco.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a propriedade especial com dois underlines utilizada para definir o nome da tabela:",
                        "codigo_snippet": (
                            "class Pedido(Base):\n"
                            "    __BLANK_0__ = 'pedidos'\n"
                            "    id = Column(Integer, primary_key=True)"
                        ),
                        "gabarito": "__tablename__",
                        "dica": "Palavra com duplos underlines: '__tablename__'."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a construcao que liga a coluna usuario_id a chave primaria da tabela usuarios:",
                        "codigo_snippet": (
                            "class Pedido(Base):\n"
                            "    __tablename__ = 'pedidos'\n"
                            "    usuario_id = Column(Integer, __BLANK_0__('usuarios.id'))"
                        ),
                        "gabarito": "ForeignKey",
                        "dica": "E o conceito de chave estrangeira, em ingles."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o metodo da query que aplica a condicao de busca por e-mail:",
                        "codigo_snippet": "usuario = db.query(UsuarioDB).__BLANK_0__(UsuarioDB.email == email).first()",
                        "gabarito": "filter",
                        "dica": "O metodo 'filtra' os registros pela expressao informada."
                    }
                ]
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Persistencia com Session",
                "descricao": "Ordene a criacao, adicao e commit de um novo registro no banco de dados.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize a sequencia correta para gravar uma nova entidade no banco via Session:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "novo_usuario = UsuarioDB(email='aluno@fatec.sp.gov.br')",
                            "db.add(novo_usuario)",
                            "db.commit()",
                            "db.refresh(novo_usuario)"
                        ],
                        "dica": "Crie o objeto, adicione a sessao com db.add(), efetive com db.commit() e atualize com db.refresh()."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize a configuracao do banco e a primeira consulta:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "engine = create_engine('sqlite:///app.db')",
                            "SessionLocal = sessionmaker(bind=engine)",
                            "db = SessionLocal()",
                            "usuarios = db.query(UsuarioDB).all()"
                        ],
                        "dica": "A fabrica de sessoes depende da engine; a consulta depende da sessao."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize a dependencia get_db que garante o fechamento da sessao:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "    __SLOT_1__\n"
                            "    __SLOT_2__\n"
                            "        __SLOT_3__\n"
                            "    __SLOT_4__\n"
                            "        __SLOT_5__"
                        ),
                        "blocos": ["def get_db():", "db = SessionLocal()", "try:", "yield db", "finally:", "db.close()"],
                        "dica": "O bloco finally executa sempre, mesmo se ocorrer erro."
                    }
                ]
            },
            {
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Reversao de Transacao",
                "descricao": "Reverta uma transacao com falha para preservar a integridade do banco.",
                "xp": 150,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o metodo da sessao que desfaz alteracoes em caso de erro na transacao:",
                        "codigo_snippet": (
                            "try:\n"
                            "    db.commit()\n"
                            "except Exception:\n"
                            "    db.__BLANK_0__()\n"
                            "    raise"
                        ),
                        "gabarito": "rollback",
                        "dica": "Termo de banco de dados para reverter ou 'desfazer' uma transacao."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o metodo da sessao que marca o objeto para remocao:",
                        "codigo_snippet": (
                            "produto = db.get(Produto, produto_id)\n"
                            "db.__BLANK_0__(produto)\n"
                            "db.commit()"
                        ),
                        "gabarito": "delete",
                        "dica": "E o oposto de db.add()."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o argumento do Column que impede valores repetidos na coluna:",
                        "codigo_snippet": "email = Column(String, __BLANK_0__=True, nullable=False)",
                        "gabarito": "unique",
                        "dica": "A restricao garante que cada valor seja 'unico'."
                    }
                ]
            }
        ]
    },
    {
        "titulo": "Autenticacao Segura com Tokens JWT",
        "descricao": "Criptografia de senhas com passlib/bcrypt, geracao de tokens JWT e protecao de rotas.",
        "nivel": "AVANCADO",
        "ordem_modulo": 5,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "Autenticacao Stateless com JWT, Hashing e Seguranca",
                "descricao": "Como funcionam tokens JWT (Header, Payload, Signature), hashing seguro de senhas e protecao de rotas com Bearer tokens.",
                "xp": 50,
                "texto": (
                    "### Seguranca e Autenticacao Stateless em APIs\n\n"
                    "Diferente de aplicacoes web tradicionais que utilizavam sessoes e cookies no servidor (stateful), APIs modernas operam no modelo **stateless**: cada requisicao HTTP deve conter todas as informacoes necessarias para autenticar e autorizar a operacao. O padrao ouro da industria para esse modelo e o **JSON Web Token (JWT)**.\n\n"
                    "### Anatomia de um Token JWT (`header.payload.signature`)\n\n"
                    "Um JWT e composto por tres partes separadas por pontos e codificadas em Base64Url:\n"
                    "1. **Header (Cabecalho)**: Informa o algoritmo de assinatura utilizado (ex: `HS256` para chave simetrica ou `RS256` para chave assimetrica publica/privada).\n"
                    "2. **Payload (Dados/Claims)**: Contem informacoes sobre o usuario e metadados, tais como:\n"
                    "   - `sub` (subject): Identificador unico do usuario (ex: email ou ID).\n"
                    "   - `exp` (expiration time): Timestamp Unix indicando quando o token expira.\n"
                    "   - `iat` (issued at): Quando o token foi gerado.\n"
                    "3. **Signature (Assinatura)**: Hash criptografico gerado a partir do header + payload + uma chave secreta privada (`SECRET_KEY`). Garante que os dados nao foram adulterados no caminho.\n\n"
                    "### Transmissao Segura via Cabecalho HTTP\n\n"
                    "O cliente deve armazenar o token com seguranca e anexa-lo em todas as chamadas autenticadas no formato:\n"
                    "`Authorization: Bearer <seu_token_jwt>`\n\n"
                    "```python\n"
                    "from datetime import datetime, timedelta, timezone\n"
                    "from jose import jwt\n"
                    "\n"
                    "SECRET_KEY = 'sua-chave-secreta-super-segura-e-longa'\n"
                    "ALGORITHM = 'HS256'\n"
                    "ACCESS_TOKEN_EXPIRE_MINUTES = 60\n"
                    "\n"
                    "def criar_token_acesso(email_usuario: str) -> str:\n"
                    "    tempo_expiracao = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)\n"
                    "    claims_payload = {\n"
                    "        'sub': email_usuario,\n"
                    "        'exp': tempo_expiracao,\n"
                    "        'papel': 'estudante'\n"
                    "    }\n"
                    "    token_assinado = jwt.encode(claims_payload, SECRET_KEY, algorithm=ALGORITHM)\n"
                    "    return token_assinado\n"
                    "\n"
                    "token = criar_token_acesso('aluno@fatec.sp.gov.br')\n"
                    "print(f'Token JWT gerado com sucesso: {token[:30]}...')\n"
                    "```\n\n"
                    "> **Alerta de Seguranca**: O payload do JWT e apenas codificado em Base64, e **nao** criptografado. Qualquer pessoa pode ler seu conteudo. Portanto, **nunca** armazene senhas ou informacoes confidenciais dentro do payload."
                )
            },
            {
                "tipo": "MULTIPLA_ESCOLHA",
                "titulo": "Exercicio: Cabecalho de Autorizacao",
                "descricao": "Identifique o padrao de envio de token JWT no cabecalho HTTP.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual prefixo padrao acompanha o token JWT no cabecalho 'Authorization'?",
                        "opcoes": ["Bearer", "Token", "JWT", "Basic"],
                        "gabarito_idx": 0,
                        "dica": "O esquema padrao do protocolo OAuth2 e 'Bearer <token>'."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Por que senhas devem ser armazenadas com hash (ex: bcrypt) em vez de texto puro?",
                        "opcoes": [
                            "Para ocupar menos espaco no banco",
                            "Porque o hash pode ser revertido facilmente",
                            "Para que um vazamento do banco nao exponha as senhas originais",
                            "Para acelerar o login"
                        ],
                        "gabarito_idx": 2,
                        "dica": "Pense no que acontece se alguem obtiver uma copia do banco de dados."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual claim padrao do JWT indica o momento de expiracao do token?",
                        "opcoes": ["sub", "iat", "aud", "exp"],
                        "gabarito_idx": 3,
                        "dica": "E uma abreviacao de 'expiration'."
                    }
                ]
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Injecao de Dependencias",
                "descricao": "Preencha a funcao do FastAPI para injetar a dependencia do usuario autenticado.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Complete a lacuna com a funcao Depends do FastAPI para proteger o endpoint:",
                        "codigo_snippet": (
                            "from fastapi import Depends\n\n"
                            "@app.get('/perfil')\n"
                            "def meu_perfil(usuario = __BLANK_0__(obter_usuario_atual)):\n"
                            "    return {'email': usuario.email}"
                        ),
                        "gabarito": "Depends",
                        "dica": "Funcao nativa do FastAPI comecando com letra maiuscula 'Depends'."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o metodo do CryptContext que compara a senha digitada com o hash armazenado:",
                        "codigo_snippet": (
                            "from passlib.context import CryptContext\n"
                            "pwd_context = CryptContext(schemes=['bcrypt'])\n"
                            "\n"
                            "valida = pwd_context.__BLANK_0__(senha_digitada, usuario.senha_hash)"
                        ),
                        "gabarito": "verify",
                        "dica": "O metodo 'verifica' se a senha corresponde ao hash."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o metodo do CryptContext que gera o hash de uma senha:",
                        "codigo_snippet": "senha_hash = pwd_context.__BLANK_0__('minhaSenha123')",
                        "gabarito": "hash",
                        "dica": "O nome do metodo e o proprio nome da operacao."
                    }
                ]
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Geracao de Token JWT",
                "descricao": "Ordene a criacao do payload com expiracao e a codificacao do token.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize o fluxo para assinar e emitir um token JWT:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "expiracao = datetime.utcnow() + timedelta(hours=2)",
                            "payload = {'sub': usuario.email, 'exp': expiracao}",
                            "token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')",
                            "return {'access_token': token, 'token_type': 'bearer'}"
                        ],
                        "dica": "Calcule a expiracao, monte o payload, assine com jwt.encode() e retorne o dicionario."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize a dependencia que identifica o usuario a partir do token:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "    __SLOT_1__\n"
                            "    __SLOT_2__\n"
                            "    __SLOT_3__"
                        ),
                        "blocos": [
                            "def obter_usuario_atual(token: str = Depends(oauth2_scheme)):",
                            "dados = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])",
                            "usuario = buscar_por_email(dados['sub'])",
                            "return usuario"
                        ],
                        "dica": "Decodifique o token antes de usar o e-mail contido no claim sub."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize o fluxo de login que valida as credenciais antes de emitir o token:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "    __SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "usuario = buscar_por_email(form.username)",
                            "if not usuario or not pwd_context.verify(form.password, usuario.senha_hash):",
                            "raise HTTPException(status_code=401)",
                            "return criar_token_acesso(usuario.email)"
                        ],
                        "dica": "O token so deve ser emitido depois que a senha for verificada."
                    }
                ]
            },
            {
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Decodificacao de Token",
                "descricao": "Valide a assinatura de um token recebido do cliente.",
                "xp": 150,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o metodo da biblioteca jwt utilizado para decodificar e verificar o token:",
                        "codigo_snippet": (
                            "from jose import jwt\n\n"
                            "dados = jwt.__BLANK_0__(token, SECRET_KEY, algorithms=['HS256'])\n"
                            "email = dados.get('sub')"
                        ),
                        "gabarito": "decode",
                        "dica": "O inverso de 'encode' e 'decode'."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a classe do FastAPI que extrai o token Bearer do cabecalho Authorization:",
                        "codigo_snippet": (
                            "from fastapi.security import OAuth2PasswordBearer\n"
                            "\n"
                            "oauth2_scheme = __BLANK_0__(tokenUrl='login')"
                        ),
                        "gabarito": "OAuth2PasswordBearer",
                        "dica": "A classe foi importada na primeira linha."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a excecao lancada quando o token e invalido ou expirou:",
                        "codigo_snippet": (
                            "from jose import jwt, JWTError\n"
                            "\n"
                            "try:\n"
                            "    dados = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])\n"
                            "except __BLANK_0__:\n"
                            "    raise HTTPException(status_code=401)"
                        ),
                        "gabarito": "JWTError",
                        "dica": "A excecao foi importada junto com jwt."
                    }
                ]
            }
        ]
    }
]

# ==============================================================================
# TRILHA 3: Python: Analise de Dados
# ==============================================================================
trilha_dados = Trilha.objects.create(
    titulo="Python: Analise de Dados",
    descricao="Analise grandes volumes de informacao com NumPy, Pandas, agregacoes estatisticas e visualizacoes graficas.",
    habilidade="Ciência de Dados",
    ativo=True
)

modulos_dados = [
    {
        "titulo": "Computacao Numerica e Vetorizacao com NumPy",
        "descricao": "Arrays multidimensionais ndarray, operacoes vetorizadas e funcoes estatisticas.",
        "nivel": "INTERMEDIARIO",
        "ordem_modulo": 1,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "Computacao Cientifica e Vetorizacao com NumPy",
                "descricao": "Por que o NumPy e o alicerce da ciencia de dados: ndarray, memoria contigua em C, broadcasting e funcoes universais (ufuncs).",
                "xp": 50,
                "texto": (
                    "### A Revolucao da Computacao Vetorizada com NumPy\n\n"
                    "O **NumPy** (Numerical Python) e o pacote fundamental para computacao cientifica em Python. Listas nativas do Python armazenam ponteiros para objetos dispersos na memoria RAM, gerando sobrecarga de checagem dinamica a cada operacao. O NumPy resolve esse gargalo atraves do **`ndarray`** (N-dimensional array), que armazena dados homogeneos em blocos de memoria continua (C-contiguous memory layout).\n\n"
                    "### O Que e Vetorizacao?\n\n"
                    "Vetorizacao e a capacidade de aplicar operacoes matematicas diretamente sobre colecoes inteiras sem escrever lacos `for` explicitos em Python. As operacoes sao delegadas para rotinas compiladas e altamente otimizadas em C e Fortran, atingindo velocidades dezenas a centenas de vezes superiores ao Python puro.\n\n"
                    "### Regras de Broadcasting e Ufuncs\n\n"
                    "- **Universal Functions (ufuncs)**: Funcoes matematicas elemento a elemento de altissimo desempenho, como `np.sqrt()`, `np.exp()`, `np.sin()`, `np.mean()` e `np.std()`.\n"
                    "- **Broadcasting**: Capacidade do NumPy de realizar operacoes aritmeticas entre arrays de dimensoes distintas (por exemplo, somar um escalar a uma matriz bidimensional) sem duplicar dados na memoria.\n\n"
                    "```python\n"
                    "import numpy as np\n"
                    "\n"
                    "# 1. Criacao e inspecao de ndarray\n"
                    "dados = np.array([[10, 20, 30], [40, 50, 60]], dtype=np.float64)\n"
                    "print(f'Formato (shape): {dados.shape} | Dimensoes: {dados.ndim} | Tipo: {dados.dtype}')\n"
                    "\n"
                    "# 2. Operacao vetorizada com Broadcasting (multiplicacao e adicao escalar)\n"
                    "dados_normalizados = (dados * 1.5) + 10\n"
                    "\n"
                    "# 3. Agregacoes estatisticas velozes\n"
                    "media_global = np.mean(dados)\n"
                    "media_por_coluna = np.mean(dados, axis=0) # Eixo vertical\n"
                    "desvio_padrao = np.std(dados)\n"
                    "\n"
                    "print(f'Media global: {media_global:.2f} | Por coluna: {media_por_coluna}')\n"
                    "```\n\n"
                    "> **Dica Pro**: Prefira sempre arrays pre-alocados como `np.zeros(shape)` ou `np.ones(shape)` em vez de criar listas Python vazias e preenche-las com `append()`."
                )
            },
            {
                "tipo": "MULTIPLA_ESCOLHA",
                "titulo": "Exercicio: Criacao de Array",
                "descricao": "Identifique a funcao basica para converter uma lista em array NumPy.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual funcao da biblioteca NumPy converte uma lista tradicional de Python em um array vetorizado?",
                        "opcoes": ["np.array()", "np.create()", "np.to_array()", "np.vector()"],
                        "gabarito_idx": 0,
                        "dica": "Funcao classica chamada simplesmente de 'array'."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual atributo de um ndarray informa suas dimensoes, como (3, 4)?",
                        "opcoes": ["size", "shape", "ndim", "length"],
                        "gabarito_idx": 1,
                        "dica": "O atributo descreve o 'formato' do array."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual o resultado de np.array([1, 2, 3]) * 2?",
                        "opcoes": ["[1, 2, 3, 1, 2, 3]", "Erro de tipo", "array([2, 4, 6])", "array([3, 4, 5])"],
                        "gabarito_idx": 2,
                        "dica": "Operacoes em arrays NumPy sao vetorizadas: aplicadas elemento a elemento."
                    }
                ]
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Alias Padrao da Biblioteca",
                "descricao": "Preencha a convencao universal de importacao do NumPy na comunidade.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Complete o alias padrao adotado globalmente para importar o pacote numpy:",
                        "codigo_snippet": (
                            "import numpy as __BLANK_0__\n\n"
                            "valores = __BLANK_0__.zeros(5)"
                        ),
                        "gabarito": "np",
                        "dica": "Abreviacao de duas letras mais famosa da ciencia de dados."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o metodo que reorganiza os 6 valores em uma matriz de 2 linhas e 3 colunas:",
                        "codigo_snippet": (
                            "import numpy as np\n"
                            "valores = np.arange(6)\n"
                            "matriz = valores.__BLANK_0__(2, 3)"
                        ),
                        "gabarito": "reshape",
                        "dica": "O metodo muda o 'formato' sem alterar os dados."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a funcao que gera uma sequencia de valores com passo definido:",
                        "codigo_snippet": (
                            "import numpy as np\n"
                            "pares = np.__BLANK_0__(0, 10, 2)  # array([0, 2, 4, 6, 8])"
                        ),
                        "gabarito": "arange",
                        "dica": "E a versao NumPy do range() do Python."
                    }
                ]
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Estatisticas Basicas com NumPy",
                "descricao": "Ordene a criacao do array e o calculo de media e desvio padrao.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize o calculo estatistico sobre uma amostra de medicoes:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "import numpy as np",
                            "dados = np.array([12, 15, 18, 20, 25])",
                            "media = np.mean(dados)",
                            "desvio = np.std(dados)"
                        ],
                        "dica": "Importe o numpy, declare os dados e calcule media e desvio padrao."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize o codigo que seleciona apenas as notas de aprovacao com uma mascara booleana:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "import numpy as np",
                            "notas = np.array([4.5, 7.0, 8.5, 5.0])",
                            "aprovados = notas[notas >= 6]",
                            "print(aprovados)  # [7.  8.5]"
                        ],
                        "dica": "A mascara e aplicada sobre o array ja criado."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize o codigo que centraliza os dados subtraindo a media:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "dados = np.array([10, 20, 30])",
                            "media = dados.mean()",
                            "centralizados = dados - media",
                            "print(centralizados)  # [-10.   0.  10.]"
                        ],
                        "dica": "Calcule a media antes de usa-la na subtracao vetorizada."
                    }
                ]
            },
            {
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Gerador de Zeros",
                "descricao": "Crie uma matriz preenchida inicialmente com zeros.",
                "xp": 150,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a funcao do NumPy que inicializa um array preenchido exclusivamente com o numero 0:",
                        "codigo_snippet": (
                            "import numpy as np\n"
                            "matriz_vazia = np.__BLANK_0__((3, 3))"
                        ),
                        "gabarito": "zeros",
                        "dica": "Palavra em ingles no plural para 'zeros'."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o parametro que faz a soma acontecer ao longo das linhas, resultando no total de cada coluna:",
                        "codigo_snippet": (
                            "matriz = np.array([[1, 2], [3, 4]])\n"
                            "soma_colunas = matriz.sum(__BLANK_0__=0)  # array([4, 6])"
                        ),
                        "gabarito": "axis",
                        "dica": "O parametro indica o 'eixo' da operacao."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a funcao do NumPy que retorna o maior valor do array:",
                        "codigo_snippet": (
                            "temperaturas = np.array([22.5, 31.0, 27.3])\n"
                            "maior = np.__BLANK_0__(temperaturas)  # 31.0"
                        ),
                        "gabarito": "max",
                        "dica": "E a abreviacao de 'maximo'."
                    }
                ]
            }
        ]
    },
    {
        "titulo": "Manipulacao Tabular com Pandas Series e DataFrames",
        "descricao": "Criacao de DataFrames, selecao com loc/iloc, inspecao de colunas e estatisticas descritivas.",
        "nivel": "INTERMEDIARIO",
        "ordem_modulo": 2,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "Estruturas Tabulares: Pandas Series e DataFrames",
                "descricao": "Dominando a manipulacao de tabelas em memoria: diferencas entre Series e DataFrame, indexacao com loc/iloc e inspecao estatistica.",
                "xp": 50,
                "texto": (
                    "### Manipulacao Tabular com Pandas\n\n"
                    "O **Pandas** e o pacote lider mundial para analise e manipulacao de dados estruturados em Python. Ele fornece duas estruturas de dados essenciais:\n\n"
                    "1. **`Series`**: Um array unidimensional rotulado capaz de armazenar qualquer tipo de dado (inteiros, strings, objetos). Funciona como uma coluna individual de uma planilha ou banco de dados.\n"
                    "2. **`DataFrame`**: Uma estrutura bidimensional rotulada com eixos heterogeneos (linhas e colunas), comparavel a uma tabela relacional SQL ou planilha do Excel.\n\n"
                    "### Selecao e Indexacao: `.loc[]` vs `.iloc[]`\n\n"
                    "- **`.loc[label]`**: Indexacao baseada em **rotulos** (nomes das colunas ou indices declarados).\n"
                    "- **`.iloc[posicao]`**: Indexacao estritamente baseada em **posicoes inteiras** (zero-indexed, similar a matrizes).\n\n"
                    "### Metodos Cruciais de Inspecao Inicial\n\n"
                    "- `df.head(n)`: Inspeciona as primeiras $n$ linhas (padrao 5).\n"
                    "- `df.info()`: Exibe contagem de nao-nulos e consumo de memoria por coluna.\n"
                    "- `df.describe()`: Gera resumo estatistico (media, desvio padrao, quartis, min, max).\n\n"
                    "```python\n"
                    "import pandas as pd\n"
                    "\n"
                    "# 1. Criando um DataFrame a partir de dicionario de listas\n"
                    "dados_vendas = {\n"
                    "    'cliente': ['Lucas', 'Julia', 'Marcos', 'Fernanda'],\n"
                    "    'departamento': ['TI', 'Marketing', 'TI', 'Financeiro'],\n"
                    "    'valor_contrato': [12500.0, 8900.0, 15400.0, 7200.0],\n"
                    "    'ativo': [True, True, False, True]\n"
                    "}\n"
                    "df = pd.DataFrame(dados_vendas)\n"
                    "\n"
                    "# 2. Selecao posicional com iloc e rotulo com loc\n"
                    "primeira_linha = df.iloc[0]                  # Retorna Series da linha 0\n"
                    "colunas_especificas = df.loc[:, ['cliente', 'valor_contrato']]\n"
                    "\n"
                    "# 3. Resumo estatistico automatico\n"
                    "resumo_numerico = df.describe()\n"
                    "print(resumo_numerico)\n"
                    "```\n\n"
                    "> **Boa Pratica**: Sempre verifique `df.info()` e `df.dtypes` logo apos carregar um arquivo para garantir que colunas de data ou preco nao foram importadas como texto genérico (`object`)."
                )
            },
            {
                "tipo": "MULTIPLA_ESCOLHA",
                "titulo": "Exercicio: Visualizar Primeiras Linhas",
                "descricao": "Metodo rapido de inspecao das primeiras linhas do DataFrame.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual metodo do DataFrame do Pandas exibe por padrao as primeiras 5 linhas da tabela?",
                        "opcoes": ["head()", "top()", "first()", "preview()"],
                        "gabarito_idx": 0,
                        "dica": "Metodo cujo nome em ingles significa 'cabeca' ou 'topo'."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual a diferenca entre loc e iloc no Pandas?",
                        "opcoes": [
                            "loc usa posicoes inteiras; iloc usa rotulos",
                            "loc usa rotulos (labels); iloc usa posicoes inteiras",
                            "Sao identicos",
                            "iloc so funciona com Series"
                        ],
                        "gabarito_idx": 1,
                        "dica": "O 'i' de iloc vem de 'integer' (posicao)."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "O que e uma Series no Pandas?",
                        "opcoes": [
                            "Uma tabela bidimensional",
                            "Um arquivo CSV",
                            "Um array unidimensional rotulado por um indice",
                            "Uma lista de DataFrames"
                        ],
                        "gabarito_idx": 2,
                        "dica": "Cada coluna de um DataFrame e uma Series."
                    }
                ]
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Importacao do Pandas",
                "descricao": "Preencha a convencao oficial de alias do Pandas.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Complete a instrucao com o alias oficial universalmente adotado para o pandas:",
                        "codigo_snippet": (
                            "import pandas as __BLANK_0__\n\n"
                            "df = __BLANK_0__.read_csv('vendas.csv')"
                        ),
                        "gabarito": "pd",
                        "dica": "Duas letras: 'p' e 'd'."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o indexador que acessa a primeira linha do DataFrame pela posicao:",
                        "codigo_snippet": "primeira_linha = df.__BLANK_0__[0]",
                        "gabarito": "iloc",
                        "dica": "Use o indexador baseado em posicao inteira."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o atributo que lista os nomes das colunas do DataFrame:",
                        "codigo_snippet": "print(df.__BLANK_0__)  # Index(['nome', 'idade', 'cidade'], dtype='object')",
                        "gabarito": "columns",
                        "dica": "O atributo tem o nome de 'colunas' em ingles."
                    }
                ]
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Leitura e Inspecao de Dados",
                "descricao": "Ordene as instrucoes para carregar um CSV e inspecionar informacoes das colunas.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize o fluxo de carga e inspecao de um arquivo CSV de clientes:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "import pandas as pd",
                            "df = pd.read_csv('clientes.csv')",
                            "print(df.shape)",
                            "print(df.info())"
                        ],
                        "dica": "Importe, leia o arquivo e chame os metodos de inspecao shape e info."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize o codigo que cria um DataFrame a partir de um dicionario e acessa um valor:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "import pandas as pd",
                            "dados = {'nome': ['Ana', 'Bia'], 'idade': [21, 34]}",
                            "df = pd.DataFrame(dados)",
                            "print(df.loc[0, 'nome'])  # Ana"
                        ],
                        "dica": "O DataFrame e construido a partir do dicionario ja declarado."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize o codigo que cria uma coluna calculada e ordena o DataFrame por ela:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "df = pd.read_csv('produtos.csv')",
                            "df['preco_com_desconto'] = df['preco'] * 0.9",
                            "df = df.sort_values('preco_com_desconto')",
                            "print(df.head())"
                        ],
                        "dica": "So e possivel ordenar por uma coluna depois que ela existe."
                    }
                ]
            },
            {
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Resumo Estatistico",
                "descricao": "Gere metricas rapidas (media, desvio, quartis) para todas as colunas numericas.",
                "xp": 150,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o metodo do Pandas que calcula automaticamente contagem, media, min e max:",
                        "codigo_snippet": (
                            "import pandas as pd\n"
                            "df = pd.read_csv('dados.csv')\n"
                            "resumo = df.__BLANK_0__()"
                        ),
                        "gabarito": "describe",
                        "dica": "Palavra em ingles para 'descrever'."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o metodo que conta quantas vezes cada valor aparece na coluna:",
                        "codigo_snippet": (
                            "contagem = df['cidade'].__BLANK_0__()\n"
                            "print(contagem)  # clientes por cidade"
                        ),
                        "gabarito": "value_counts",
                        "dica": "O nome significa 'contagem de valores'."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o metodo que exporta o DataFrame para um arquivo CSV:",
                        "codigo_snippet": "df.__BLANK_0__('relatorio.csv', index=False)",
                        "gabarito": "to_csv",
                        "dica": "E o caminho inverso de pd.read_csv()."
                    }
                ]
            }
        ]
    },
    {
        "titulo": "Limpeza, Filtros e Tratamento de Dados Ausentes",
        "descricao": "Identificacao de nulos com isna, preenchimento com fillna, remocao com dropna e filtros booleanos.",
        "nivel": "INTERMEDIARIO",
        "ordem_modulo": 3,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "Limpeza, Dados Ausentes (NaN) e Mascaras Booleanas",
                "descricao": "Estrategias profissionais de tratamento de nulos (imputacao vs descarte com dropna e fillna) e filtragem com operadores bitwise (&, |).",
                "xp": 50,
                "texto": (
                    "### Qualidade dos Dados e Valores Ausentes\n\n"
                    "Em cenarios reais de ciencia de dados, bases brutas contem celulas incompletas representadas pelo marcador especial de ponto flutuante **`NaN`** (Not a Number) ou `None`. O tratamento inadequado desses valores distorce medias, quebra modelos estatisticos e gera previsoes incorretas.\n\n"
                    "### Estrategias de Tratamento: Descarte vs Imputacao\n\n"
                    "1. **Deteccao de Nulos**: `df.isna().sum()` contabiliza a quantidade exata de celulas vazias por coluna.\n"
                    "2. **Descarte com `dropna()`**: Remove linhas ou colunas contendo nulos. Util quando a proporcao de registros incompletos e insignificante (< 2% da base):\n"
                    "   - `df.dropna(subset=['coluna_critica'])`: Remove apenas se a coluna essencial estiver vazia.\n"
                    "3. **Imputacao com `fillna()`**: Preenche posicoes vazias preservando o tamanho da amostra (com a media, mediana ou valor constante de sentinela).\n\n"
                    "### Filtros Avancados com Mascaras Booleanas\n\n"
                    "Para filtrar multiplas condicoes simultaneas no Pandas, **deve-se** utilizar operadores bitwise (`&` para E, `|` para OU) e envolver cada comparacao entre parenteses `(condicao1) & (condicao2)`:\n\n"
                    "```python\n"
                    "import pandas as pd\n"
                    "import numpy as np\n"
                    "\n"
                    "# 1. Criacao de DataFrame com valores ausentes intencionais\n"
                    "dados = pd.DataFrame({\n"
                    "    'cliente': ['Lucas', 'Ana', 'Marcos', 'Beatriz'],\n"
                    "    'idade': [24, np.nan, 32, np.nan],\n"
                    "    'score_credito': [750, 820, np.nan, 690],\n"
                    "    'renda': [4500.0, 9200.0, 3100.0, 6800.0]\n"
                    "})\n"
                    "\n"
                    "# 2. Imputacao da mediana na coluna 'idade'\n"
                    "mediana_idade = dados['idade'].median()\n"
                    "dados['idade'] = dados['idade'].fillna(mediana_idade)\n"
                    "\n"
                    "# 3. Filtragem composta com parenteses e operador bitwise &\n"
                    "mascara = (dados['idade'] >= 25) & (dados['renda'] > 5000.0)\n"
                    "clientes_selecionados = dados[mascara]\n"
                    "print(clientes_selecionados[['cliente', 'idade', 'renda']])\n"
                    "```\n\n"
                    "> **Armadilha Frequente**: Nunca utilize palavras-chave `and` ou `or` ao filtrar DataFrames inteiros. Em series do Pandas, o interpretador exige os operadores bitwise `&` e `|` obrigatoriamente."
                )
            },
            {
                "tipo": "MULTIPLA_ESCOLHA",
                "titulo": "Exercicio: Remocao de Linhas Nulas",
                "descricao": "Identifique o metodo para descartar registros ausentes.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual metodo e utilizado para excluir linhas que contenham valores nulos (NaN) no Pandas?",
                        "opcoes": ["dropna()", "remove_nulls()", "delete_empty()", "clean_na()"],
                        "gabarito_idx": 0,
                        "dica": "O termo 'drop' em conjunto com a sigla de 'Not Available' (NA)."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual o resultado de df['coluna'].isna().sum()?",
                        "opcoes": [
                            "A soma dos valores da coluna",
                            "A quantidade de valores nulos na coluna",
                            "A quantidade de valores nao nulos",
                            "Um DataFrame vazio"
                        ],
                        "gabarito_idx": 1,
                        "dica": "isna() gera True/False e, na soma, cada True vale 1."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual operador combina duas condicoes com E logico em um filtro booleano do Pandas?",
                        "opcoes": ["and", "&&", "&", "+"],
                        "gabarito_idx": 2,
                        "dica": "Em Series, os operadores logicos sao bit a bit; lembre-se de usar parenteses."
                    }
                ]
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Preenchimento de Nulos",
                "descricao": "Preencha os valores ausentes com a media da coluna.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Complete a chamada com o metodo utilizado para imputar valores em posicoes nulas:",
                        "codigo_snippet": (
                            "media_idade = df['idade'].mean()\n"
                            "df['idade'] = df['idade'].__BLANK_0__(media_idade)"
                        ),
                        "gabarito": "fillna",
                        "dica": "Juncao de 'fill' (preencher) com 'na'."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o metodo que remove as linhas repetidas do DataFrame:",
                        "codigo_snippet": "df = df.__BLANK_0__()  # remove linhas repetidas",
                        "gabarito": "drop_duplicates",
                        "dica": "O nome significa 'descartar duplicados'."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o metodo que converte o tipo da coluna para inteiro:",
                        "codigo_snippet": "df['idade'] = df['idade'].__BLANK_0__(int)",
                        "gabarito": "astype",
                        "dica": "O metodo transforma a coluna 'como tipo' informado."
                    }
                ]
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Filtro Booleano de Vendas",
                "descricao": "Ordene a aplicacao de um filtro de vendas de alto valor.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize o codigo para filtrar apenas vendas com valor superior a 1000 reais:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__"
                        ),
                        "blocos": [
                            "condicao = df['valor'] > 1000",
                            "vendas_altas = df[condicao]",
                            "print(f'Total de grandes vendas: {len(vendas_altas)}')"
                        ],
                        "dica": "Crie a mascara booleana, aplique a indexacao no DataFrame e exiba a quantidade."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize a limpeza: remover e-mails nulos, padronizar em minusculas e so entao eliminar duplicados:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "df = pd.read_csv('clientes.csv')",
                            "df = df.dropna(subset=['email'])",
                            "df['email'] = df['email'].str.lower()",
                            "df = df.drop_duplicates(subset=['email'])"
                        ],
                        "dica": "Padronize antes de deduplicar, ou 'Ana@x.com' e 'ana@x.com' serao tratados como diferentes."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize o preenchimento de salarios ausentes com a mediana e a verificacao final:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__"
                        ),
                        "blocos": [
                            "mediana = df['salario'].median()",
                            "df['salario'] = df['salario'].fillna(mediana)",
                            "print(df['salario'].isna().sum())  # 0"
                        ],
                        "dica": "Calcule a mediana antes de usa-la no preenchimento."
                    }
                ]
            },
            {
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Detecao de Nulos",
                "descricao": "Identifique quais celulas estao vazias no DataFrame.",
                "xp": 150,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a funcao que retorna uma mascara booleana identificando onde estao os valores nulos:",
                        "codigo_snippet": (
                            "total_nulos = df.__BLANK_0__().sum()\n"
                            "print(total_nulos)"
                        ),
                        "gabarito": "isna",
                        "dica": "Metodo de 4 letras que checa 'is NA' (ou isnull)."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o metodo que filtra as linhas cuja cidade esta na lista informada:",
                        "codigo_snippet": (
                            "cidades_alvo = ['Recife', 'Natal']\n"
                            "filtrados = df[df['cidade'].__BLANK_0__(cidades_alvo)]"
                        ),
                        "gabarito": "isin",
                        "dica": "O metodo verifica se o valor 'esta em' uma colecao."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o metodo que renomeia a coluna nm_cliente para nome:",
                        "codigo_snippet": "df = df.__BLANK_0__(columns={'nm_cliente': 'nome'})",
                        "gabarito": "rename",
                        "dica": "O metodo recebe um mapeamento de nome antigo para nome novo."
                    }
                ]
            }
        ]
    },
    {
        "titulo": "Agrupamentos, Agregacoes e Transformacoes (GroupBy)",
        "descricao": "Operacoes split-apply-combine com groupby, agregacoes multiplas e pivot tables.",
        "nivel": "INTERMEDIARIO",
        "ordem_modulo": 4,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "Agrupamentos, Agregacoes e o Paradigma Split-Apply-Combine",
                "descricao": "Como sintetizar dados em categorias com groupby, aplicar agregacoes customizadas com agg() e remodelar resultados com reset_index().",
                "xp": 50,
                "texto": (
                    "### O Paradigma Split-Apply-Combine\n\n"
                    "O agrupamento e uma das tecnicas analiticas mais frequentes no trabalho com dados. O Pandas implementa o paradigma formalizado por Hadley Wickham, dividido em tres etapas automaticas:\n\n"
                    "1. **Split (Dividir)**: O DataFrame original e particionado em subgrupos com base nos valores exclusivos de uma ou mais chaves (ex: categoria, ano, filial).\n"
                    "2. **Apply (Aplicar)**: Uma operacao ou funcao de agregacao e calculada de forma isolada para cada particao (ex: media, soma, variancia, contagem).\n"
                    "3. **Combine (Combinar)**: Os resultados de todos os grupos sao reunidos em uma nova estrutura de dados unificada.\n\n"
                    "### Agregacoes Multiplas e Customizadas com `.agg()`\n\n"
                    "Em vez de aplicar uma unica funcao com `.mean()` ou `.sum()`, o metodo `.agg()` permite extrair relatorios completos com diversas metricas estatisticas simultaneamente, inclusive aplicando operacoes diferentes por coluna atraves de um dicionario.\n\n"
                    "### O Papel de `.reset_index()`\n\n"
                    "Por padrao, as colunas agrupadas tornam-se o novo indice da tabela resultante. Para trazer essas categorias de volta como colunas normais de dados e facilitar joins futuros, encadeia-se `.reset_index()`.\n\n"
                    "```python\n"
                    "import pandas as pd\n"
                    "\n"
                    "dados_vendas = pd.DataFrame({\n"
                    "    'regiao': ['Sudeste', 'Sul', 'Sudeste', 'Sul', 'Nordeste', 'Sudeste'],\n"
                    "    'vendedor': ['Lucas', 'Carla', 'Lucas', 'Roberto', 'Maria', 'Carla'],\n"
                    "    'faturamento': [15000.0, 12000.0, 8500.0, 9400.0, 18000.0, 11000.0],\n"
                    "    'itens_vendidos': [30, 25, 18, 20, 42, 22]\n"
                    "})\n"
                    "\n"
                    "# 1. Agrupamento multi-coluna com agregacoes distintas (.agg)\n"
                    "relatorio = dados_vendas.groupby(['regiao']).agg({\n"
                    "    'faturamento': ['sum', 'mean'],\n"
                    "    'itens_vendidos': 'sum'\n"
                    "}).reset_index()\n"
                    "\n"
                    "print(relatorio)\n"
                    "```\n\n"
                    "> **Dica Pro**: Ao agrupar por multiplas colunas (`df.groupby(['ano', 'mes'])`), passar `as_index=False` no construtor do groupby (`df.groupby(..., as_index=False)`) evita a necessidade de chamar `.reset_index()` explicitamente ao final."
                )
            },
            {
                "tipo": "MULTIPLA_ESCOLHA",
                "titulo": "Exercicio: Agrupamento de Dados",
                "descricao": "Identifique o metodo principal de agrupamento no Pandas.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual metodo e utilizado no Pandas para dividir um DataFrame em grupos por valores de uma ou mais colunas?",
                        "opcoes": ["groupby()", "cluster()", "partition()", "categorize()"],
                        "gabarito_idx": 0,
                        "dica": "Mesmo nome da clausula SQL 'GROUP BY'."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "No paradigma split-apply-combine, o que acontece na etapa 'apply'?",
                        "opcoes": [
                            "Os dados sao divididos em grupos",
                            "Uma funcao (ex: soma, media) e aplicada a cada grupo",
                            "Os resultados sao combinados em uma estrutura",
                            "O DataFrame e salvo em disco"
                        ],
                        "gabarito_idx": 1,
                        "dica": "'Apply' significa aplicar."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual funcao do Pandas cria uma tabela dinamica com linhas, colunas e valores agregados?",
                        "opcoes": ["df.crosstab_all()", "df.table()", "df.matrix()", "pd.pivot_table()"],
                        "gabarito_idx": 3,
                        "dica": "E o equivalente a 'tabela dinamica' das planilhas."
                    }
                ]
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Agrupamento Simples",
                "descricao": "Preencha o metodo para calcular a soma de faturamento por departamento.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Complete o metodo de agrupamento que separa os colaboradores por setor:",
                        "codigo_snippet": (
                            "media_salarial = df.__BLANK_0__('departamento')['salario'].mean()\n"
                            "print(media_salarial)"
                        ),
                        "gabarito": "groupby",
                        "dica": "Palavra 'groupby' toda em minusculo."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a agregacao que conta os registros de cada cidade:",
                        "codigo_snippet": "qtd_por_cidade = df.groupby('cidade')['id'].__BLANK_0__()",
                        "gabarito": "count",
                        "dica": "O metodo significa 'contar'."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a funcao que cria a tabela dinamica de vendas por regiao e mes:",
                        "codigo_snippet": "tabela = pd.__BLANK_0__(df, values='vendas', index='regiao', columns='mes', aggfunc='sum')",
                        "gabarito": "pivot_table",
                        "dica": "O nome da funcao combina 'pivot' e 'table'."
                    }
                ]
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Metricas Consolidadas",
                "descricao": "Ordene a criacao de agrupamento com multiplas agregacoes estatisticas.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize o relatorio consolidado de vendas por filial:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__"
                        ),
                        "blocos": [
                            "grupos = df.groupby('filial')",
                            "relatorio = grupos['valor'].agg(['count', 'sum', 'mean'])",
                            "print(relatorio.reset_index())"
                        ],
                        "dica": "Crie o objeto agrupado, execute o agg com a lista de operacoes e resete o indice."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize o codigo que mostra as 3 categorias com maior faturamento:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__"
                        ),
                        "blocos": [
                            "totais = df.groupby('categoria')['valor'].sum()",
                            "totais = totais.sort_values(ascending=False)",
                            "print(totais.head(3))"
                        ],
                        "dica": "Agregue, ordene do maior para o menor e entao pegue os primeiros."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize o calculo de faturamento mensal agrupando por ano e mes:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "grupos = df.groupby(['ano', 'mes'])",
                            "faturamento = grupos['valor'].sum()",
                            "tabela = faturamento.reset_index()",
                            "print(tabela)"
                        ],
                        "dica": "reset_index transforma o indice do agrupamento de volta em colunas."
                    }
                ]
            },
            {
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Agregacao Especifica",
                "descricao": "Aplique o metodo agg para customizar as funcoes de agregacao.",
                "xp": 150,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a abreviacao do metodo de agregacao multipla do Pandas:",
                        "codigo_snippet": (
                            "resumo = df.groupby('categoria')['vendas'].__BLANK_0__(['sum', 'mean'])"
                        ),
                        "gabarito": "agg",
                        "dica": "Abreviacao de 'aggregate' com 3 letras."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o metodo que transforma o indice do agrupamento de volta em coluna:",
                        "codigo_snippet": "resumo = df.groupby('loja')['valor'].sum().__BLANK_0__()",
                        "gabarito": "reset_index",
                        "dica": "O metodo 'reinicia' o indice."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o metodo que calcula a media por setor mantendo o mesmo numero de linhas do DataFrame:",
                        "codigo_snippet": "df['media_setor'] = df.groupby('setor')['salario'].__BLANK_0__('mean')",
                        "gabarito": "transform",
                        "dica": "Diferente de agg, este metodo devolve um resultado alinhado a cada linha original."
                    }
                ]
            }
        ]
    },
    {
        "titulo": "Visualizacao de Dados com Matplotlib e Seaborn",
        "descricao": "Graficos de linha, barras, dispersao, histogramas e correlacao para storytelling com dados.",
        "nivel": "AVANCADO",
        "ordem_modulo": 5,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "Visualizacao Estatistica e Storytelling com Matplotlib e Seaborn",
                "descricao": "Hierarquia Figure/Axes, estilizacao com temas do Seaborn e escolha assertiva de graficos (barras, linhas, dispersao e boxplot).",
                "xp": 50,
                "texto": (
                    "### Comunicacao Visual e Storytelling com Dados\n\n"
                    "A visualizacao e a etapa culminante da analise de dados: transformar tabelas densas em graficos claros e intuitivos que orientam tomadas de decisao estrategicas. No ecossistema Python, duas bibliotecas formam a dupla definitiva:\n\n"
                    "1. **Matplotlib (`pyplot`)**: A biblioteca de fundacao. Fornece controle milimetrico sobre cada elemento visual (rotulos, eixos, legendas, dimensoes e fontes) atraves da hierarquia orientada a objetos `Figure` (a tela/janela inteira) e `Axes` (o subplot ou grafico individual).\n"
                    "2. **Seaborn**: Construida sobre o Matplotlib, abstrai dezenas de linhas de configuracao estatistica. Ela plota diretamente a partir de DataFrames do Pandas com paletas harmoniosas e tratamento de intervalos de confianca.\n\n"
                    "### Qual Grafico Escolher?\n\n"
                    "- **Barras (`sns.barplot`)**: Comparacao quantitativa entre categorias discretas.\n"
                    "- **Linhas (`plt.plot` / `sns.lineplot`)**: Evolucao temporal e series continuas.\n"
                    "- **Dispersao (`sns.scatterplot`)**: Correlacao e distribuicao bivariada entre variaveis continuas.\n"
                    "- **Boxplot (`sns.boxplot`)**: Deteccao de outliers, assimetria e dispersao dos quartis.\n\n"
                    "```python\n"
                    "import matplotlib.pyplot as plt\n"
                    "import seaborn as sns\n"
                    "import pandas as pd\n"
                    "\n"
                    "# 1. Definicao de estilo elegante com Seaborn\n"
                    "sns.set_theme(style='whitegrid', palette='muted')\n"
                    "\n"
                    "# 2. Criacao da estrutura orientada a objetos (Figure e Axes)\n"
                    "fig, ax = plt.subplots(figsize=(8, 4.5))\n"
                    "\n"
                    "dados_exemplo = pd.DataFrame({\n"
                    "    'mes': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai'],\n"
                    "    'satisfacao': [78, 82, 85, 84, 91]\n"
                    "})\n"
                    "\n"
                    "# 3. Plotagem no eixo especifico\n"
                    "sns.lineplot(data=dados_exemplo, x='mes', y='satisfacao', marker='o', ax=ax, color='#2b5c8f')\n"
                    "ax.set_title('Evolucao do Indice de Satisfacao dos Alunos', fontsize=14, pad=12)\n"
                    "ax.set_xlabel('Mes de Referencia')\n"
                    "ax.set_ylabel('Satisfacao (NPS %)')\n"
                    "\n"
                    "plt.tight_layout()\n"
                    "plt.show()\n"
                    "```\n\n"
                    "> **Boa Pratica de Storytelling**: Remova poluicao visual (chartjunk). Prefira titulos que expliquem a conclusao do grafico em vez de apenas rotular os eixos."
                )
            },
            {
                "tipo": "MULTIPLA_ESCOLHA",
                "titulo": "Exercicio: Exibicao do Grafico",
                "descricao": "Comando para renderizar a janela de visualizacao no Matplotlib.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual funcao do matplotlib.pyplot e chamada para exibir a janela com o grafico plotado?",
                        "opcoes": ["plt.show()", "plt.render()", "plt.display()", "plt.view()"],
                        "gabarito_idx": 0,
                        "dica": "Verbo em ingles para 'mostrar'."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual tipo de grafico e mais adequado para visualizar a distribuicao de uma unica variavel numerica?",
                        "opcoes": ["Grafico de pizza", "Histograma", "Grafico de linhas", "Mapa de calor"],
                        "gabarito_idx": 1,
                        "dica": "Ele agrupa os valores em faixas (bins) e mostra a frequencia de cada uma."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual funcao do Seaborn gera um mapa de calor, muito usado para matrizes de correlacao?",
                        "opcoes": ["sns.colormap()", "sns.matrix()", "sns.heatmap()", "sns.hotplot()"],
                        "gabarito_idx": 2,
                        "dica": "'Mapa de calor' em ingles e heat map."
                    }
                ]
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Grafico de Linhas",
                "descricao": "Complete a funcao para desenhar um grafico de series temporais (linhas).",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a funcao do pyplot utilizada para desenhar graficos de linha simples:",
                        "codigo_snippet": (
                            "import matplotlib.pyplot as plt\n"
                            "meses = [1, 2, 3, 4]\n"
                            "vendas = [100, 150, 130, 200]\n\n"
                            "plt.__BLANK_0__(meses, vendas)\n"
                            "plt.show()"
                        ),
                        "gabarito": "plot",
                        "dica": "Verbo classico 'plot' para tracar o grafico."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a funcao do pyplot que desenha um grafico de barras:",
                        "codigo_snippet": (
                            "categorias = ['A', 'B', 'C']\n"
                            "valores = [10, 25, 15]\n"
                            "plt.__BLANK_0__(categorias, valores)\n"
                            "plt.show()"
                        ),
                        "gabarito": "bar",
                        "dica": "E a palavra 'barra' em ingles."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a funcao que define o rotulo do eixo horizontal:",
                        "codigo_snippet": (
                            "plt.plot(meses, vendas)\n"
                            "plt.__BLANK_0__('Mes')\n"
                            "plt.ylabel('Vendas (R$)')"
                        ),
                        "gabarito": "xlabel",
                        "dica": "Compare com a funcao usada no eixo vertical."
                    }
                ]
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Grafico com Seaborn",
                "descricao": "Ordene a importacao, configuracao de estilo e geracao de grafico de dispersao.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as instrucoes para gerar um scatterplot com linha de tendencia:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "import seaborn as sns; import matplotlib.pyplot as plt",
                            "sns.set_theme(style='whitegrid')",
                            "sns.scatterplot(data=df, x='idade', y='salario')",
                            "plt.show()"
                        ],
                        "dica": "Importe as bibliotecas, configure o tema, plote a dispersao e chame plt.show()."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize o codigo que gera e exibe um mapa de calor das correlacoes:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "correlacao = df.corr(numeric_only=True)",
                            "sns.heatmap(correlacao, annot=True)",
                            "plt.title('Matriz de Correlacao')",
                            "plt.show()"
                        ],
                        "dica": "Calcule a correlacao, desenhe, adicione o titulo e so entao exiba."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize o codigo que cria a figura, plota um histograma, define o titulo e salva a imagem:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "fig, ax = plt.subplots(figsize=(8, 4))",
                            "ax.hist(df['idade'], bins=10)",
                            "ax.set_title('Distribuicao de Idades')",
                            "plt.savefig('idades.png')"
                        ],
                        "dica": "Os eixos (ax) precisam existir antes de receber o grafico."
                    }
                ]
            },
            {
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Titulo da Figura",
                "descricao": "Adicione o titulo descritivo na figura gerada.",
                "xp": 150,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a funcao do pyplot que define o titulo do grafico:",
                        "codigo_snippet": (
                            "import matplotlib.pyplot as plt\n"
                            "plt.plot([1, 2, 3], [10, 20, 30])\n"
                            "plt.__BLANK_0__('Crescimento Mensal de Acessos')\n"
                            "plt.show()"
                        ),
                        "gabarito": "title",
                        "dica": "Palavra em ingles para 'titulo'."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a funcao que salva o grafico em um arquivo de imagem:",
                        "codigo_snippet": (
                            "plt.plot([1, 2, 3], [10, 20, 30])\n"
                            "plt.__BLANK_0__('grafico.png', dpi=300)"
                        ),
                        "gabarito": "savefig",
                        "dica": "O nome combina 'save' e 'figure'."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a funcao que exibe a legenda com os rotulos de cada serie:",
                        "codigo_snippet": (
                            "plt.plot(x, y1, label='2025')\n"
                            "plt.plot(x, y2, label='2026')\n"
                            "plt.__BLANK_0__()\n"
                            "plt.show()"
                        ),
                        "gabarito": "legend",
                        "dica": "E a palavra 'legenda' em ingles."
                    }
                ]
            }
        ]
    }
]
# ==============================================================================
# TRILHAS POR INTERESSE
# Cobrem os interesses de userManagement/management/commands/seed_interesses.py
# que ainda nao tinham trilha propria. O campo "habilidade" usa o nome exato do
# interesse para que a recomendacao consiga relacionar trilha e interesse.
# ==============================================================================

# ==============================================================================
# TRILHA 4: JavaScript: Fundamentos
# ==============================================================================
trilha_javascript = Trilha.objects.create(
    titulo="JavaScript: Fundamentos",
    descricao="Domine variaveis, funcoes, arrays e objetos na linguagem que move a web.",
    habilidade="JavaScript",
    ativo=True
)

modulos_javascript = [
    {
        "titulo": "Variaveis, Tipos e Operadores",
        "descricao": "Declaracoes com let e const, tipos primitivos, comparacao estrita e template literals.",
        "nivel": "INICIANTE",
        "ordem_modulo": 1,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "Declarando Variaveis e Conhecendo os Tipos",
                "descricao": "Entenda let, const, os tipos primitivos do JavaScript e a diferenca entre == e ===.",
                "xp": 50,
                "texto": (
                    "### Variaveis em JavaScript\n\n"
                    "JavaScript possui tres formas de declarar variaveis, mas no codigo moderno usamos apenas duas:\n\n"
                    "- **`const`**: cria uma referencia que **nao pode ser reatribuida**. Deve ser a sua escolha padrao.\n"
                    "- **`let`**: cria uma variavel que pode receber um novo valor, com escopo de bloco (`{ }`).\n"
                    "- **`var`**: forma antiga, com escopo de funcao e comportamento de *hoisting* confuso. Evite.\n\n"
                    "### Tipos Primitivos\n\n"
                    "- **`number`**: inteiros e decimais usam o mesmo tipo (ex: `42`, `3.14`).\n"
                    "- **`string`**: textos entre aspas simples, duplas ou crases.\n"
                    "- **`boolean`**: `true` ou `false`.\n"
                    "- **`undefined`** e **`null`**: ausencia de valor (nao inicializado vs. vazio intencional).\n\n"
                    "### Comparacao Estrita\n\n"
                    "O operador `==` converte os tipos antes de comparar (`5 == '5'` e `true`), o que gera bugs sutis. "
                    "Prefira sempre `===`, que compara **valor e tipo** (`5 === '5'` e `false`).\n\n"
                    "```javascript\n"
                    "const curso = 'VariSkill';\n"
                    "let pontos = 10;\n"
                    "pontos = pontos + 5;\n"
                    "\n"
                    "// Template literals permitem interpolar valores com ${}\n"
                    "console.log(`Curso: ${curso} | Pontos: ${pontos}`);\n"
                    "\n"
                    "console.log(5 == '5');  // true  (conversao implicita)\n"
                    "console.log(5 === '5'); // false (tipos diferentes)\n"
                    "```\n\n"
                    "> **Dica Pro**: Comece declarando tudo com `const` e troque para `let` apenas quando precisar reatribuir o valor."
                )
            },
            {
                "tipo": "MULTIPLA_ESCOLHA",
                "titulo": "Exercicio: Declaracao de Variaveis",
                "descricao": "Identifique a palavra-chave que impede reatribuicao.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual palavra-chave declara uma variavel que nao pode ser reatribuida em JavaScript?",
                        "opcoes": ["const", "let", "var", "static"],
                        "gabarito_idx": 0,
                        "dica": "Pense na abreviacao de 'constante'."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual o resultado de typeof null em JavaScript?",
                        "opcoes": ["'null'", "'undefined'", "'object'", "'number'"],
                        "gabarito_idx": 2,
                        "dica": "E um comportamento historico (e famoso) da linguagem."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual a principal diferenca entre let e var?",
                        "opcoes": [
                            "Nao ha diferenca",
                            "var nao permite reatribuicao",
                            "let so aceita numeros",
                            "let tem escopo de bloco; var tem escopo de funcao"
                        ],
                        "gabarito_idx": 3,
                        "dica": "Pense no que acontece com a variavel fora de um bloco if ou for."
                    }
                ]
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Exibindo no Console",
                "descricao": "Complete o metodo que imprime mensagens no console.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a lacuna com o metodo do objeto console que exibe a mensagem de boas-vindas:",
                        "codigo_snippet": (
                            "const nome = 'Ana';\n"
                            "console.__BLANK_0__(`Ola, ${nome}!`);"
                        ),
                        "gabarito": "log",
                        "dica": "E o metodo mais usado para depuracao, com tres letras."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a funcao que converte a string em numero:",
                        "codigo_snippet": (
                            "const entrada = '42';\n"
                            "const idade = __BLANK_0__(entrada);\n"
                            "console.log(idade + 1); // 43"
                        ),
                        "gabarito": "Number",
                        "dica": "A funcao tem o mesmo nome do tipo numerico, com inicial maiuscula."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o operador que retorna o tipo de um valor como string:",
                        "codigo_snippet": (
                            "const ativo = true;\n"
                            "console.log(__BLANK_0__ ativo); // 'boolean'"
                        ),
                        "gabarito": "typeof",
                        "dica": "O operador junta as palavras 'type' e 'of'."
                    }
                ]
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Acumulando Pontos",
                "descricao": "Ordene as instrucoes para declarar, atualizar e exibir um total.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as linhas para iniciar o total, somar 10 pontos e exibir o resultado:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__"
                        ),
                        "blocos": [
                            "let total = 0;",
                            "total = total + 10;",
                            "console.log(total);"
                        ],
                        "dica": "A variavel precisa existir antes de ser atualizada e exibida."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as linhas para calcular o preco com 10% de desconto e exibi-lo:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "const preco = 50;",
                            "const desconto = preco * 0.1;",
                            "const precoFinal = preco - desconto;",
                            "console.log(`Total: R$ ${precoFinal}`);"
                        ],
                        "dica": "Cada constante depende do valor declarado anteriormente."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as linhas para subir o jogador de nivel e exibir a mensagem:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "let nivel = 1;",
                            "nivel += 1;",
                            "const mensagem = `Voce esta no nivel ${nivel}`;",
                            "console.log(mensagem); // Voce esta no nivel 2"
                        ],
                        "dica": "A mensagem deve ser montada depois que o nivel foi incrementado."
                    }
                ]
            },
            {
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Comparacao Estrita",
                "descricao": "Use o operador que compara valor e tipo.",
                "xp": 150,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o operador de igualdade estrita para que a comparacao entre o numero 5 e a string '5' resulte em false:",
                        "codigo_snippet": (
                            "const iguais = 5 __BLANK_0__ '5';\n"
                            "console.log(iguais); // false"
                        ),
                        "gabarito": "===",
                        "dica": "E o operador de igualdade com tres sinais de igual."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o operador de desigualdade estrita para que a comparacao resulte em true:",
                        "codigo_snippet": (
                            "const a = 10;\n"
                            "const b = '10';\n"
                            "console.log(a __BLANK_0__ b); // true"
                        ),
                        "gabarito": "!==",
                        "dica": "Os valores tem tipos diferentes; use a versao estrita de 'diferente'."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a palavra-chave que declara uma variavel que pode ser reatribuida, com escopo de bloco:",
                        "codigo_snippet": (
                            "__BLANK_0__ contador = 0;\n"
                            "contador = contador + 1;"
                        ),
                        "gabarito": "let",
                        "dica": "const nao permite reatribuicao e var nao tem escopo de bloco."
                    }
                ]
            }
        ]
    },
    {
        "titulo": "Funcoes, Arrays e Objetos",
        "descricao": "Arrow functions, metodos de array (map, filter) e manipulacao de objetos.",
        "nivel": "INTERMEDIARIO",
        "ordem_modulo": 2,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "Funcoes e Colecoes em JavaScript",
                "descricao": "Aprenda arrow functions, os metodos funcionais de array e a desestruturacao de objetos.",
                "xp": 50,
                "texto": (
                    "### Funcoes\n\n"
                    "Funcoes podem ser declaradas com `function` ou como **arrow functions** (`=>`), mais curtas e muito usadas em callbacks:\n\n"
                    "```javascript\n"
                    "function somar(a, b) {\n"
                    "  return a + b;\n"
                    "}\n"
                    "\n"
                    "const dobrar = (n) => n * 2; // retorno implicito\n"
                    "```\n\n"
                    "### Metodos de Array\n\n"
                    "- **`map`**: transforma cada elemento e devolve um **novo array** do mesmo tamanho.\n"
                    "- **`filter`**: devolve um novo array apenas com os elementos que passam no teste.\n"
                    "- **`reduce`**: acumula os elementos em um unico valor (ex: soma total).\n"
                    "- **`forEach`**: apenas percorre, sem retornar um novo array.\n\n"
                    "### Objetos e Desestruturacao\n\n"
                    "Objetos agrupam dados em pares chave-valor. A desestruturacao extrai propriedades em variaveis:\n\n"
                    "```javascript\n"
                    "const aluno = { nome: 'Rafa', xp: 320 };\n"
                    "const { nome, xp } = aluno;\n"
                    "\n"
                    "const notas = [6, 8, 10];\n"
                    "const aprovadas = notas.filter((nota) => nota >= 7); // [8, 10]\n"
                    "const bonus = notas.map((nota) => nota + 1);          // [7, 9, 11]\n"
                    "```\n\n"
                    "> **Dica Pro**: `map` e `filter` nao alteram o array original, o que torna o codigo mais previsivel."
                )
            },
            {
                "tipo": "MULTIPLA_ESCOLHA",
                "titulo": "Exercicio: Metodos de Array",
                "descricao": "Escolha o metodo que seleciona elementos por uma condicao.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual metodo de array cria um novo array apenas com os elementos que passam em um teste?",
                        "opcoes": ["filter", "map", "forEach", "push"],
                        "gabarito_idx": 0,
                        "dica": "O nome do metodo significa 'filtrar' em ingles."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "O que o metodo reduce faz em um array?",
                        "opcoes": [
                            "Remove o ultimo elemento",
                            "Acumula os elementos em um unico valor",
                            "Ordena o array",
                            "Cria uma copia rasa"
                        ],
                        "gabarito_idx": 1,
                        "dica": "Pense em somar todos os itens de uma lista."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Como acessar a propriedade nome do objeto const aluno = { nome: 'Ana' }?",
                        "opcoes": ["aluno->nome", "aluno::nome", "aluno.nome", "aluno#nome"],
                        "gabarito_idx": 2,
                        "dica": "JavaScript usa a notacao de ponto (ou colchetes)."
                    }
                ]
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Arrow Function",
                "descricao": "Complete a sintaxe de uma arrow function.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a lacuna com o operador que define uma arrow function:",
                        "codigo_snippet": (
                            "const dobro = (n) __BLANK_0__ n * 2;\n"
                            "console.log(dobro(4)); // 8"
                        ),
                        "gabarito": "=>",
                        "dica": "O operador lembra uma seta."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o metodo de array que soma todos os valores a partir do acumulador 0:",
                        "codigo_snippet": (
                            "const total = [10, 20, 30].__BLANK_0__((acc, n) => acc + n, 0);\n"
                            "console.log(total); // 60"
                        ),
                        "gabarito": "reduce",
                        "dica": "O metodo 'reduz' o array a um unico valor."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a desestruturacao que extrai a propriedade nome do objeto:",
                        "codigo_snippet": (
                            "const usuario = { nome: 'Rui', idade: 30 };\n"
                            "const { __BLANK_0__ } = usuario;\n"
                            "console.log(nome); // Rui"
                        ),
                        "gabarito": "nome",
                        "dica": "O nome da variavel deve ser igual ao nome da propriedade."
                    }
                ]
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Filtrando Numeros Pares",
                "descricao": "Ordene as instrucoes para filtrar e exibir os numeros pares.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as linhas para criar a lista, filtrar os pares e exibir o resultado:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__"
                        ),
                        "blocos": [
                            "const numeros = [1, 2, 3, 4];",
                            "const pares = numeros.filter((n) => n % 2 === 0);",
                            "console.log(pares);"
                        ],
                        "dica": "Os dados de origem vem primeiro, depois a transformacao e por fim a exibicao."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as linhas para obter apenas o nome dos produtos que custam mais de 10:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "const produtos = [{ nome: 'Livro', preco: 40 }, { nome: 'Caneta', preco: 5 }];",
                            "const caros = produtos.filter((p) => p.preco > 10);",
                            "const nomes = caros.map((p) => p.nome);",
                            "console.log(nomes); // ['Livro']"
                        ],
                        "dica": "Filtre primeiro e transforme depois."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize a funcao que calcula a media de uma lista de notas:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "  __SLOT_1__\n"
                            "  __SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "function calcularMedia(notas) {",
                            "const soma = notas.reduce((a, b) => a + b, 0);",
                            "return soma / notas.length;",
                            "}"
                        ],
                        "dica": "A soma precisa existir antes de ser dividida."
                    }
                ]
            },
            {
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Transformando com map",
                "descricao": "Gere um novo array com o quadrado de cada numero.",
                "xp": 150,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o metodo de array que transforma cada elemento e devolve um novo array:",
                        "codigo_snippet": (
                            "const quadrados = [1, 2, 3].__BLANK_0__((n) => n * n);\n"
                            "console.log(quadrados); // [1, 4, 9]"
                        ),
                        "gabarito": "map",
                        "dica": "O metodo 'mapeia' cada valor para um novo valor."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o metodo de array que retorna o primeiro elemento que satisfaz a condicao:",
                        "codigo_snippet": (
                            "const usuarios = [{ id: 1 }, { id: 2 }];\n"
                            "const encontrado = usuarios.__BLANK_0__((u) => u.id === 2);\n"
                            "console.log(encontrado); // { id: 2 }"
                        ),
                        "gabarito": "find",
                        "dica": "O metodo 'encontra' um unico item."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o operador que espalha os itens de um array dentro de outro:",
                        "codigo_snippet": (
                            "const base = [1, 2];\n"
                            "const completa = [__BLANK_0__base, 3];\n"
                            "console.log(completa); // [1, 2, 3]"
                        ),
                        "gabarito": "...",
                        "dica": "E o operador spread, formado por tres caracteres iguais."
                    }
                ]
            }
        ]
    }
]

# ==============================================================================
# TRILHA 5: TypeScript: Tipagem Estatica
# ==============================================================================
trilha_typescript = Trilha.objects.create(
    titulo="TypeScript: Tipagem Estatica",
    descricao="Escreva JavaScript mais seguro com tipos, interfaces e generics.",
    habilidade="TypeScript",
    ativo=True
)

modulos_typescript = [
    {
        "titulo": "Tipos Basicos e Anotacoes",
        "descricao": "Anotacoes de tipo, tipos primitivos, arrays, union types e a diferenca entre any e unknown.",
        "nivel": "INICIANTE",
        "ordem_modulo": 1,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "O que o TypeScript Adiciona ao JavaScript",
                "descricao": "Entenda a compilacao para JavaScript, as anotacoes de tipo e os union types.",
                "xp": 50,
                "texto": (
                    "### TypeScript em Uma Frase\n\n"
                    "TypeScript e um **superconjunto do JavaScript** que adiciona tipos estaticos. O compilador (`tsc`) verifica os tipos e "
                    "gera JavaScript puro: os tipos sao **removidos** no codigo final (*type erasure*), entao nao existem em tempo de execucao.\n\n"
                    "### Anotacoes de Tipo\n\n"
                    "- **Primitivos**: `string`, `number`, `boolean`.\n"
                    "- **Arrays**: `number[]` ou `Array<number>`.\n"
                    "- **Union types**: um valor que pode ter mais de um tipo, como `string | number`.\n"
                    "- **`any`**: desliga a verificacao (evite). **`unknown`**: aceita qualquer valor, mas exige checagem antes do uso.\n\n"
                    "```typescript\n"
                    "let nome: string = 'Bia';\n"
                    "let idade: number = 21;\n"
                    "const notas: number[] = [7, 8.5, 10];\n"
                    "\n"
                    "let codigo: string | number = 'A1';\n"
                    "codigo = 42; // permitido pelo union type\n"
                    "\n"
                    "function saudar(pessoa: string): string {\n"
                    "  return `Ola, ${pessoa}`;\n"
                    "}\n"
                    "\n"
                    "saudar(10); // Erro de compilacao: number nao e string\n"
                    "```\n\n"
                    "> **Dica Pro**: Na maioria das vezes o TypeScript **infere** o tipo sozinho (`let x = 5` ja e `number`). Anote parametros e retornos de funcoes."
                )
            },
            {
                "tipo": "MULTIPLA_ESCOLHA",
                "titulo": "Exercicio: Compilacao do TypeScript",
                "descricao": "Entenda o que acontece com os tipos apos a compilacao.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "O que acontece com as anotacoes de tipo do TypeScript quando o codigo e compilado para JavaScript?",
                        "opcoes": [
                            "Sao removidas (type erasure)",
                            "Viram validacoes em tempo de execucao",
                            "Sao convertidas em comentarios obrigatorios",
                            "Geram classes JavaScript equivalentes"
                        ],
                        "gabarito_idx": 0,
                        "dica": "Os tipos so existem durante a verificacao do compilador."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual a diferenca entre any e unknown em TypeScript?",
                        "opcoes": [
                            "Sao identicos",
                            "unknown exige verificacao de tipo antes do uso; any desativa a checagem",
                            "any exige verificacao de tipo antes do uso",
                            "unknown so aceita strings"
                        ],
                        "gabarito_idx": 1,
                        "dica": "unknown e a alternativa segura ao any."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Como declarar um array de strings em TypeScript?",
                        "opcoes": [
                            "let nomes: [string];",
                            "let nomes: Array<string>[];",
                            "let nomes: string[];",
                            "let nomes: str[];"
                        ],
                        "gabarito_idx": 2,
                        "dica": "Coloque colchetes logo apos o tipo dos elementos."
                    }
                ]
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Anotando uma Variavel",
                "descricao": "Complete a anotacao de tipo numerico.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a lacuna com o tipo adequado para armazenar a idade do estudante:",
                        "codigo_snippet": (
                            "let idade: __BLANK_0__ = 25;"
                        ),
                        "gabarito": "number",
                        "dica": "Em TypeScript, inteiros e decimais compartilham o mesmo tipo."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o tipo adequado para armazenar um valor verdadeiro ou falso:",
                        "codigo_snippet": "let ativo: __BLANK_0__ = true;",
                        "gabarito": "boolean",
                        "dica": "O nome do tipo homenageia George Boole."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o tipo de retorno de uma funcao que nao devolve nenhum valor:",
                        "codigo_snippet": (
                            "function registrarLog(msg: string): __BLANK_0__ {\n"
                            "  console.log(msg);\n"
                            "}"
                        ),
                        "gabarito": "void",
                        "dica": "O tipo representa 'vazio'."
                    }
                ]
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Funcao Tipada",
                "descricao": "Ordene a declaracao de uma funcao com parametro e retorno tipados.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as linhas para declarar a funcao saudar e utiliza-la em seguida:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "function saudar(nome: string): string {",
                            "return `Ola, ${nome}`;",
                            "}",
                            "console.log(saudar('Bia'));"
                        ],
                        "dica": "A assinatura abre a funcao, o retorno fica dentro do bloco e a chamada vem depois do fechamento."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize a funcao que recebe um valor unknown e so usa .length depois de verificar o tipo:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "  __SLOT_1__\n"
                            "  __SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "function tamanho(valor: unknown): number {",
                            "if (typeof valor === 'string') return valor.length;",
                            "return 0;",
                            "}"
                        ],
                        "dica": "A verificacao com typeof (narrowing) deve vir antes do retorno padrao."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as linhas que declaram um tipo literal e o utilizam:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "type Status = 'ativo' | 'inativo';",
                            "let status: Status = 'ativo';",
                            "status = 'inativo';",
                            "console.log(status);"
                        ],
                        "dica": "O tipo precisa ser declarado antes de ser usado na anotacao."
                    }
                ]
            },
            {
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Union Type",
                "descricao": "Permita que o identificador seja texto ou numero.",
                "xp": 150,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o operador que cria um union type, permitindo string ou number:",
                        "codigo_snippet": (
                            "let id: string __BLANK_0__ number;\n"
                            "id = 'abc';\n"
                            "id = 123;"
                        ),
                        "gabarito": "|",
                        "dica": "E o mesmo caractere usado como 'ou' bit a bit."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o tipo do segundo elemento da tupla:",
                        "codigo_snippet": "let coordenada: [number, __BLANK_0__] = [10, 'norte'];",
                        "gabarito": "string",
                        "dica": "Observe o tipo do valor 'norte'."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o simbolo que torna o parametro nome opcional:",
                        "codigo_snippet": (
                            "function saudar(nome__BLANK_0__: string) {\n"
                            "  return `Ola, ${nome ?? 'visitante'}`;\n"
                            "}"
                        ),
                        "gabarito": "?",
                        "dica": "E o mesmo simbolo usado para propriedades opcionais em interfaces."
                    }
                ]
            }
        ]
    },
    {
        "titulo": "Interfaces, Types e Generics",
        "descricao": "Modelagem de objetos com interface e type, propriedades opcionais e funcoes genericas.",
        "nivel": "INTERMEDIARIO",
        "ordem_modulo": 2,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "Modelando Dados com Interfaces e Generics",
                "descricao": "Descreva o formato de objetos e crie funcoes reutilizaveis para qualquer tipo.",
                "xp": 50,
                "texto": (
                    "### Interfaces e Type Aliases\n\n"
                    "Uma `interface` descreve o **formato de um objeto**. Um `type` pode fazer o mesmo e tambem nomear unions e outros tipos compostos.\n\n"
                    "- **Propriedade opcional**: `email?: string` pode estar ausente.\n"
                    "- **Somente leitura**: `readonly id: number` nao pode ser alterado apos a criacao.\n\n"
                    "```typescript\n"
                    "interface Usuario {\n"
                    "  readonly id: number;\n"
                    "  nome: string;\n"
                    "  email?: string;\n"
                    "}\n"
                    "\n"
                    "type Status = 'ATIVO' | 'INATIVO';\n"
                    "```\n\n"
                    "### Generics\n\n"
                    "Generics permitem escrever codigo que funciona com **qualquer tipo** sem perder a verificacao. "
                    "O parametro de tipo (por convencao `T`) e definido entre `< >`:\n\n"
                    "```typescript\n"
                    "function primeiro<T>(itens: T[]): T | undefined {\n"
                    "  return itens[0];\n"
                    "}\n"
                    "\n"
                    "const n = primeiro([1, 2, 3]);      // n: number | undefined\n"
                    "const s = primeiro(['a', 'b']);     // s: string | undefined\n"
                    "```\n\n"
                    "> **Dica Pro**: Use `interface` para objetos que podem ser estendidos e `type` para unions e composicoes."
                )
            },
            {
                "tipo": "MULTIPLA_ESCOLHA",
                "titulo": "Exercicio: Propriedades Opcionais",
                "descricao": "Identifique a sintaxe de propriedade opcional.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Como indicar que a propriedade 'email' de uma interface e opcional?",
                        "opcoes": ["email?: string", "email!: string", "optional email: string", "email: string | required"],
                        "gabarito_idx": 0,
                        "dica": "Um ponto de interrogacao logo apos o nome da propriedade."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual palavra-chave permite que uma interface herde as propriedades de outra?",
                        "opcoes": ["implements", "inherits", "with", "extends"],
                        "gabarito_idx": 3,
                        "dica": "E a mesma palavra usada em heranca de classes."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "O que o tipo utilitario Partial<Usuario> produz?",
                        "opcoes": [
                            "Um tipo com todas as propriedades de Usuario opcionais",
                            "Um tipo apenas com metade das propriedades",
                            "Um tipo com todas as propriedades readonly",
                            "Um array de Usuario"
                        ],
                        "gabarito_idx": 0,
                        "dica": "'Parcial' significa que nem todas as propriedades precisam estar presentes."
                    }
                ]
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Declarando uma Interface",
                "descricao": "Complete a palavra-chave que define o formato de um objeto.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a lacuna com a palavra-chave que declara o contrato de um objeto Usuario:",
                        "codigo_snippet": (
                            "__BLANK_0__ Usuario {\n"
                            "  nome: string;\n"
                            "  idade: number;\n"
                            "}"
                        ),
                        "gabarito": "interface",
                        "dica": "A palavra significa 'interface' em ingles."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a palavra-chave que cria um alias de tipo:",
                        "codigo_snippet": "__BLANK_0__ Ponto = { x: number; y: number };",
                        "gabarito": "type",
                        "dica": "E a alternativa a interface que usa o sinal de igual."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o modificador que impede a alteracao da propriedade apos a criacao do objeto:",
                        "codigo_snippet": (
                            "interface Config {\n"
                            "  __BLANK_0__ apiUrl: string;\n"
                            "}"
                        ),
                        "gabarito": "readonly",
                        "dica": "O modificador significa 'somente leitura'."
                    }
                ]
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Funcao Generica",
                "descricao": "Ordene a declaracao e o uso de uma funcao generica.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as linhas para declarar a funcao generica primeiro e chama-la com uma lista de numeros:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "function primeiro<T>(itens: T[]): T | undefined {",
                            "return itens[0];",
                            "}",
                            "const n = primeiro([1, 2, 3]);"
                        ],
                        "dica": "Declare a funcao completa antes de usa-la."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as linhas para declarar Pessoa, estende-la em Aluno e criar um objeto:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "interface Pessoa { nome: string; }",
                            "interface Aluno extends Pessoa { ra: string; }",
                            "const aluno: Aluno = { nome: 'Lia', ra: '123' };",
                            "console.log(aluno.nome);"
                        ],
                        "dica": "A interface base precisa existir antes de ser estendida."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as linhas para declarar a interface generica Caixa e usa-la com number:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "  __SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "interface Caixa<T> {",
                            "conteudo: T;",
                            "}",
                            "const caixa: Caixa<number> = { conteudo: 42 };"
                        ],
                        "dica": "Feche a interface antes de usa-la."
                    }
                ]
            },
            {
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Parametro de Tipo",
                "descricao": "Declare o parametro generico de uma funcao identidade.",
                "xp": 150,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o nome do parametro de tipo generico usado pela funcao identidade:",
                        "codigo_snippet": (
                            "function identidade<__BLANK_0__>(valor: T): T {\n"
                            "  return valor;\n"
                            "}"
                        ),
                        "gabarito": "T",
                        "dica": "Por convencao, o primeiro parametro generico e uma letra maiuscula usada no proprio parametro valor."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a palavra-chave que restringe T a tipos que possuem a propriedade length:",
                        "codigo_snippet": (
                            "function obterTamanho<T __BLANK_0__ { length: number }>(item: T): number {\n"
                            "  return item.length;\n"
                            "}"
                        ),
                        "gabarito": "extends",
                        "dica": "A restricao de generics usa a mesma palavra da heranca."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o tipo generico nativo equivalente a number[]:",
                        "codigo_snippet": "const ids: __BLANK_0__<number> = [1, 2, 3];",
                        "gabarito": "Array",
                        "dica": "E o nome do construtor de listas do JavaScript."
                    }
                ]
            }
        ]
    }
]

# ==============================================================================
# TRILHA 6: Frontend: HTML, CSS e React
# ==============================================================================
trilha_frontend = Trilha.objects.create(
    titulo="Frontend: HTML, CSS e React",
    descricao="Construa interfaces acessiveis com HTML semantico, layouts com Flexbox e componentes React.",
    habilidade="Frontend",
    ativo=True
)

modulos_frontend = [
    {
        "titulo": "HTML Semantico e CSS",
        "descricao": "Estrutura semantica, acessibilidade, box model e layouts com Flexbox.",
        "nivel": "INICIANTE",
        "ordem_modulo": 1,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "Estrutura e Estilo de Paginas Web",
                "descricao": "Use as tags semanticas certas e organize elementos na tela com Flexbox.",
                "xp": 50,
                "texto": (
                    "### HTML Semantico\n\n"
                    "Tags semanticas descrevem o **significado** do conteudo, o que melhora acessibilidade e SEO:\n\n"
                    "- **`<header>`** e **`<footer>`**: cabecalho e rodape.\n"
                    "- **`<nav>`**: bloco de navegacao.\n"
                    "- **`<main>`**: conteudo principal e unico da pagina (apenas um por pagina).\n"
                    "- **`<section>`** e **`<article>`**: agrupamentos tematicos e conteudos independentes.\n\n"
                    "Imagens devem ter o atributo `alt`, que descreve a imagem para leitores de tela.\n\n"
                    "### Box Model e Flexbox\n\n"
                    "Todo elemento e uma caixa formada por **content**, **padding**, **border** e **margin**. "
                    "Para alinhar elementos, o **Flexbox** e a ferramenta mais pratica:\n\n"
                    "```css\n"
                    ".barra {\n"
                    "  display: flex;            /* ativa o Flexbox */\n"
                    "  justify-content: space-between; /* eixo principal */\n"
                    "  align-items: center;      /* eixo cruzado */\n"
                    "  gap: 16px;\n"
                    "}\n"
                    "```\n\n"
                    "```html\n"
                    "<header class=\"barra\">\n"
                    "  <img src=\"logo.png\" alt=\"Logo do VariSkill\">\n"
                    "  <nav><a href=\"/trilhas\">Trilhas</a></nav>\n"
                    "</header>\n"
                    "<main>...</main>\n"
                    "```\n\n"
                    "> **Dica Pro**: Antes de usar uma `<div>`, pergunte se existe uma tag semantica que descreva melhor aquele conteudo."
                )
            },
            {
                "tipo": "MULTIPLA_ESCOLHA",
                "titulo": "Exercicio: Tags Semanticas",
                "descricao": "Reconheca a tag do conteudo principal.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual tag HTML representa o conteudo principal e unico de uma pagina?",
                        "opcoes": ["<main>", "<div>", "<section>", "<body>"],
                        "gabarito_idx": 0,
                        "dica": "A palavra significa 'principal' em ingles."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "No box model do CSS, qual propriedade define o espaco interno entre o conteudo e a borda?",
                        "opcoes": ["margin", "padding", "border", "outline"],
                        "gabarito_idx": 1,
                        "dica": "margin e o espaco externo; procure o interno."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual propriedade do Flexbox alinha os itens no eixo cruzado?",
                        "opcoes": ["justify-content", "flex-wrap", "align-items", "flex-direction"],
                        "gabarito_idx": 2,
                        "dica": "justify-content atua no eixo principal."
                    }
                ]
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Ativando o Flexbox",
                "descricao": "Complete a propriedade que transforma o container em flex.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o valor da propriedade display que ativa o Flexbox no container:",
                        "codigo_snippet": (
                            ".container {\n"
                            "  display: __BLANK_0__;\n"
                            "  justify-content: center;\n"
                            "}"
                        ),
                        "gabarito": "flex",
                        "dica": "O valor tem o mesmo nome do modelo de layout."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o valor de flex-direction que empilha os itens verticalmente:",
                        "codigo_snippet": (
                            ".menu {\n"
                            "  display: flex;\n"
                            "  flex-direction: __BLANK_0__;\n"
                            "}"
                        ),
                        "gabarito": "column",
                        "dica": "O oposto de row."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o atributo que associa o label ao campo de id email:",
                        "codigo_snippet": (
                            "<label __BLANK_0__=\"email\">E-mail</label>\n"
                            "<input id=\"email\" type=\"email\">"
                        ),
                        "gabarito": "for",
                        "dica": "O atributo indica 'para qual' campo o rotulo serve."
                    }
                ]
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Montando a Navegacao",
                "descricao": "Ordene as tags para criar um bloco de navegacao.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as linhas para abrir o bloco de navegacao, inserir o link e fecha-lo:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__"
                        ),
                        "blocos": [
                            "<nav>",
                            "<a href=\"/\">Inicio</a>",
                            "</nav>"
                        ],
                        "dica": "Toda tag aberta precisa envolver seu conteudo antes de ser fechada."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as linhas para criar um artigo com titulo e paragrafo:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "<article>",
                            "<h2>Novidades da Plataforma</h2>",
                            "<p>Novas trilhas foram publicadas.</p>",
                            "</article>"
                        ],
                        "dica": "O titulo vem antes do texto, e tudo fica dentro do article."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as linhas do formulario de login:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "<form action=\"/login\" method=\"post\">",
                            "<input id=\"senha\" type=\"password\">",
                            "<button type=\"submit\">Entrar</button>",
                            "</form>"
                        ],
                        "dica": "O botao de envio costuma ser o ultimo elemento do formulario."
                    }
                ]
            },
            {
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Imagem Acessivel",
                "descricao": "Adicione o texto alternativo de uma imagem.",
                "xp": 150,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o atributo que descreve a imagem para leitores de tela:",
                        "codigo_snippet": (
                            "<img src=\"logo.png\" __BLANK_0__=\"Logo do VariSkill\">"
                        ),
                        "gabarito": "alt",
                        "dica": "E a abreviacao de 'alternative'."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o valor de box-sizing que inclui padding e borda na largura total do elemento:",
                        "codigo_snippet": (
                            "* {\n"
                            "  box-sizing: __BLANK_0__;\n"
                            "}"
                        ),
                        "gabarito": "border-box",
                        "dica": "O valor diz que a caixa vai ate a borda."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o valor de justify-content que coloca o primeiro item a esquerda e o ultimo a direita:",
                        "codigo_snippet": (
                            ".barra {\n"
                            "  display: flex;\n"
                            "  justify-content: __BLANK_0__;\n"
                            "}"
                        ),
                        "gabarito": "space-between",
                        "dica": "O espaco livre e distribuido 'entre' os itens."
                    }
                ]
            }
        ]
    },
    {
        "titulo": "Componentes e Estado com React",
        "descricao": "Componentes funcionais, JSX, props, estado com useState e renderizacao de listas.",
        "nivel": "INTERMEDIARIO",
        "ordem_modulo": 2,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "Pensando em Componentes",
                "descricao": "Crie componentes reutilizaveis com props e estado.",
                "xp": 50,
                "texto": (
                    "### Componentes e JSX\n\n"
                    "No React, a interface e dividida em **componentes**: funcoes que recebem dados (**props**) e retornam **JSX**, "
                    "uma sintaxe parecida com HTML dentro do JavaScript.\n\n"
                    "```jsx\n"
                    "function Saudacao({ nome }) {\n"
                    "  return <h1>Ola, {nome}!</h1>;\n"
                    "}\n"
                    "\n"
                    "<Saudacao nome=\"Lia\" />\n"
                    "```\n\n"
                    "### Estado com useState\n\n"
                    "Props vem de fora; **estado** e a memoria interna do componente. Quando o estado muda, o React renderiza o componente novamente:\n\n"
                    "```jsx\n"
                    "import { useState } from 'react';\n"
                    "\n"
                    "function Contador() {\n"
                    "  const [contador, setContador] = useState(0);\n"
                    "  return (\n"
                    "    <button onClick={() => setContador(contador + 1)}>\n"
                    "      Cliques: {contador}\n"
                    "    </button>\n"
                    "  );\n"
                    "}\n"
                    "```\n\n"
                    "### Listas e a Prop key\n\n"
                    "Ao renderizar listas com `map`, cada item precisa de uma prop **`key`** unica e estavel, para o React identificar o que mudou.\n\n"
                    "> **Dica Pro**: Nunca altere o estado diretamente (`contador++`); sempre use a funcao setter."
                )
            },
            {
                "tipo": "MULTIPLA_ESCOLHA",
                "titulo": "Exercicio: Hooks do React",
                "descricao": "Escolha o hook que guarda estado local.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual hook do React e usado para guardar estado local em um componente funcional?",
                        "opcoes": ["useState", "useEffect", "useRef", "useContext"],
                        "gabarito_idx": 0,
                        "dica": "O nome do hook contem a palavra 'estado' em ingles."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "O que sao props em React?",
                        "opcoes": [
                            "Estado interno e mutavel do componente",
                            "Dados passados do componente pai para o filho, somente leitura",
                            "Funcoes de ciclo de vida",
                            "Estilos CSS do componente"
                        ],
                        "gabarito_idx": 1,
                        "dica": "Pense em como um componente recebe configuracoes de quem o renderiza."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Quando o efeito declarado com useEffect(() => {...}, []) e executado?",
                        "opcoes": [
                            "A cada renderizacao",
                            "Nunca",
                            "Apenas quando o estado muda",
                            "Apenas uma vez, apos a primeira renderizacao"
                        ],
                        "gabarito_idx": 3,
                        "dica": "O array de dependencias vazio significa que nada dispara uma nova execucao."
                    }
                ]
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Criando um Estado",
                "descricao": "Complete a criacao de um estado numerico.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o hook que cria o estado contador iniciando em zero:",
                        "codigo_snippet": (
                            "const [contador, setContador] = __BLANK_0__(0);"
                        ),
                        "gabarito": "useState",
                        "dica": "Ele retorna um par: o valor atual e a funcao para atualiza-lo."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o evento que executa a funcao ao clicar no botao:",
                        "codigo_snippet": (
                            "<button __BLANK_0__={() => setContador(contador + 1)}>\n"
                            "  Incrementar\n"
                            "</button>"
                        ),
                        "gabarito": "onClick",
                        "dica": "Eventos no JSX usam camelCase."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o atributo JSX equivalente ao class do HTML:",
                        "codigo_snippet": "<div __BLANK_0__=\"cartao\">Conteudo</div>",
                        "gabarito": "className",
                        "dica": "class e palavra reservada em JavaScript."
                    }
                ]
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Componente com Props",
                "descricao": "Ordene as linhas de um componente funcional.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as linhas para declarar o componente Saudacao, que recebe a prop nome:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__"
                        ),
                        "blocos": [
                            "function Saudacao({ nome }) {",
                            "return <h1>Ola, {nome}!</h1>;",
                            "}"
                        ],
                        "dica": "A assinatura da funcao vem primeiro, o JSX e retornado dentro dela."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as linhas do componente Contador:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "  __SLOT_1__\n"
                            "  __SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "function Contador() {",
                            "const [valor, setValor] = useState(0);",
                            "return <button onClick={() => setValor(valor + 1)}>{valor}</button>;",
                            "}"
                        ],
                        "dica": "Hooks sao declarados antes do return."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as linhas que carregam a lista de cursos ao montar o componente:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "  __SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "const [cursos, setCursos] = useState([]);",
                            "useEffect(() => {",
                            "fetch('/api/cursos').then((r) => r.json()).then(setCursos);",
                            "}, []);"
                        ],
                        "dica": "O estado precisa existir antes do efeito que o atualiza."
                    }
                ]
            },
            {
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Renderizando Listas",
                "descricao": "Identifique cada item de uma lista renderizada.",
                "xp": 150,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a prop especial que identifica cada item ao renderizar uma lista no React:",
                        "codigo_snippet": (
                            "{itens.map((item) => (\n"
                            "  <li __BLANK_0__={item.id}>{item.nome}</li>\n"
                            "))}"
                        ),
                        "gabarito": "key",
                        "dica": "A palavra significa 'chave' em ingles."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o hook que sincroniza o titulo da pagina sempre que o contador mudar:",
                        "codigo_snippet": (
                            "__BLANK_0__(() => {\n"
                            "  document.title = `Voce clicou ${contador} vezes`;\n"
                            "}, [contador]);"
                        ),
                        "gabarito": "useEffect",
                        "dica": "E o hook para efeitos colaterais."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o operador que renderiza o paragrafo apenas enquanto carregando for true:",
                        "codigo_snippet": "{carregando __BLANK_0__ <p>Carregando...</p>}",
                        "gabarito": "&&",
                        "dica": "E o operador logico E do JavaScript."
                    }
                ]
            }
        ]
    }
]

# ==============================================================================
# TRILHA 7: Banco de Dados: SQL e Modelagem
# ==============================================================================
trilha_banco = Trilha.objects.create(
    titulo="Banco de Dados: SQL e Modelagem",
    descricao="Consulte, filtre e relacione dados com SQL e modele tabelas relacionais.",
    habilidade="Banco de Dados",
    ativo=True
)

modulos_banco = [
    {
        "titulo": "Consultas SQL Essenciais",
        "descricao": "SELECT, WHERE, ORDER BY, agregacoes e comandos de escrita (INSERT, UPDATE, DELETE).",
        "nivel": "INICIANTE",
        "ordem_modulo": 1,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "Lendo e Escrevendo Dados com SQL",
                "descricao": "Aprenda a estrutura de uma consulta SQL e os comandos basicos de manipulacao.",
                "xp": 50,
                "texto": (
                    "### Tabelas e Consultas\n\n"
                    "Em um banco relacional, os dados ficam em **tabelas** formadas por colunas (atributos) e linhas (registros). "
                    "A linguagem **SQL** e usada para consultar e alterar esses dados.\n\n"
                    "### Estrutura de um SELECT\n\n"
                    "- **`SELECT`**: quais colunas retornar.\n"
                    "- **`FROM`**: de qual tabela.\n"
                    "- **`WHERE`**: filtra as linhas por uma condicao.\n"
                    "- **`ORDER BY`**: ordena o resultado (`ASC` ou `DESC`).\n"
                    "- **`GROUP BY`** + funcoes de agregacao (`COUNT`, `SUM`, `AVG`): resume grupos de linhas.\n\n"
                    "```sql\n"
                    "SELECT nome, nota\n"
                    "FROM alunos\n"
                    "WHERE nota >= 7\n"
                    "ORDER BY nota DESC;\n"
                    "\n"
                    "SELECT trilha_id, COUNT(*) AS total\n"
                    "FROM matriculas\n"
                    "GROUP BY trilha_id;\n"
                    "```\n\n"
                    "### Escrita de Dados\n\n"
                    "```sql\n"
                    "INSERT INTO alunos (nome, nota) VALUES ('Caio', 8.5);\n"
                    "UPDATE alunos SET nota = 9 WHERE nome = 'Caio';\n"
                    "DELETE FROM alunos WHERE nota < 2;\n"
                    "```\n\n"
                    "> **Dica Pro**: Sempre teste a condicao com um `SELECT` antes de rodar um `UPDATE` ou `DELETE`. Sem `WHERE`, eles afetam a tabela inteira."
                )
            },
            {
                "tipo": "MULTIPLA_ESCOLHA",
                "titulo": "Exercicio: Filtrando Linhas",
                "descricao": "Identifique a clausula de filtro do SQL.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual clausula SQL filtra as linhas retornadas por uma consulta de acordo com uma condicao?",
                        "opcoes": ["WHERE", "ORDER BY", "GROUP BY", "FROM"],
                        "gabarito_idx": 0,
                        "dica": "A palavra significa 'onde' em ingles."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual comando SQL altera dados de linhas ja existentes?",
                        "opcoes": ["INSERT", "ALTER", "UPDATE", "MODIFY"],
                        "gabarito_idx": 2,
                        "dica": "ALTER muda a estrutura da tabela, nao os dados."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual funcao de agregacao retorna a quantidade de linhas?",
                        "opcoes": ["SUM()", "COUNT()", "TOTAL()", "LEN()"],
                        "gabarito_idx": 1,
                        "dica": "A funcao significa 'contar'."
                    }
                ]
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Alunos Maiores de Idade",
                "descricao": "Complete a consulta que filtra por idade.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a clausula que retorna apenas os alunos com 18 anos ou mais:",
                        "codigo_snippet": (
                            "SELECT nome, email\n"
                            "FROM alunos\n"
                            "__BLANK_0__ idade >= 18;"
                        ),
                        "gabarito": "WHERE",
                        "dica": "E a mesma clausula de filtro vista no exercicio anterior."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o comando que adiciona um novo aluno a tabela:",
                        "codigo_snippet": (
                            "__BLANK_0__ INTO alunos (nome, idade)\n"
                            "VALUES ('Ana', 21);"
                        ),
                        "gabarito": "INSERT",
                        "dica": "O comando significa 'inserir'."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a clausula que define o novo valor da coluna no UPDATE:",
                        "codigo_snippet": (
                            "UPDATE alunos\n"
                            "__BLANK_0__ email = 'ana@fatec.sp.gov.br'\n"
                            "WHERE id = 1;"
                        ),
                        "gabarito": "SET",
                        "dica": "A clausula 'define' os novos valores."
                    }
                ]
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Ranking de Notas",
                "descricao": "Ordene as clausulas de uma consulta com ordenacao.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as clausulas para listar nome e nota dos alunos, da maior para a menor nota:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__"
                        ),
                        "blocos": [
                            "SELECT nome, nota",
                            "FROM alunos",
                            "ORDER BY nota DESC;"
                        ],
                        "dica": "A ordem obrigatoria e: SELECT, FROM e por ultimo ORDER BY."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as clausulas para listar as trilhas com mais de 10 matriculas:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "SELECT trilha_id, COUNT(*) AS total",
                            "FROM matriculas",
                            "GROUP BY trilha_id",
                            "HAVING COUNT(*) > 10;"
                        ],
                        "dica": "HAVING filtra os grupos, por isso vem depois do GROUP BY."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as clausulas para listar os aprovados (nota >= 7) em ordem alfabetica:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": ["SELECT nome, nota", "FROM alunos", "WHERE nota >= 7", "ORDER BY nome;"],
                        "dica": "A ordem padrao e SELECT, FROM, WHERE, ORDER BY."
                    }
                ]
            },
            {
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Agrupando Matriculas",
                "descricao": "Conte quantas matriculas existem por trilha.",
                "xp": 150,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a palavra-chave que agrupa as linhas por trilha antes de contar as matriculas:",
                        "codigo_snippet": (
                            "SELECT trilha_id, COUNT(*)\n"
                            "FROM matriculas\n"
                            "__BLANK_0__ BY trilha_id;"
                        ),
                        "gabarito": "GROUP",
                        "dica": "A palavra significa 'grupo' em ingles."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a clausula que limita o resultado as 3 maiores notas:",
                        "codigo_snippet": (
                            "SELECT nome, nota\n"
                            "FROM alunos\n"
                            "ORDER BY nota DESC\n"
                            "__BLANK_0__ 3;"
                        ),
                        "gabarito": "LIMIT",
                        "dica": "A clausula 'limita' a quantidade de linhas."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a clausula que filtra os grupos pela media calculada:",
                        "codigo_snippet": (
                            "SELECT curso, AVG(nota)\n"
                            "FROM alunos\n"
                            "GROUP BY curso\n"
                            "__BLANK_0__ AVG(nota) >= 7;"
                        ),
                        "gabarito": "HAVING",
                        "dica": "WHERE nao pode ser usado com funcoes de agregacao."
                    }
                ]
            }
        ]
    },
    {
        "titulo": "Modelagem Relacional e JOINs",
        "descricao": "Chaves primarias e estrangeiras, relacionamentos 1:N e N:N, normalizacao e JOINs.",
        "nivel": "INTERMEDIARIO",
        "ordem_modulo": 2,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "Relacionando Tabelas",
                "descricao": "Modele relacionamentos com chaves e combine tabelas com JOIN.",
                "xp": 50,
                "texto": (
                    "### Chaves e Relacionamentos\n\n"
                    "- **Chave primaria (PK)**: identifica cada linha de forma unica (ex: `id`).\n"
                    "- **Chave estrangeira (FK)**: coluna que aponta para a PK de outra tabela, garantindo integridade referencial.\n"
                    "- **1:N**: um aluno possui varias matriculas.\n"
                    "- **N:N**: alunos e trilhas se relacionam por uma tabela intermediaria (`matriculas`).\n\n"
                    "**Normalizar** e evitar dados duplicados: em vez de repetir o nome da trilha em cada matricula, guardamos apenas o `trilha_id`.\n\n"
                    "```sql\n"
                    "CREATE TABLE matriculas (\n"
                    "  id SERIAL PRIMARY KEY,\n"
                    "  aluno_id INTEGER REFERENCES alunos(id),\n"
                    "  trilha_id INTEGER REFERENCES trilhas(id)\n"
                    ");\n"
                    "```\n\n"
                    "### Tipos de JOIN\n\n"
                    "- **`INNER JOIN`**: apenas linhas com correspondencia nas duas tabelas.\n"
                    "- **`LEFT JOIN`**: todas as linhas da tabela da esquerda, com `NULL` quando nao ha correspondencia.\n\n"
                    "```sql\n"
                    "SELECT a.nome, t.titulo\n"
                    "FROM matriculas m\n"
                    "JOIN alunos a ON a.id = m.aluno_id\n"
                    "JOIN trilhas t ON t.id = m.trilha_id;\n"
                    "```\n\n"
                    "> **Dica Pro**: Use `LEFT JOIN` para encontrar ausencias, como alunos que ainda nao se matricularam em nenhuma trilha."
                )
            },
            {
                "tipo": "MULTIPLA_ESCOLHA",
                "titulo": "Exercicio: Tipos de JOIN",
                "descricao": "Reconheca o JOIN que preserva a tabela da esquerda.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual JOIN retorna todas as linhas da tabela da esquerda, mesmo quando nao ha correspondencia na tabela da direita?",
                        "opcoes": ["LEFT JOIN", "INNER JOIN", "CROSS JOIN", "SELF JOIN"],
                        "gabarito_idx": 0,
                        "dica": "O nome do JOIN indica o lado que e preservado."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Como normalmente se implementa um relacionamento N:N entre alunos e trilhas?",
                        "opcoes": [
                            "Uma coluna com uma lista de ids",
                            "Uma tabela associativa (ex: matriculas) com duas chaves estrangeiras",
                            "Duplicando as tabelas",
                            "Com um LEFT JOIN permanente"
                        ],
                        "gabarito_idx": 1,
                        "dica": "Uma tabela intermediaria liga os dois lados."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual o objetivo principal da normalizacao de um banco relacional?",
                        "opcoes": [
                            "Aumentar a redundancia",
                            "Eliminar chaves primarias",
                            "Acelerar todos os JOINs",
                            "Reduzir redundancia e anomalias de atualizacao"
                        ],
                        "gabarito_idx": 3,
                        "dica": "Pense em evitar que a mesma informacao fique repetida em varios lugares."
                    }
                ]
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Chave Estrangeira",
                "descricao": "Complete a definicao de uma chave estrangeira.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a palavra-chave que faz a coluna aluno_id apontar para a tabela alunos:",
                        "codigo_snippet": (
                            "CREATE TABLE matriculas (\n"
                            "  id SERIAL PRIMARY KEY,\n"
                            "  aluno_id INTEGER __BLANK_0__ alunos(id)\n"
                            ");"
                        ),
                        "gabarito": "REFERENCES",
                        "dica": "A coluna 'referencia' outra tabela."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a palavra-chave que define a chave primaria da tabela:",
                        "codigo_snippet": (
                            "CREATE TABLE trilhas (\n"
                            "  id SERIAL __BLANK_0__ KEY,\n"
                            "  titulo VARCHAR(120) NOT NULL\n"
                            ");"
                        ),
                        "gabarito": "PRIMARY",
                        "dica": "A chave e 'primaria'."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a palavra-chave que introduz a condicao de juncao:",
                        "codigo_snippet": (
                            "SELECT a.nome, m.trilha_id\n"
                            "FROM alunos a\n"
                            "JOIN matriculas m __BLANK_0__ m.aluno_id = a.id;"
                        ),
                        "gabarito": "ON",
                        "dica": "A condicao indica 'em que' colunas as tabelas se ligam."
                    }
                ]
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Consulta com JOINs",
                "descricao": "Ordene uma consulta que combina tres tabelas.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as linhas para listar o nome do aluno e o titulo da trilha de cada matricula:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "SELECT a.nome, t.titulo",
                            "FROM matriculas m",
                            "JOIN alunos a ON a.id = m.aluno_id",
                            "JOIN trilhas t ON t.id = m.trilha_id;"
                        ],
                        "dica": "Depois do SELECT e do FROM, cada JOIN acrescenta uma tabela relacionada."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize a criacao da tabela matriculas com chave estrangeira:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "  __SLOT_1__\n"
                            "  __SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "CREATE TABLE matriculas (",
                            "id SERIAL PRIMARY KEY,",
                            "aluno_id INTEGER REFERENCES alunos(id)",
                            ");"
                        ],
                        "dica": "A chave primaria costuma ser a primeira coluna; a ultima coluna nao leva virgula."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize a consulta que lista os alunos SEM nenhuma matricula:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "SELECT a.nome",
                            "FROM alunos a",
                            "LEFT JOIN matriculas m ON m.aluno_id = a.id",
                            "WHERE m.id IS NULL;"
                        ],
                        "dica": "O LEFT JOIN mantem todos os alunos; o WHERE fica com os que nao tiveram correspondencia."
                    }
                ]
            },
            {
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Apenas Alunos Matriculados",
                "descricao": "Escolha o JOIN que descarta alunos sem matricula.",
                "xp": 150,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o tipo de JOIN para listar somente os alunos que possuem ao menos uma matricula:",
                        "codigo_snippet": (
                            "SELECT a.nome\n"
                            "FROM alunos a\n"
                            "__BLANK_0__ JOIN matriculas m ON m.aluno_id = a.id;"
                        ),
                        "gabarito": "INNER",
                        "dica": "E o JOIN que retorna apenas as linhas com correspondencia nas duas tabelas."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a acao que remove automaticamente as matriculas quando o aluno for excluido:",
                        "codigo_snippet": "aluno_id INTEGER REFERENCES alunos(id) ON DELETE __BLANK_0__",
                        "gabarito": "CASCADE",
                        "dica": "A exclusao se propaga 'em cascata'."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a restricao que impede dois alunos com o mesmo e-mail:",
                        "codigo_snippet": (
                            "CREATE TABLE alunos (\n"
                            "  id SERIAL PRIMARY KEY,\n"
                            "  email VARCHAR(150) __BLANK_0__ NOT NULL\n"
                            ");"
                        ),
                        "gabarito": "UNIQUE",
                        "dica": "A restricao garante valores 'unicos'."
                    }
                ]
            }
        ]
    }
]

# ==============================================================================
# TRILHA 8: Inteligencia Artificial: Machine Learning
# ==============================================================================
trilha_ia = Trilha.objects.create(
    titulo="Inteligencia Artificial: Machine Learning",
    descricao="Entenda os fundamentos de Machine Learning e treine seus primeiros modelos com scikit-learn.",
    habilidade="Inteligência Artificial",
    ativo=True
)

modulos_ia = [
    {
        "titulo": "Conceitos de Machine Learning",
        "descricao": "IA, ML e Deep Learning, aprendizado supervisionado, features, rotulos e divisao treino/teste.",
        "nivel": "INICIANTE",
        "ordem_modulo": 1,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "Como uma Maquina Aprende",
                "descricao": "Diferencie os tipos de aprendizado e conheca o fluxo de treino de um modelo.",
                "xp": 50,
                "texto": (
                    "### IA, Machine Learning e Deep Learning\n\n"
                    "- **Inteligencia Artificial**: area ampla que busca sistemas capazes de tarefas que exigem inteligencia.\n"
                    "- **Machine Learning (ML)**: subarea em que o sistema **aprende padroes a partir de dados**, em vez de seguir regras escritas manualmente.\n"
                    "- **Deep Learning**: ML com redes neurais de muitas camadas.\n\n"
                    "### Tipos de Aprendizado\n\n"
                    "- **Supervisionado**: os dados possuem **rotulos** (respostas conhecidas). Ex: prever o preco de um imovel.\n"
                    "- **Nao supervisionado**: sem rotulos; o modelo encontra grupos ou estruturas. Ex: segmentar clientes.\n"
                    "- **Por reforco**: um agente aprende com recompensas e penalidades.\n\n"
                    "### Fluxo Basico com scikit-learn\n\n"
                    "As **features** (`X`) sao as caracteristicas de entrada e o **alvo** (`y`) e o que queremos prever. "
                    "Separamos parte dos dados para **teste**, para medir o desempenho em exemplos que o modelo nunca viu:\n\n"
                    "```python\n"
                    "from sklearn.model_selection import train_test_split\n"
                    "from sklearn.linear_model import LinearRegression\n"
                    "\n"
                    "X_treino, X_teste, y_treino, y_teste = train_test_split(X, y, test_size=0.2)\n"
                    "\n"
                    "modelo = LinearRegression()\n"
                    "modelo.fit(X_treino, y_treino)     # treino\n"
                    "previsoes = modelo.predict(X_teste) # inferencia\n"
                    "```\n\n"
                    "> **Dica Pro**: Nunca avalie o modelo com os mesmos dados usados no treino; o resultado parecera melhor do que realmente e."
                )
            },
            {
                "tipo": "MULTIPLA_ESCOLHA",
                "titulo": "Exercicio: Aprendizado Supervisionado",
                "descricao": "Identifique a base do aprendizado supervisionado.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Em aprendizado supervisionado, o modelo aprende a partir de:",
                        "opcoes": [
                            "Exemplos com rotulos (respostas conhecidas)",
                            "Dados sem nenhum rotulo",
                            "Recompensas recebidas de um ambiente",
                            "Regras escritas manualmente pelo programador"
                        ],
                        "gabarito_idx": 0,
                        "dica": "A 'supervisao' vem das respostas corretas fornecidas junto aos dados."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Em um dataset para prever o preco de casas, o que e a coluna 'preco'?",
                        "opcoes": ["Uma feature", "O rotulo (target)", "Um hiperparametro", "Uma metrica de avaliacao"],
                        "gabarito_idx": 1,
                        "dica": "E justamente o valor que o modelo deve aprender a prever."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Prever se um e-mail e spam ou nao e um problema de:",
                        "opcoes": ["Regressao", "Clusterizacao", "Classificacao", "Reducao de dimensionalidade"],
                        "gabarito_idx": 2,
                        "dica": "A saida e uma categoria, nao um numero continuo."
                    }
                ]
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Separando Treino e Teste",
                "descricao": "Complete a importacao da funcao que divide os dados.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a funcao do scikit-learn que separa os dados em conjuntos de treino e teste:",
                        "codigo_snippet": (
                            "from sklearn.model_selection import __BLANK_0__\n"
                            "X_treino, X_teste, y_treino, y_teste = train_test_split(X, y, test_size=0.2)"
                        ),
                        "gabarito": "train_test_split",
                        "dica": "E a mesma funcao chamada na segunda linha."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o metodo que treina o modelo com os dados de treino:",
                        "codigo_snippet": (
                            "modelo = LinearRegression()\n"
                            "modelo.__BLANK_0__(X_treino, y_treino)"
                        ),
                        "gabarito": "fit",
                        "dica": "O modelo e 'ajustado' aos dados."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o parametro que reserva 30% dos dados para teste:",
                        "codigo_snippet": "X_treino, X_teste, y_treino, y_teste = train_test_split(X, y, __BLANK_0__=0.3, random_state=42)",
                        "gabarito": "test_size",
                        "dica": "O parametro define o 'tamanho do teste'."
                    }
                ]
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Ciclo de Treino",
                "descricao": "Ordene as etapas de criacao, treino e previsao de um modelo.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as linhas para criar o modelo, treina-lo e gerar previsoes:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__"
                        ),
                        "blocos": [
                            "modelo = LinearRegression()",
                            "modelo.fit(X_treino, y_treino)",
                            "previsoes = modelo.predict(X_teste)"
                        ],
                        "dica": "Um modelo precisa existir e ser treinado antes de prever."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize a preparacao dos dados ate a divisao em treino e teste:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "df = pd.read_csv('casas.csv')",
                            "df = df.dropna()",
                            "X, y = df[['area', 'quartos']], df['preco']",
                            "X_treino, X_teste, y_treino, y_teste = train_test_split(X, y)"
                        ],
                        "dica": "Limpe os dados antes de separar features e rotulo."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Ordene as etapas de um projeto de Machine Learning supervisionado:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "Coletar e limpar os dados",
                            "Separar os dados em treino e teste",
                            "Treinar o modelo com os dados de treino",
                            "Avaliar o modelo com os dados de teste"
                        ],
                        "dica": "O teste so faz sentido com um modelo ja treinado."
                    }
                ]
            },
            {
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Gerando Previsoes",
                "descricao": "Use o metodo de inferencia de um modelo treinado.",
                "xp": 150,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o metodo que gera previsoes para os dados de teste:",
                        "codigo_snippet": (
                            "modelo.fit(X_treino, y_treino)\n"
                            "previsoes = modelo.__BLANK_0__(X_teste)"
                        ),
                        "gabarito": "predict",
                        "dica": "A palavra significa 'prever' em ingles."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a classe do scikit-learn usada para regressao linear:",
                        "codigo_snippet": (
                            "from sklearn.linear_model import __BLANK_0__\n"
                            "modelo = LinearRegression()"
                        ),
                        "gabarito": "LinearRegression",
                        "dica": "E a mesma classe instanciada na linha seguinte."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o parametro que define quantos vizinhos o KNN considera:",
                        "codigo_snippet": (
                            "from sklearn.neighbors import KNeighborsClassifier\n"
                            "modelo = KNeighborsClassifier(__BLANK_0__=5)"
                        ),
                        "gabarito": "n_neighbors",
                        "dica": "O parametro significa 'numero de vizinhos'."
                    }
                ]
            }
        ]
    },
    {
        "titulo": "Avaliacao de Modelos",
        "descricao": "Metricas de classificacao, matriz de confusao, overfitting e underfitting.",
        "nivel": "INTERMEDIARIO",
        "ordem_modulo": 2,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "Medindo a Qualidade de um Modelo",
                "descricao": "Escolha as metricas certas e reconheca overfitting.",
                "xp": 50,
                "texto": (
                    "### Metricas de Classificacao\n\n"
                    "- **Acuracia**: proporcao de acertos sobre o total. Engana em dados desbalanceados.\n"
                    "- **Precisao**: dos que o modelo marcou como positivos, quantos realmente sao.\n"
                    "- **Recall (revocacao)**: dos positivos reais, quantos o modelo encontrou.\n"
                    "- **Matriz de confusao**: tabela com verdadeiros/falsos positivos e negativos.\n\n"
                    "### Overfitting e Underfitting\n\n"
                    "- **Overfitting**: o modelo decora o treino (desempenho alto) e falha em dados novos (desempenho baixo no teste).\n"
                    "- **Underfitting**: o modelo e simples demais e vai mal ate no treino.\n\n"
                    "Limitar a complexidade, como a profundidade de uma arvore de decisao, ajuda a evitar overfitting:\n\n"
                    "```python\n"
                    "from sklearn.tree import DecisionTreeClassifier\n"
                    "from sklearn.metrics import accuracy_score\n"
                    "\n"
                    "modelo = DecisionTreeClassifier(max_depth=3)\n"
                    "modelo.fit(X_treino, y_treino)\n"
                    "\n"
                    "acuracia_treino = accuracy_score(y_treino, modelo.predict(X_treino))\n"
                    "acuracia_teste = accuracy_score(y_teste, modelo.predict(X_teste))\n"
                    "print(acuracia_treino, acuracia_teste)\n"
                    "```\n\n"
                    "> **Dica Pro**: Uma grande diferenca entre a metrica de treino e a de teste e o principal sinal de overfitting."
                )
            },
            {
                "tipo": "MULTIPLA_ESCOLHA",
                "titulo": "Exercicio: Diagnosticando o Modelo",
                "descricao": "Interprete a diferenca entre treino e teste.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Um modelo com 99% de acuracia no treino e 60% no teste provavelmente esta sofrendo de:",
                        "opcoes": ["Overfitting", "Underfitting", "Vazamento de memoria", "Normalizacao excessiva"],
                        "gabarito_idx": 0,
                        "dica": "O modelo 'decorou' os dados de treino."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Em um teste de doenca rara, qual metrica mede a proporcao de doentes reais que o modelo identificou?",
                        "opcoes": ["Precisao", "Acuracia", "Recall (sensibilidade)", "Especificidade"],
                        "gabarito_idx": 2,
                        "dica": "A metrica se preocupa em nao deixar positivos reais passarem."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Um modelo que erra muito tanto no treino quanto no teste provavelmente sofre de:",
                        "opcoes": ["Overfitting", "Underfitting", "Data leakage", "Excesso de dados de teste"],
                        "gabarito_idx": 1,
                        "dica": "O modelo e simples demais para capturar os padroes."
                    }
                ]
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Calculando a Acuracia",
                "descricao": "Complete a funcao de metrica de acuracia.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a funcao que calcula a acuracia comparando os rotulos reais com as previsoes:",
                        "codigo_snippet": (
                            "from sklearn.metrics import accuracy_score\n"
                            "acuracia = __BLANK_0__(y_teste, previsoes)"
                        ),
                        "gabarito": "accuracy_score",
                        "dica": "E a funcao importada na primeira linha."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a funcao que gera a matriz de confusao:",
                        "codigo_snippet": (
                            "from sklearn.metrics import confusion_matrix\n"
                            "matriz = __BLANK_0__(y_teste, previsoes)"
                        ),
                        "gabarito": "confusion_matrix",
                        "dica": "A funcao foi importada na primeira linha."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a funcao que executa validacao cruzada com 5 particoes:",
                        "codigo_snippet": (
                            "from sklearn.model_selection import cross_val_score\n"
                            "notas = __BLANK_0__(modelo, X, y, cv=5)\n"
                            "print(notas.mean())"
                        ),
                        "gabarito": "cross_val_score",
                        "dica": "A funcao foi importada na primeira linha."
                    }
                ]
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Avaliando uma Arvore de Decisao",
                "descricao": "Ordene a importacao, criacao, treino e avaliacao do modelo.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as linhas para importar, criar, treinar e avaliar uma arvore de decisao:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "from sklearn.tree import DecisionTreeClassifier",
                            "modelo = DecisionTreeClassifier(max_depth=3)",
                            "modelo.fit(X_treino, y_treino)",
                            "print(modelo.score(X_teste, y_teste))"
                        ],
                        "dica": "Importe a classe, instancie, treine e so entao avalie."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize o treino, a previsao e a geracao do relatorio de classificacao:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "modelo.fit(X_treino, y_treino)",
                            "previsoes = modelo.predict(X_teste)",
                            "relatorio = classification_report(y_teste, previsoes)",
                            "print(relatorio)"
                        ],
                        "dica": "O relatorio compara os rotulos reais com as previsoes ja geradas."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize o codigo que mede a diferenca entre o desempenho no treino e no teste:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "modelo = DecisionTreeClassifier(max_depth=None)",
                            "modelo.fit(X_treino, y_treino)",
                            "gap = modelo.score(X_treino, y_treino) - modelo.score(X_teste, y_teste)",
                            "print(f'Diferenca treino/teste: {gap:.2f}')"
                        ],
                        "dica": "Uma grande diferenca entre treino e teste indica overfitting."
                    }
                ]
            },
            {
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Controlando a Complexidade",
                "descricao": "Limite a profundidade da arvore para reduzir overfitting.",
                "xp": 150,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o parametro que limita a profundidade maxima da arvore de decisao:",
                        "codigo_snippet": (
                            "modelo = DecisionTreeClassifier(__BLANK_0__=3)"
                        ),
                        "gabarito": "max_depth",
                        "dica": "O nome combina 'maximo' e 'profundidade' em ingles, separados por underline."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a funcao que calcula a media harmonica entre precisao e recall:",
                        "codigo_snippet": (
                            "from sklearn.metrics import f1_score\n"
                            "f1 = __BLANK_0__(y_teste, previsoes)"
                        ),
                        "gabarito": "f1_score",
                        "dica": "A funcao foi importada na primeira linha."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o parametro que define o numero de particoes da validacao cruzada:",
                        "codigo_snippet": "notas = cross_val_score(modelo, X, y, __BLANK_0__=5)",
                        "gabarito": "cv",
                        "dica": "E a abreviacao de 'cross-validation'."
                    }
                ]
            }
        ]
    }
]

# ==============================================================================
# TRILHA 9: DevOps e Cloud: Docker e CI/CD
# ==============================================================================
trilha_devops = Trilha.objects.create(
    titulo="DevOps e Cloud: Docker e CI/CD",
    descricao="Empacote aplicacoes em containers e automatize testes e deploys com pipelines de CI/CD.",
    habilidade="DevOps/Cloud",
    ativo=True
)

modulos_devops = [
    {
        "titulo": "Containers com Docker",
        "descricao": "Containers vs. maquinas virtuais, imagens, Dockerfile e execucao de containers.",
        "nivel": "INICIANTE",
        "ordem_modulo": 1,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "Empacotando Aplicacoes com Docker",
                "descricao": "Entenda imagens, containers e as instrucoes de um Dockerfile.",
                "xp": 50,
                "texto": (
                    "### Por que Containers?\n\n"
                    "Um **container** empacota a aplicacao com todas as suas dependencias, garantindo que ela rode igual no computador do desenvolvedor, "
                    "no servidor de testes e em producao. Diferente de uma maquina virtual, ele compartilha o kernel do sistema, sendo mais leve e rapido.\n\n"
                    "### Imagem vs. Container\n\n"
                    "- **Imagem**: modelo imutavel, construido a partir de um `Dockerfile`.\n"
                    "- **Container**: uma instancia em execucao de uma imagem.\n\n"
                    "### Instrucoes do Dockerfile\n\n"
                    "- **`FROM`**: imagem base.\n"
                    "- **`WORKDIR`**: diretorio de trabalho.\n"
                    "- **`COPY`**: copia arquivos para a imagem.\n"
                    "- **`RUN`**: executa comandos durante o build (ex: instalar dependencias).\n"
                    "- **`CMD`**: comando padrao ao iniciar o container.\n\n"
                    "```dockerfile\n"
                    "FROM python:3.13-slim\n"
                    "WORKDIR /app\n"
                    "COPY requirements.txt .\n"
                    "RUN pip install -r requirements.txt\n"
                    "COPY . .\n"
                    "CMD [\"python\", \"main.py\"]\n"
                    "```\n\n"
                    "```bash\n"
                    "docker build -t minha-api .\n"
                    "docker run -p 8000:8000 minha-api   # porta do host:porta do container\n"
                    "```\n\n"
                    "> **Dica Pro**: Copie o `requirements.txt` antes do restante do codigo para aproveitar o cache de camadas do Docker."
                )
            },
            {
                "tipo": "MULTIPLA_ESCOLHA",
                "titulo": "Exercicio: Imagem e Container",
                "descricao": "Diferencie imagem e container.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual a diferenca entre imagem e container no Docker?",
                        "opcoes": [
                            "A imagem e o modelo imutavel; o container e uma instancia em execucao dela",
                            "Sao sinonimos e podem ser usados da mesma forma",
                            "O container e o modelo; a imagem e a execucao",
                            "A imagem so pode existir em provedores de nuvem"
                        ],
                        "gabarito_idx": 0,
                        "dica": "Pense na relacao entre uma classe e um objeto."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Por que containers costumam ser mais leves que maquinas virtuais?",
                        "opcoes": [
                            "Nao usam memoria RAM",
                            "Rodam apenas em nuvem",
                            "Compartilham o kernel do sistema operacional host",
                            "Nao possuem sistema de arquivos"
                        ],
                        "gabarito_idx": 2,
                        "dica": "Uma VM precisa de um sistema operacional completo; o container nao."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual comando lista os containers em execucao?",
                        "opcoes": ["docker ls", "docker ps", "docker images", "docker run"],
                        "gabarito_idx": 1,
                        "dica": "O nome vem do comando Unix que lista processos."
                    }
                ]
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Instalando Dependencias",
                "descricao": "Complete a instrucao que executa um comando durante o build.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a instrucao do Dockerfile que executa a instalacao das dependencias durante o build:",
                        "codigo_snippet": (
                            "FROM python:3.13-slim\n"
                            "WORKDIR /app\n"
                            "COPY . .\n"
                            "__BLANK_0__ pip install -r requirements.txt"
                        ),
                        "gabarito": "RUN",
                        "dica": "A instrucao significa 'executar' em ingles."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a instrucao que define o diretorio de trabalho dentro da imagem:",
                        "codigo_snippet": (
                            "FROM node:22-alpine\n"
                            "__BLANK_0__ /app\n"
                            "COPY package.json .\n"
                            "RUN npm install"
                        ),
                        "gabarito": "WORKDIR",
                        "dica": "O nome combina 'work' e 'directory'."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a instrucao que documenta a porta em que a aplicacao escuta:",
                        "codigo_snippet": (
                            "FROM python:3.13-slim\n"
                            "COPY . /app\n"
                            "__BLANK_0__ 8000\n"
                            "CMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\"]"
                        ),
                        "gabarito": "EXPOSE",
                        "dica": "A instrucao 'expoe' a porta."
                    }
                ]
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Montando um Dockerfile",
                "descricao": "Ordene as instrucoes de um Dockerfile simples.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as instrucoes para definir a imagem base, copiar o codigo e iniciar a aplicacao:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__"
                        ),
                        "blocos": [
                            "FROM python:3.13-slim",
                            "COPY . /app",
                            "CMD [\"python\", \"/app/main.py\"]"
                        ],
                        "dica": "Todo Dockerfile comeca pela imagem base e termina com o comando de inicializacao."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize o Dockerfile para aproveitar o cache: dependencias antes do restante do codigo:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__\n"
                            "__SLOT_4__"
                        ),
                        "blocos": [
                            "FROM python:3.13-slim",
                            "WORKDIR /app",
                            "COPY requirements.txt .",
                            "RUN pip install -r requirements.txt",
                            "COPY . ."
                        ],
                        "dica": "Copiar so o requirements.txt primeiro evita reinstalar tudo a cada mudanca no codigo."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize os comandos para construir a imagem, subir o container, ver os logs e para-lo:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "docker build -t minha-api .",
                            "docker run -d -p 8000:8000 --name api minha-api",
                            "docker logs api",
                            "docker stop api"
                        ],
                        "dica": "O container so existe depois que a imagem foi construida."
                    }
                ]
            },
            {
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Publicando a Porta",
                "descricao": "Exponha a porta do container no host.",
                "xp": 150,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a flag que mapeia a porta 8000 do host para a porta 8000 do container:",
                        "codigo_snippet": (
                            "docker run __BLANK_0__ 8000:8000 minha-api"
                        ),
                        "gabarito": "-p",
                        "dica": "E a flag curta de 'publish'."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a flag que define o nome e a tag da imagem no build:",
                        "codigo_snippet": "docker build __BLANK_0__ minha-api:1.0 .",
                        "gabarito": "-t",
                        "dica": "A flag e a inicial de 'tag'."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a flag que executa o container em segundo plano:",
                        "codigo_snippet": "docker run __BLANK_0__ -p 5432:5432 postgres:16",
                        "gabarito": "-d",
                        "dica": "A flag e a inicial de 'detached'."
                    }
                ]
            }
        ]
    },
    {
        "titulo": "Integracao e Entrega Continuas",
        "descricao": "Pipelines de CI/CD, GitHub Actions, Docker Compose e modelos de servico em nuvem.",
        "nivel": "INTERMEDIARIO",
        "ordem_modulo": 2,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "Automatizando o Caminho ate Producao",
                "descricao": "Entenda CI/CD, escreva um workflow e orquestre servicos com Docker Compose.",
                "xp": 50,
                "texto": (
                    "### CI e CD\n\n"
                    "- **Integracao Continua (CI)**: cada alteracao enviada ao repositorio dispara automaticamente build e testes.\n"
                    "- **Entrega/Deploy Continuo (CD)**: versoes aprovadas sao publicadas automaticamente em homologacao ou producao.\n\n"
                    "### Workflow no GitHub Actions\n\n"
                    "Um workflow e um arquivo YAML em `.github/workflows/`. Ele define **quando** rodar (`on`) e **o que** rodar (`jobs` e `steps`):\n\n"
                    "```yaml\n"
                    "on:\n"
                    "  push:\n"
                    "    branches: [main]\n"
                    "jobs:\n"
                    "  testes:\n"
                    "    runs-on: ubuntu-latest\n"
                    "    steps:\n"
                    "      - uses: actions/checkout@v4\n"
                    "      - run: pip install -r requirements.txt\n"
                    "      - run: pytest\n"
                    "```\n\n"
                    "### Docker Compose e Nuvem\n\n"
                    "O **Docker Compose** sobe varios containers juntos (API + banco) com `docker compose up -d`. "
                    "Na nuvem, os servicos se dividem em **IaaS** (maquinas virtuais), **PaaS** (plataforma gerenciada para rodar sua aplicacao) e **SaaS** (software pronto).\n\n"
                    "> **Dica Pro**: Um pipeline que falha rapido e barato: rode lint e testes unitarios antes das etapas mais demoradas."
                )
            },
            {
                "tipo": "MULTIPLA_ESCOLHA",
                "titulo": "Exercicio: Objetivo da CI",
                "descricao": "Reconheca o papel da integracao continua.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual o principal objetivo da Integracao Continua (CI)?",
                        "opcoes": [
                            "Validar automaticamente cada alteracao com build e testes",
                            "Substituir o controle de versao do projeto",
                            "Publicar em producao sem executar testes",
                            "Monitorar os custos da infraestrutura em nuvem"
                        ],
                        "gabarito_idx": 0,
                        "dica": "A ideia e detectar problemas logo apos cada alteracao."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual a diferenca entre Entrega Continua e Implantacao Continua (Continuous Deployment)?",
                        "opcoes": [
                            "Sao exatamente a mesma pratica",
                            "Na implantacao continua toda alteracao aprovada vai para producao automaticamente; na entrega continua ha uma aprovacao manual",
                            "Entrega continua nao executa testes",
                            "Implantacao continua exige deploy manual"
                        ],
                        "gabarito_idx": 1,
                        "dica": "A diferenca esta em quem aperta o botao final de producao."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Em qual modelo de servico em nuvem o provedor gerencia infraestrutura e runtime e voce so publica o codigo?",
                        "opcoes": ["IaaS", "On-premise", "PaaS", "Bare metal"],
                        "gabarito_idx": 2,
                        "dica": "O provedor entrega uma 'plataforma' pronta."
                    }
                ]
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Escolhendo o Runner",
                "descricao": "Complete a chave que define a maquina do job.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a chave do GitHub Actions que define em qual sistema operacional o job sera executado:",
                        "codigo_snippet": (
                            "jobs:\n"
                            "  testes:\n"
                            "    __BLANK_0__: ubuntu-latest"
                        ),
                        "gabarito": "runs-on",
                        "dica": "A chave significa 'roda em', com as palavras separadas por hifen."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a chave que define os eventos que disparam o workflow:",
                        "codigo_snippet": (
                            "name: CI\n"
                            "__BLANK_0__:\n"
                            "  push:\n"
                            "    branches: [main]"
                        ),
                        "gabarito": "on",
                        "dica": "O workflow roda 'quando' (em) um evento acontece."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a chave que lista os passos do job:",
                        "codigo_snippet": (
                            "jobs:\n"
                            "  build:\n"
                            "    runs-on: ubuntu-latest\n"
                            "    __BLANK_0__:\n"
                            "      - uses: actions/checkout@v4"
                        ),
                        "gabarito": "steps",
                        "dica": "Significa 'passos' em ingles."
                    }
                ]
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Etapas do Pipeline",
                "descricao": "Ordene os passos de um job de testes.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize os passos para baixar o codigo, instalar as dependencias e rodar os testes:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__"
                        ),
                        "blocos": [
                            "- uses: actions/checkout@v4",
                            "- run: pip install -r requirements.txt",
                            "- run: pytest"
                        ],
                        "dica": "Nao e possivel instalar dependencias antes de ter o codigo do repositorio."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Ordene as etapas de um pipeline de CI/CD com containers:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "Desenvolvedor faz push para o repositorio",
                            "Pipeline de CI executa build e testes",
                            "Imagem Docker e publicada no registry",
                            "Deploy da nova versao em producao"
                        ],
                        "dica": "Nada deve ser publicado sem antes passar pelos testes."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize os comandos do ciclo de vida de uma stack com Docker Compose:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "docker compose build",
                            "docker compose up -d",
                            "docker compose logs -f api",
                            "docker compose down"
                        ],
                        "dica": "Construa, suba, acompanhe e, por fim, derrube a stack."
                    }
                ]
            },
            {
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Subindo os Servicos",
                "descricao": "Inicie todos os servicos do Compose em segundo plano.",
                "xp": 150,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o subcomando que cria e inicia todos os servicos definidos no docker-compose.yaml:",
                        "codigo_snippet": (
                            "docker compose __BLANK_0__ -d"
                        ),
                        "gabarito": "up",
                        "dica": "O oposto do subcomando 'down'."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o contexto do GitHub Actions que guarda valores sensiveis do repositorio:",
                        "codigo_snippet": (
                            "env:\n"
                            "  DATABASE_URL: ${{ __BLANK_0__.DATABASE_URL }}"
                        ),
                        "gabarito": "secrets",
                        "dica": "Significa 'segredos' em ingles."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o subcomando que para e remove os containers da stack:",
                        "codigo_snippet": "docker compose __BLANK_0__",
                        "gabarito": "down",
                        "dica": "E o oposto de up."
                    }
                ]
            }
        ]
    }
]

# ==============================================================================
# TRILHA 10: Algoritmos e Estruturas de Dados
# ==============================================================================
trilha_algoritmos = Trilha.objects.create(
    titulo="Algoritmos e Estruturas de Dados",
    descricao="Analise a eficiencia de algoritmos e use as estruturas de dados certas para cada problema.",
    habilidade="Algoritmos",
    ativo=True
)

modulos_algoritmos = [
    {
        "titulo": "Complexidade e Busca",
        "descricao": "Notacao Big-O, busca linear e busca binaria.",
        "nivel": "INICIANTE",
        "ordem_modulo": 1,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "Medindo a Eficiencia de Algoritmos",
                "descricao": "Entenda a notacao Big-O e compare busca linear e busca binaria.",
                "xp": 50,
                "texto": (
                    "### Notacao Big-O\n\n"
                    "A notacao **Big-O** descreve como o tempo (ou memoria) de um algoritmo cresce conforme a entrada `n` aumenta:\n\n"
                    "- **O(1)**: constante (acessar `lista[0]`).\n"
                    "- **O(log n)**: logaritmica (busca binaria).\n"
                    "- **O(n)**: linear (percorrer a lista uma vez).\n"
                    "- **O(n^2)**: quadratica (dois lacos aninhados).\n\n"
                    "### Busca Linear vs. Busca Binaria\n\n"
                    "A **busca linear** verifica item por item: O(n). A **busca binaria** exige uma lista **ordenada** e descarta metade dos elementos a cada passo: O(log n).\n\n"
                    "```python\n"
                    "def busca_binaria(lista, alvo):\n"
                    "    inicio, fim = 0, len(lista) - 1\n"
                    "    while inicio <= fim:\n"
                    "        meio = (inicio + fim) // 2\n"
                    "        if lista[meio] == alvo:\n"
                    "            return meio\n"
                    "        if lista[meio] < alvo:\n"
                    "            inicio = meio + 1\n"
                    "        else:\n"
                    "            fim = meio - 1\n"
                    "    return -1\n"
                    "\n"
                    "print(busca_binaria([1, 3, 5, 7, 9], 7))  # 3\n"
                    "```\n\n"
                    "> **Dica Pro**: Em uma lista de 1 milhao de itens, a busca binaria precisa de no maximo cerca de 20 comparacoes."
                )
            },
            {
                "tipo": "MULTIPLA_ESCOLHA",
                "titulo": "Exercicio: Complexidade da Busca Binaria",
                "descricao": "Identifique a complexidade de tempo da busca binaria.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual a complexidade de tempo da busca binaria em uma lista ordenada?",
                        "opcoes": ["O(log n)", "O(n)", "O(1)", "O(n^2)"],
                        "gabarito_idx": 0,
                        "dica": "A cada passo, metade dos elementos e descartada."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual a complexidade de tempo da busca linear no pior caso?",
                        "opcoes": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
                        "gabarito_idx": 2,
                        "dica": "No pior caso, todos os elementos precisam ser verificados."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual pre-requisito e obrigatorio para aplicar a busca binaria?",
                        "opcoes": [
                            "A lista deve conter apenas numeros positivos",
                            "A lista deve estar ordenada",
                            "A lista deve ter tamanho par",
                            "A lista nao pode ter duplicados"
                        ],
                        "gabarito_idx": 1,
                        "dica": "A busca descarta metade da lista comparando com o elemento do meio."
                    }
                ]
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Calculando o Meio",
                "descricao": "Complete o calculo do indice central com divisao inteira.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o operador de divisao inteira que calcula o indice do meio da busca binaria:",
                        "codigo_snippet": (
                            "inicio, fim = 0, 9\n"
                            "meio = (inicio + fim) __BLANK_0__ 2"
                        ),
                        "gabarito": "//",
                        "dica": "Indices precisam ser inteiros: use o operador de divisao que descarta a parte decimal."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o operador de comparacao da busca linear:",
                        "codigo_snippet": (
                            "def busca_linear(lista, alvo):\n"
                            "    for i in range(len(lista)):\n"
                            "        if lista[i] __BLANK_0__ alvo:\n"
                            "            return i\n"
                            "    return -1"
                        ),
                        "gabarito": "==",
                        "dica": "Queremos saber se o elemento e igual ao alvo."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o operador que move o inicio para depois do meio quando o alvo e maior:",
                        "codigo_snippet": (
                            "elif lista[meio] < alvo:\n"
                            "    inicio = meio __BLANK_0__ 1\n"
                            "else:\n"
                            "    fim = meio - 1"
                        ),
                        "gabarito": "+",
                        "dica": "O alvo esta na metade direita da lista."
                    }
                ]
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Preparando a Busca Binaria",
                "descricao": "Ordene as etapas antes de executar uma busca binaria.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as linhas para criar a lista, ordena-la e entao buscar o valor 7:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__"
                        ),
                        "blocos": [
                            "numeros = [9, 3, 7, 1]",
                            "numeros.sort()",
                            "posicao = busca_binaria(numeros, 7)"
                        ],
                        "dica": "A busca binaria so funciona em listas ordenadas."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "O indice do meio ja foi calculado. Organize as comparacoes do laco da busca binaria:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "    __SLOT_1__\n"
                            "__SLOT_2__\n"
                            "    __SLOT_3__\n"
                            "__SLOT_4__\n"
                            "    __SLOT_5__"
                        ),
                        "blocos": [
                            "if lista[meio] == alvo:",
                            "return meio",
                            "elif lista[meio] < alvo:",
                            "inicio = meio + 1",
                            "else:",
                            "fim = meio - 1"
                        ],
                        "dica": "Primeiro verifique se encontrou o alvo; o else e sempre o ultimo ramo."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize a funcao de busca linear:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "    __SLOT_1__\n"
                            "        __SLOT_2__\n"
                            "            __SLOT_3__\n"
                            "    __SLOT_4__"
                        ),
                        "blocos": [
                            "def busca_linear(lista, alvo):",
                            "for i, valor in enumerate(lista):",
                            "if valor == alvo:",
                            "return i",
                            "return -1"
                        ],
                        "dica": "O return -1 fica fora do laco: so executa se o alvo nao for encontrado."
                    }
                ]
            },
            {
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Condicao de Parada",
                "descricao": "Defina ate quando a busca binaria deve continuar.",
                "xp": 150,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o operador de comparacao para que a busca continue enquanto ainda houver elementos no intervalo:",
                        "codigo_snippet": (
                            "while inicio __BLANK_0__ fim:\n"
                            "    meio = (inicio + fim) // 2"
                        ),
                        "gabarito": "<=",
                        "dica": "Quando inicio e fim sao iguais, ainda resta um elemento para verificar."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o valor retornado quando o alvo nao e encontrado:",
                        "codigo_snippet": (
                            "for i, valor in enumerate(lista):\n"
                            "    if valor == alvo:\n"
                            "        return i\n"
                            "return __BLANK_0__"
                        ),
                        "gabarito": "-1",
                        "dica": "Use um indice que nunca seria valido em uma lista."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a funcao que define o indice final inicial da busca binaria:",
                        "codigo_snippet": (
                            "inicio = 0\n"
                            "fim = __BLANK_0__(lista) - 1"
                        ),
                        "gabarito": "len",
                        "dica": "O ultimo indice e o tamanho da lista menos um."
                    }
                ]
            }
        ]
    },
    {
        "titulo": "Ordenacao e Estruturas de Dados",
        "descricao": "Pilhas, filas, dicionarios e algoritmos de ordenacao.",
        "nivel": "INTERMEDIARIO",
        "ordem_modulo": 2,
        "atividades": [
            {
                "tipo": "CONTEUDO",
                "titulo": "Escolhendo a Estrutura Certa",
                "descricao": "Conheca pilhas, filas e dicionarios e compare algoritmos de ordenacao.",
                "xp": 50,
                "texto": (
                    "### Estruturas de Dados Essenciais\n\n"
                    "- **Pilha (LIFO)**: o ultimo a entrar e o primeiro a sair. Em Python: `append()` e `pop()` em uma lista.\n"
                    "- **Fila (FIFO)**: o primeiro a entrar e o primeiro a sair. Use `collections.deque` com `append()` e `popleft()`, ambos O(1).\n"
                    "- **Dicionario (tabela hash)**: busca, insercao e remocao por chave em O(1) na media.\n\n"
                    "```python\n"
                    "from collections import deque\n"
                    "\n"
                    "pilha = []\n"
                    "pilha.append('a'); pilha.append('b')\n"
                    "print(pilha.pop())      # 'b'\n"
                    "\n"
                    "fila = deque(['a', 'b'])\n"
                    "print(fila.popleft())   # 'a'\n"
                    "```\n\n"
                    "### Algoritmos de Ordenacao\n\n"
                    "- **Bubble Sort**: troca vizinhos fora de ordem repetidamente. O(n^2), didatico mas lento.\n"
                    "- **Merge Sort**: divide a lista, ordena as metades e as intercala. O(n log n).\n"
                    "- **`sorted()` do Python**: usa o Timsort, O(n log n), e e a escolha no dia a dia.\n\n"
                    "```python\n"
                    "def bubble_sort(lista):\n"
                    "    for i in range(len(lista)):\n"
                    "        for j in range(len(lista) - 1 - i):\n"
                    "            if lista[j] > lista[j + 1]:\n"
                    "                lista[j], lista[j + 1] = lista[j + 1], lista[j]\n"
                    "    return lista\n"
                    "```\n\n"
                    "> **Dica Pro**: Usar `pop(0)` em uma lista Python como fila custa O(n); prefira `deque.popleft()`."
                )
            },
            {
                "tipo": "MULTIPLA_ESCOLHA",
                "titulo": "Exercicio: Principio LIFO",
                "descricao": "Identifique a estrutura LIFO.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual estrutura de dados segue o principio LIFO (ultimo a entrar, primeiro a sair)?",
                        "opcoes": ["Pilha", "Fila", "Lista ligada", "Arvore binaria"],
                        "gabarito_idx": 0,
                        "dica": "Pense em uma pilha de pratos."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual estrutura de dados segue o principio FIFO (primeiro a entrar, primeiro a sair)?",
                        "opcoes": ["Pilha", "Arvore", "Fila", "Grafo"],
                        "gabarito_idx": 2,
                        "dica": "Pense em uma fila de banco."
                    },
                    {
                        "tipo": "MULTIPLA_ESCOLHA",
                        "enunciado": "Qual a complexidade de tempo do Bubble Sort no pior caso?",
                        "opcoes": ["O(n)", "O(log n)", "O(n log n)", "O(n^2)"],
                        "gabarito_idx": 3,
                        "dica": "O algoritmo usa dois lacos aninhados sobre a lista."
                    }
                ]
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Consumindo uma Fila",
                "descricao": "Complete o metodo que remove o primeiro elemento de uma deque.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o metodo da deque que remove e retorna o primeiro elemento da fila em O(1):",
                        "codigo_snippet": (
                            "from collections import deque\n"
                            "fila = deque(['a', 'b', 'c'])\n"
                            "primeiro = fila.__BLANK_0__()"
                        ),
                        "gabarito": "popleft",
                        "dica": "E o 'pop' feito pelo lado esquerdo."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o metodo de dicionario que conta as palavras com valor padrao 0:",
                        "codigo_snippet": (
                            "contagem = {}\n"
                            "for palavra in palavras:\n"
                            "    contagem[palavra] = contagem.__BLANK_0__(palavra, 0) + 1"
                        ),
                        "gabarito": "get",
                        "dica": "O metodo retorna o valor padrao quando a chave nao existe."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o metodo da deque que insere um cliente no final da fila:",
                        "codigo_snippet": (
                            "from collections import deque\n"
                            "fila = deque()\n"
                            "fila.__BLANK_0__('cliente_1')"
                        ),
                        "gabarito": "append",
                        "dica": "E o mesmo metodo usado para adicionar ao final de uma lista."
                    }
                ]
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Operacoes de Pilha",
                "descricao": "Ordene as operacoes de empilhar e desempilhar.",
                "xp": 100,
                "questoes": [
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as linhas para criar a pilha, empilhar 1 e 2 e desempilhar o topo (que deve ser 2):",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "pilha = []",
                            "pilha.append(1)",
                            "pilha.append(2)",
                            "topo = pilha.pop()"
                        ],
                        "dica": "O ultimo valor empilhado e o primeiro a sair."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize os lacos do Bubble Sort:",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "    __SLOT_1__\n"
                            "        __SLOT_2__\n"
                            "            __SLOT_3__"
                        ),
                        "blocos": [
                            "for i in range(len(lista)):",
                            "for j in range(len(lista) - i - 1):",
                            "if lista[j] > lista[j + 1]:",
                            "lista[j], lista[j + 1] = lista[j + 1], lista[j]"
                        ],
                        "dica": "A troca so acontece quando o par esta fora de ordem."
                    },
                    {
                        "tipo": "ORDENAR_BLOCOS",
                        "enunciado": "Organize as linhas para que primeiro receba o valor 'a':",
                        "codigo_snippet": (
                            "__SLOT_0__\n"
                            "__SLOT_1__\n"
                            "__SLOT_2__\n"
                            "__SLOT_3__"
                        ),
                        "blocos": [
                            "fila = deque()",
                            "fila.append('a')",
                            "fila.append('b')",
                            "primeiro = fila.popleft()"
                        ],
                        "dica": "Na fila, quem entra primeiro sai primeiro."
                    }
                ]
            },
            {
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Trocando Elementos",
                "descricao": "Complete a troca de posicoes usada nos algoritmos de ordenacao.",
                "xp": 150,
                "questoes": [
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha a lacuna para trocar os valores das posicoes i e j em uma unica linha:",
                        "codigo_snippet": (
                            "lista[i], lista[j] = lista[j], __BLANK_0__"
                        ),
                        "gabarito": "lista[i]",
                        "dica": "Do lado direito, os valores aparecem na ordem inversa do lado esquerdo."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o metodo de lista que remove e retorna o topo da pilha:",
                        "codigo_snippet": (
                            "pilha = [1, 2, 3]\n"
                            "topo = pilha.__BLANK_0__()  # 3"
                        ),
                        "gabarito": "pop",
                        "dica": "E a operacao de 'desempilhar'."
                    },
                    {
                        "tipo": "COMPLETE_CODIGO",
                        "enunciado": "Preencha o parametro que ordena os alunos da maior para a menor nota:",
                        "codigo_snippet": "alunos.sort(key=lambda a: a['nota'], __BLANK_0__=True)",
                        "gabarito": "reverse",
                        "dica": "O parametro 'inverte' a ordem padrao (crescente)."
                    }
                ]
            }
        ]
    }
]


MAX_BLOCOS_ORDENAR = 6


def distribuir_pontuacao(xp_total, quantidade):
    """Divide o XP da atividade entre as questoes; a soma dos pesos e sempre igual ao XP."""
    base, resto = divmod(xp_total, quantidade)
    return [base + (1 if i < resto else 0) for i in range(quantidade)]


def criar_questao(atividade, q_data, ordem, peso):
    tipo = q_data["tipo"]

    if tipo == "MULTIPLA_ESCOLHA":
        gabarito_idx = q_data["gabarito_idx"]
        questao = Questao.objects.create(
            atividade=atividade,
            tipo_exercicio="MULTIPLA_ESCOLHA",
            enunciado=q_data["enunciado"],
            codigo_snippet="",
            gabarito_esperado="",
            explicacao=f"A resposta correta e: {q_data['opcoes'][gabarito_idx]}",
            dica_conceitual=q_data["dica"],
            ordem_questao=ordem,
            peso_pontuacao=peso
        )
        opcao_correta_id = None
        for op_idx, op_texto in enumerate(q_data["opcoes"]):
            opcao = QuestaoOpcao.objects.create(
                questao=questao,
                texto_opcao=op_texto,
                ordem=op_idx + 1
            )
            if op_idx == gabarito_idx:
                opcao_correta_id = str(opcao.id)
        questao.gabarito_esperado = opcao_correta_id
        questao.save(update_fields=["gabarito_esperado"])

    elif tipo == "COMPLETE_CODIGO":
        Questao.objects.create(
            atividade=atividade,
            tipo_exercicio="COMPLETE_CODIGO",
            enunciado=q_data["enunciado"],
            codigo_snippet=q_data["codigo_snippet"],
            gabarito_esperado=q_data["gabarito"],
            explicacao=f"O valor esperado para completar o codigo e: {q_data['gabarito']}",
            dica_conceitual=q_data["dica"],
            ordem_questao=ordem,
            peso_pontuacao=peso
        )

    elif tipo == "ORDENAR_BLOCOS":
        # gabarito_esperado guarda os UUIDs dos blocos separados por virgula em um
        # CharField(255): 36 + 1 caracteres por bloco => no maximo 6 blocos.
        if len(q_data["blocos"]) > MAX_BLOCOS_ORDENAR:
            raise ValueError(
                f"Questao '{q_data['enunciado']}' tem {len(q_data['blocos'])} blocos; "
                f"o maximo suportado e {MAX_BLOCOS_ORDENAR}."
            )
        questao = Questao.objects.create(
            atividade=atividade,
            tipo_exercicio="ORDENAR_BLOCOS",
            enunciado=q_data["enunciado"],
            codigo_snippet=q_data["codigo_snippet"],
            gabarito_esperado="",
            explicacao="A ordem correta das instrucoes foi estruturada para manter a consistencia logica do algoritmo.",
            dica_conceitual=q_data["dica"],
            ordem_questao=ordem,
            peso_pontuacao=peso
        )
        ids_ordenados = []
        for b_idx, bloco_texto in enumerate(q_data["blocos"]):
            opcao = QuestaoOpcao.objects.create(
                questao=questao,
                texto_opcao=bloco_texto,
                ordem=b_idx + 1
            )
            ids_ordenados.append(str(opcao.id))
        questao.gabarito_esperado = ",".join(ids_ordenados)
        questao.save(update_fields=["gabarito_esperado"])

    else:
        raise ValueError(f"Tipo de questao desconhecido: {tipo}")


def popular_trilha(trilha, modulos_data):
    print(f"\nPopulando Trilha: {trilha.titulo}")
    for m_data in modulos_data:
        modulo = Modulo.objects.create(
            trilha=trilha,
            titulo=m_data["titulo"],
            descricao=m_data["descricao"],
            nivel=m_data["nivel"],
            ordem_modulo=m_data["ordem_modulo"]
        )
        print(f"  + Modulo {modulo.ordem_modulo}: {modulo.titulo}")
        total_atividades = len(m_data["atividades"])
        for idx, ativ_data in enumerate(m_data["atividades"], start=1):
            tipo = ativ_data["tipo"]

            conteudo = None
            if tipo == "CONTEUDO":
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
                contexto_avaliacao="SOMATIVA" if tipo == "DESAFIO" else "FORMATIVA",
                xp_recompensa=ativ_data["xp"],
                ordem=idx,
                ativo=True
            )

            questoes = ativ_data.get("questoes", [])
            pesos = distribuir_pontuacao(ativ_data["xp"], len(questoes)) if questoes else []
            for ordem, (q_data, peso) in enumerate(zip(questoes, pesos), start=1):
                criar_questao(atividade, q_data, ordem, peso)

            detalhe = f" ({len(questoes)} questoes)" if questoes else ""
            print(f"    [{idx}/{total_atividades}] {tipo}: {atividade.titulo}{detalhe}")


popular_trilha(trilha_fundamentos, modulos_fundamentos)
popular_trilha(trilha_web, modulos_web)
popular_trilha(trilha_dados, modulos_dados)
popular_trilha(trilha_javascript, modulos_javascript)
popular_trilha(trilha_typescript, modulos_typescript)
popular_trilha(trilha_frontend, modulos_frontend)
popular_trilha(trilha_banco, modulos_banco)
popular_trilha(trilha_ia, modulos_ia)
popular_trilha(trilha_devops, modulos_devops)
popular_trilha(trilha_algoritmos, modulos_algoritmos)

print("\n==========================================")
print("--- RESUMO DO SEED DO CATALOGO ---")
print("==========================================")
print(f"Total Trilhas: {Trilha.objects.count()} (esperado: 10)")
print(f"Total Modulos: {Modulo.objects.count()} (esperado: 29)")
print(f"Total Atividades: {Atividade.objects.count()} (esperado: 145)")
print(f"Total Conteudos: {Conteudo.objects.count()} (esperado: 29)")
print(f"Total Questoes: {Questao.objects.count()} (esperado: 348)")
print(f"Total Opcoes: {QuestaoOpcao.objects.count()}")
print("==========================================")
print("Seed executado com sucesso absoluto!")

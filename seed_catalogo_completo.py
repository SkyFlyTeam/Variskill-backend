"""
Script para popular o banco de dados pedagógico com 3 Trilhas Python completas,
5 Módulos em cada trilha e exatamente 5 Atividades por Módulo:
  1. CONTEUDO (Teórico em Markdown)
  2. MULTIPLA_ESCOLHA (Conceitual, 4 opções)
  3. COMPLETE_CODIGO (Sintaxe básica, __BLANK_0__)
  4. ORDENAR_BLOCOS (Algoritmo e estrutura, __SLOT_X__)
  5. COMPLETE_CODIGO (Desafio prático do módulo, __BLANK_0__)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings')
django.setup()

from trackManagement.models import Trilha, Modulo, Matricula, ProgressoModulo
from activityManagement.models import Atividade, Conteudo, ExecucaoAtividade
from questionsManagement.models import Questao, QuestaoOpcao

print("Iniciando seed do catalogo completo de Python...")

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
    habilidade="Fundamentos",
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
                "enunciado": "Qual funcao nativa do Python e utilizada para converter a string '42' em um numero inteiro?",
                "opcoes": ["int('42')", "Integer.parse('42')", "toInt('42')", "cast<int>('42')"],
                "gabarito_idx": 0,
                "dica": "Utilize a funcao nativa cujo nome e exatamente a abreviacao do tipo inteiro."
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Conversao de Tipos",
                "descricao": "Complete a conversao de entrada de dados para float.",
                "xp": 100,
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
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Calculo de Media",
                "descricao": "Ordene as instrucoes para calcular e exibir a media aritmetica de duas notas.",
                "xp": 100,
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
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Resto da Divisao",
                "descricao": "Descubra se um numero e par ou impar utilizando o operador adequado.",
                "xp": 150,
                "enunciado": "Preencha o operador aritmetico que calcula o resto da divisao inteira (modulo) para validar paridade:",
                "codigo_snippet": (
                    "numero = 14\n"
                    "resto = numero __BLANK_0__ 2\n"
                    "eh_par = (resto == 0)"
                ),
                "gabarito": "%",
                "dica": "O operador de resto da divisao em Python e representado pelo caractere de porcentagem."
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
                "enunciado": "Qual operador logico deve ser utilizado quando precisamos que duas condicoes sejam simultaneamente verdadeiras?",
                "opcoes": ["and", "&&", "both", "all"],
                "gabarito_idx": 0,
                "dica": "Em Python usamos a palavra em ingles 'and', e nao simbolos como '&&'."
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Condicional Intermediaria",
                "descricao": "Complete a clausula intermediaria entre o if e o else.",
                "xp": 100,
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
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Validacao de Acesso",
                "descricao": "Ordene a checagem de permissao de usuario ativo e autenticado.",
                "xp": 100,
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
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Negacao Logica",
                "descricao": "Aplique o operador de inversao de valor booleano.",
                "xp": 150,
                "enunciado": "Preencha a lacuna com a palavra-chave que inverte o valor logico da expressao:",
                "codigo_snippet": (
                    "bloqueado = False\n"
                    "if __BLANK_0__ bloqueado:\n"
                    "    print('Usuario liberado')"
                ),
                "gabarito": "not",
                "dica": "Palavra em ingles para negacao logica."
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
                "enunciado": "Qual palavra-chave e utilizada para encerrar imediatamente a execucao de um laco for ou while?",
                "opcoes": ["break", "stop", "exit", "terminate"],
                "gabarito_idx": 0,
                "dica": "Comando classico em linguagens de programacao que significa 'quebrar' o loop."
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Gerador de Intervalos",
                "descricao": "Preencha a funcao nativa que gera sequencias numericas.",
                "xp": 100,
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
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Contador com While",
                "descricao": "Ordene a inicializacao e o incremento de uma variavel em loop.",
                "xp": 100,
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
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Pular Iteracao",
                "descricao": "Pule para a proxima iteracao sem executar o restante do corpo do loop.",
                "xp": 150,
                "enunciado": "Preencha a palavra-chave que ignora a iteracao atual quando o numero for par e continua o loop:",
                "codigo_snippet": (
                    "for num in range(10):\n"
                    "    if num % 2 == 0:\n"
                    "        __BLANK_0__\n"
                    "    print(num)"
                ),
                "gabarito": "continue",
                "dica": "Palavra em ingles que diz ao loop para prosseguir para o proximo ciclo."
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
                "enunciado": "Qual metodo de lista adiciona um novo item ao final da colecao?",
                "opcoes": ["append()", "push()", "add()", "insertLast()"],
                "gabarito_idx": 0,
                "dica": "No Python o termo utilizado e 'append', ao contrario de linguagens que usam 'push'."
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Busca Segura em Dicionarios",
                "descricao": "Utilize o metodo que nao dispara KeyError caso a chave nao exista.",
                "xp": 100,
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
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Filtragem com List Comprehension",
                "descricao": "Ordene a criacao de uma nova lista contendo apenas numeros pares.",
                "xp": 100,
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
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Tamanho de Colecoes",
                "descricao": "Obtenha a quantidade total de itens de qualquer sequencia.",
                "xp": 150,
                "enunciado": "Preencha a funcao nativa que retorna o numero de elementos de uma lista:",
                "codigo_snippet": (
                    "linguagens = ['Python', 'SQL', 'FastAPI']\n"
                    "total = __BLANK_0__(linguagens)\n"
                    "print(f'Total: {total}')"
                ),
                "gabarito": "len",
                "dica": "Abreviacao de 'length' (comprimento/tamanho)."
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
                "enunciado": "Qual palavra-chave e utilizada em Python para declarar uma funcao?",
                "opcoes": ["def", "function", "fn", "fun"],
                "gabarito_idx": 0,
                "dica": "Abreviacao de 'define' com 3 letras."
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Retorno de Valores",
                "descricao": "Preencha a instrucao que devolve o resultado calculado para quem chamou a funcao.",
                "xp": 100,
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
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Funcao Completa",
                "descricao": "Ordene a definicao, o calculo e a chamada de uma funcao que calcula a area de retangulos.",
                "xp": 100,
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
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Funcoes Lambda",
                "descricao": "Utilize a expressao anonima de uma unica linha.",
                "xp": 150,
                "enunciado": "Preencha a palavra reservada para criar uma pequena funcao anonima em Python:",
                "codigo_snippet": (
                    "dobro = __BLANK_0__ x: x * 2\n"
                    "print(dobro(5))"
                ),
                "gabarito": "lambda",
                "dica": "Nome de letra grega que denomina funcoes anonimas em programacao funcional."
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
    habilidade="Desenvolvimento Web",
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
                "enunciado": "Qual codigo de status HTTP padrao deve ser retornado quando uma requisicao POST cria um recurso com sucesso?",
                "opcoes": ["201 Created", "200 OK", "204 No Content", "302 Found"],
                "gabarito_idx": 0,
                "dica": "Codigo da familia 2xx especifico para itens 'Created' (criados)."
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Metodo HTTP Sem Efeito Colateral",
                "descricao": "Preencha o metodo HTTP idenpotente para consulta de dados.",
                "xp": 100,
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
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Ciclo de Requisicao e Resposta",
                "descricao": "Ordene as etapas fundamentais de uma requisicao HTTP.",
                "xp": 100,
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
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Cabecalho de Conteudo",
                "descricao": "Informe ao servidor o formato dos dados enviados no corpo da requisicao.",
                "xp": 150,
                "enunciado": "Preencha o tipo de midia padrao para payloads de dados em APIs REST modernas:",
                "codigo_snippet": (
                    "POST /api/usuarios HTTP/1.1\n"
                    "Content-Type: application/__BLANK_0__\n\n"
                    "{\"nome\": \"Lucas\"}"
                ),
                "gabarito": "json",
                "dica": "Formato de texto leve baseado em notacao de objetos JavaScript amplamente usado em APIs."
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
                "enunciado": "Como um Path Parameter deve ser declarado no caminho da rota no FastAPI?",
                "opcoes": ["{item_id}", ":item_id", "<item_id>", "$item_id"],
                "gabarito_idx": 0,
                "dica": "O FastAPI utiliza chaves `{parametro}` para mapear variaveis na URL."
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Rota de Criacao",
                "descricao": "Complete o decorator do FastAPI para endpoints de cadastro.",
                "xp": 100,
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
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Aplicacao FastAPI Basica",
                "descricao": "Ordene a importacao, instanciacao e rota raiz de um projeto FastAPI.",
                "xp": 100,
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
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Servidor ASGI",
                "descricao": "Comando para executar aplicacoes FastAPI em modo de desenvolvimento.",
                "xp": 150,
                "enunciado": "Preencha o nome do servidor ASGI padrao mais popular para rodar aplicacoes FastAPI:",
                "codigo_snippet": (
                    "# Execucao no terminal:\n"
                    "__BLANK_0__ main:app --reload"
                ),
                "gabarito": "uvicorn",
                "dica": "Servidor ultrarrapido para Python cujo nome comeca com 'uv'."
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
                "enunciado": "Qual classe base do Pydantic deve ser herdada para criar modelos de validacao de dados?",
                "opcoes": ["BaseModel", "SchemaModel", "DataModel", "Entity"],
                "gabarito_idx": 0,
                "dica": "Classe fundamental do Pydantic composta pelas palavras 'Base' e 'Model'."
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Heranca do Modelo",
                "descricao": "Complete a definicao de classe herdando do BaseModel.",
                "xp": 100,
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
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Endpoint com Body Validado",
                "descricao": "Ordene a criacao do schema Pydantic e a rota que o consome no FastAPI.",
                "xp": 100,
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
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Campos Opcionais",
                "descricao": "Declare campos nao-obrigatorios utilizando Optional da biblioteca typing.",
                "xp": 150,
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
                "enunciado": "No SQLAlchemy, qual argumento do Column define que uma coluna e a chave primaria da tabela?",
                "opcoes": ["primary_key=True", "is_primary=True", "id_key=True", "unique_key=True"],
                "gabarito_idx": 0,
                "dica": "O argumento em ingles e 'primary_key' atribuido com True."
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Nome da Tabela",
                "descricao": "Complete o atributo especial que especifica o nome da tabela no banco.",
                "xp": 100,
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
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Persistencia com Session",
                "descricao": "Ordene a criacao, adicao e commit de um novo registro no banco de dados.",
                "xp": 100,
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
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Reversao de Transacao",
                "descricao": "Reverta uma transacao com falha para preservar a integridade do banco.",
                "xp": 150,
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
                "enunciado": "Qual prefixo padrao acompanha o token JWT no cabecalho 'Authorization'?",
                "opcoes": ["Bearer", "Token", "JWT", "Basic"],
                "gabarito_idx": 0,
                "dica": "O esquema padrao do protocolo OAuth2 e 'Bearer <token>'."
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Injecao de Dependencias",
                "descricao": "Preencha a funcao do FastAPI para injetar a dependencia do usuario autenticado.",
                "xp": 100,
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
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Geracao de Token JWT",
                "descricao": "Ordene a criacao do payload com expiracao e a codificacao do token.",
                "xp": 100,
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
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Decodificacao de Token",
                "descricao": "Valide a assinatura de um token recebido do cliente.",
                "xp": 150,
                "enunciado": "Preencha o metodo da biblioteca jwt utilizado para decodificar e verificar o token:",
                "codigo_snippet": (
                    "from jose import jwt\n\n"
                    "dados = jwt.__BLANK_0__(token, SECRET_KEY, algorithms=['HS256'])\n"
                    "email = dados.get('sub')"
                ),
                "gabarito": "decode",
                "dica": "O inverso de 'encode' e 'decode'."
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
    habilidade="Analise de Dados",
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
                "enunciado": "Qual funcao da biblioteca NumPy converte uma lista tradicional de Python em um array vetorizado?",
                "opcoes": ["np.array()", "np.create()", "np.to_array()", "np.vector()"],
                "gabarito_idx": 0,
                "dica": "Funcao classica chamada simplesmente de 'array'."
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Alias Padrao da Biblioteca",
                "descricao": "Preencha a convencao universal de importacao do NumPy na comunidade.",
                "xp": 100,
                "enunciado": "Complete o alias padrao adotado globalmente para importar o pacote numpy:",
                "codigo_snippet": (
                    "import numpy as __BLANK_0__\n\n"
                    "valores = __BLANK_0__.zeros(5)"
                ),
                "gabarito": "np",
                "dica": "Abreviacao de duas letras mais famosa da ciencia de dados."
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Estatisticas Basicas com NumPy",
                "descricao": "Ordene a criacao do array e o calculo de media e desvio padrao.",
                "xp": 100,
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
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Gerador de Zeros",
                "descricao": "Crie uma matriz preenchida inicialmente com zeros.",
                "xp": 150,
                "enunciado": "Preencha a funcao do NumPy que inicializa um array preenchido exclusivamente com o numero 0:",
                "codigo_snippet": (
                    "import numpy as np\n"
                    "matriz_vazia = np.__BLANK_0__((3, 3))"
                ),
                "gabarito": "zeros",
                "dica": "Palavra em ingles no plural para 'zeros'."
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
                "enunciado": "Qual metodo do DataFrame do Pandas exibe por padrao as primeiras 5 linhas da tabela?",
                "opcoes": ["head()", "top()", "first()", "preview()"],
                "gabarito_idx": 0,
                "dica": "Metodo cujo nome em ingles significa 'cabeca' ou 'topo'."
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Importacao do Pandas",
                "descricao": "Preencha a convencao oficial de alias do Pandas.",
                "xp": 100,
                "enunciado": "Complete a instrucao com o alias oficial universalmente adotado para o pandas:",
                "codigo_snippet": (
                    "import pandas as __BLANK_0__\n\n"
                    "df = __BLANK_0__.read_csv('vendas.csv')"
                ),
                "gabarito": "pd",
                "dica": "Duas letras: 'p' e 'd'."
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Leitura e Inspecao de Dados",
                "descricao": "Ordene as instrucoes para carregar um CSV e inspecionar informacoes das colunas.",
                "xp": 100,
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
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Resumo Estatistico",
                "descricao": "Gere metricas rapidas (media, desvio, quartis) para todas as colunas numericas.",
                "xp": 150,
                "enunciado": "Preencha o metodo do Pandas que calcula automaticamente contagem, media, min e max:",
                "codigo_snippet": (
                    "import pandas as pd\n"
                    "df = pd.read_csv('dados.csv')\n"
                    "resumo = df.__BLANK_0__()"
                ),
                "gabarito": "describe",
                "dica": "Palavra em ingles para 'descrever'."
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
                "enunciado": "Qual metodo e utilizado para excluir linhas que contenham valores nulos (NaN) no Pandas?",
                "opcoes": ["dropna()", "remove_nulls()", "delete_empty()", "clean_na()"],
                "gabarito_idx": 0,
                "dica": "O termo 'drop' em conjunto com a sigla de 'Not Available' (NA)."
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Preenchimento de Nulos",
                "descricao": "Preencha os valores ausentes com a media da coluna.",
                "xp": 100,
                "enunciado": "Complete a chamada com o metodo utilizado para imputar valores em posicoes nulas:",
                "codigo_snippet": (
                    "media_idade = df['idade'].mean()\n"
                    "df['idade'] = df['idade'].__BLANK_0__(media_idade)"
                ),
                "gabarito": "fillna",
                "dica": "Juncao de 'fill' (preencher) com 'na'."
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Filtro Booleano de Vendas",
                "descricao": "Ordene a aplicacao de um filtro de vendas de alto valor.",
                "xp": 100,
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
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Detecao de Nulos",
                "descricao": "Identifique quais celulas estao vazias no DataFrame.",
                "xp": 150,
                "enunciado": "Preencha a funcao que retorna uma mascara booleana identificando onde estao os valores nulos:",
                "codigo_snippet": (
                    "total_nulos = df.__BLANK_0__().sum()\n"
                    "print(total_nulos)"
                ),
                "gabarito": "isna",
                "dica": "Metodo de 4 letras que checa 'is NA' (ou isnull)."
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
                "enunciado": "Qual metodo e utilizado no Pandas para dividir um DataFrame em grupos por valores de uma ou mais colunas?",
                "opcoes": ["groupby()", "cluster()", "partition()", "categorize()"],
                "gabarito_idx": 0,
                "dica": "Mesmo nome da clausula SQL 'GROUP BY'."
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Agrupamento Simples",
                "descricao": "Preencha o metodo para calcular a soma de faturamento por departamento.",
                "xp": 100,
                "enunciado": "Complete o metodo de agrupamento que separa os colaboradores por setor:",
                "codigo_snippet": (
                    "media_salarial = df.__BLANK_0__('departamento')['salario'].mean()\n"
                    "print(media_salarial)"
                ),
                "gabarito": "groupby",
                "dica": "Palavra 'groupby' toda em minusculo."
            },
            {
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Metricas Consolidadas",
                "descricao": "Ordene a criacao de agrupamento com multiplas agregacoes estatisticas.",
                "xp": 100,
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
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Agregacao Especifica",
                "descricao": "Aplique o metodo agg para customizar as funcoes de agregacao.",
                "xp": 150,
                "enunciado": "Preencha a abreviacao do metodo de agregacao multipla do Pandas:",
                "codigo_snippet": (
                    "resumo = df.groupby('categoria')['vendas'].__BLANK_0__(['sum', 'mean'])"
                ),
                "gabarito": "agg",
                "dica": "Abreviacao de 'aggregate' com 3 letras."
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
                "enunciado": "Qual funcao do matplotlib.pyplot e chamada para exibir a janela com o grafico plotado?",
                "opcoes": ["plt.show()", "plt.render()", "plt.display()", "plt.view()"],
                "gabarito_idx": 0,
                "dica": "Verbo em ingles para 'mostrar'."
            },
            {
                "tipo": "COMPLETE_CODIGO",
                "titulo": "Pratica: Grafico de Linhas",
                "descricao": "Complete a funcao para desenhar um grafico de series temporais (linhas).",
                "xp": 100,
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
                "tipo": "ORDENAR_BLOCOS",
                "titulo": "Pratica: Grafico com Seaborn",
                "descricao": "Ordene a importacao, configuracao de estilo e geracao de grafico de dispersao.",
                "xp": 100,
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
                "tipo": "DESAFIO",
                "titulo": "Desafio do Modulo: Titulo da Figura",
                "descricao": "Adicione o titulo descritivo na figura gerada.",
                "xp": 150,
                "enunciado": "Preencha a funcao do pyplot que define o titulo do grafico:",
                "codigo_snippet": (
                    "import matplotlib.pyplot as plt\n"
                    "plt.plot([1, 2, 3], [10, 20, 30])\n"
                    "plt.__BLANK_0__('Crescimento Mensal de Acessos')\n"
                    "plt.show()"
                ),
                "gabarito": "title",
                "dica": "Palavra em ingles para 'titulo'."
            }
        ]
    }
]

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
        for idx, ativ_data in enumerate(m_data["atividades"], start=1):
            tipo = ativ_data["tipo"]

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
                    contexto_avaliacao="FORMATIVA",
                    xp_recompensa=ativ_data["xp"],
                    ordem=idx,
                    ativo=True
                )
                print(f"    [{idx}/5] CONTEUDO: {atividade.titulo}")

            elif tipo == "MULTIPLA_ESCOLHA":
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
                    gabarito_esperado="",
                    explicacao=f"A resposta correta e: {gabarito_texto}",
                    dica_conceitual=ativ_data["dica"],
                    ordem_questao=1,
                    peso_pontuacao=ativ_data["xp"]
                )
                opcao_correta_id = None
                for op_idx, op_texto in enumerate(ativ_data["opcoes"]):
                    opcao = QuestaoOpcao.objects.create(
                        questao=questao,
                        texto_opcao=op_texto,
                        ordem=op_idx + 1
                    )
                    if op_idx == gabarito_idx:
                        opcao_correta_id = str(opcao.id)
                questao.gabarito_esperado = opcao_correta_id
                questao.save(update_fields=["gabarito_esperado"])
                print(f"    [{idx}/5] MULTIPLA_ESCOLHA: {atividade.titulo}")

            elif tipo in ("COMPLETE_CODIGO", "DESAFIO"):
                atividade = Atividade.objects.create(
                    modulo=modulo,
                    conteudo=None,
                    titulo=ativ_data["titulo"],
                    descricao=ativ_data["descricao"],
                    contexto_avaliacao="SOMATIVA" if tipo == "DESAFIO" else "FORMATIVA",
                    xp_recompensa=ativ_data["xp"],
                    ordem=idx,
                    ativo=True
                )
                Questao.objects.create(
                    atividade=atividade,
                    tipo_exercicio="COMPLETE_CODIGO",
                    enunciado=ativ_data["enunciado"],
                    codigo_snippet=ativ_data["codigo_snippet"],
                    gabarito_esperado=ativ_data["gabarito"],
                    explicacao=f"O valor esperado para completar o codigo e: {ativ_data['gabarito']}",
                    dica_conceitual=ativ_data["dica"],
                    ordem_questao=1,
                    peso_pontuacao=ativ_data["xp"]
                )
                tag = "DESAFIO" if tipo == "DESAFIO" else "COMPLETE_CODIGO"
                print(f"    [{idx}/5] {tag}: {atividade.titulo}")

            elif tipo == "ORDENAR_BLOCOS":
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
                questao = Questao.objects.create(
                    atividade=atividade,
                    tipo_exercicio="ORDENAR_BLOCOS",
                    enunciado=ativ_data["enunciado"],
                    codigo_snippet=ativ_data["codigo_snippet"],
                    gabarito_esperado="",
                    explicacao="A ordem correta das instrucoes foi estruturada para manter a consistencia logica do algoritmo.",
                    dica_conceitual=ativ_data["dica"],
                    ordem_questao=1,
                    peso_pontuacao=ativ_data["xp"]
                )
                ids_ordenados = []
                for b_idx, bloco_texto in enumerate(ativ_data["blocos"]):
                    opcao = QuestaoOpcao.objects.create(
                        questao=questao,
                        texto_opcao=bloco_texto,
                        ordem=b_idx + 1
                    )
                    ids_ordenados.append(str(opcao.id))
                questao.gabarito_esperado = ",".join(ids_ordenados)
                questao.save(update_fields=["gabarito_esperado"])
                print(f"    [{idx}/5] ORDENAR_BLOCOS: {atividade.titulo}")

popular_trilha(trilha_fundamentos, modulos_fundamentos)
popular_trilha(trilha_web, modulos_web)
popular_trilha(trilha_dados, modulos_dados)

print("\n==========================================")
print("--- RESUMO DO NOVO SEED PYTHON ---")
print("==========================================")
print(f"Total Trilhas: {Trilha.objects.count()} (esperado: 3)")
print(f"Total Modulos: {Modulo.objects.count()} (esperado: 15)")
print(f"Total Atividades: {Atividade.objects.count()} (esperado: 75)")
print(f"Total Conteudos: {Conteudo.objects.count()} (esperado: 15)")
print(f"Total Questoes: {Questao.objects.count()} (esperado: 60)")
print(f"Total Opcoes: {QuestaoOpcao.objects.count()}")
print("==========================================")
print("Seed executado com sucesso absoluto!")

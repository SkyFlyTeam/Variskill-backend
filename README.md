# Comandos do projeto

## Execução do projeto

```bash
docker compose run --rm --service-ports app
```

## Aplicação das migrations

```bash
docker compose run --rm --service-ports app python3 manage.py migrate
```

## Criação de migrations

```bash
docker compose run --rm --service-ports app python3 manage.py makemigrations
```

## Build da aplicação

O build sobe a aplicação completa em modo de produção, em duas stacks do Compose:

- **Backend** (`docker-compose-build.yaml`, neste repositório): PostgreSQL com
  pgvector, um serviço `migrate` que aplica as migrations e executa o
  `collectstatic`, e o Django servido pelo uvicorn (`Dockerfile.build`).
- **Frontend** (`docker-compose-build.yaml`, no repositório `vite-cookiecutter`):
  o bundle do Vite servido pelo nginx, que encaminha `/api/` e `/admin/` para o
  Django e serve os arquivos estáticos do Django em `/static/`.

As duas stacks se comunicam pela rede `cookiecutter-shared` e compartilham o
volume `cookiecutter-static`, ambos criados pela stack do backend. Por isso, o
backend deve ser iniciado primeiro.

### Pré-requisitos

- Docker com o plugin Compose v2.
- Os dois repositórios clonados lado a lado:

```text
6sem/
├── django-cookiecutter/
└── vite-cookiecutter/
```

### 1. Configurar as variáveis de ambiente (opcional)

Todas as variáveis têm valores padrão. Para alterá-las, defina-as no shell ou em
um arquivo `.env` na raiz de cada repositório. As principais são:

| Variável | Stack | Padrão | Descrição |
| --- | --- | --- | --- |
| `OPENAI_API_KEY` / `EXTERNAL_AI_API_KEY` | backend | vazio | Chaves do assistente de IA |
| `EXTERNAL_AI_MODEL` | backend | `gpt-4o-mini` | Modelo usado pelo assistente |
| `DJANGO_BUILD_ALLOWED_HOSTS` | backend | `*` | Hosts aceitos pelo Django no build. `*` aceita qualquer IP/domínio; para restringir, informe o domínio (ex.: `variskill.com.br`). O `DJANGO_ALLOWED_HOSTS` do `.env` vale apenas para o ambiente de desenvolvimento |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | backend | `cookie_cutter` | Credenciais do banco |
| `UVICORN_WORKERS` | backend | `2` | Processos do uvicorn; cada um carrega o modelo de embeddings na memória |
| `APP_PORT` | backend | `8000` | Porta do Django no host |
| `WEB_PORT` | frontend | `80` | Porta do nginx no host |
| `IMAGE_TAG` | ambas | `latest` | Tag das imagens geradas |

> O `BACKEND_URL` do `.env` do frontend é usado apenas pelo `npm run dev` e não
> afeta o build. O destino do nginx é configurado por `API_UPSTREAM`
> (padrão `http://backend:8000`).

### 2. Subir o backend

Na raiz deste repositório:

```bash
docker compose -f docker-compose-build.yaml up -d --build
```

O primeiro build demora alguns minutos e gera uma imagem de aproximadamente
2,6 GB, pois inclui o PyTorch e os modelos de NLP. O Compose aguarda o banco,
executa o serviço `migrate` e só então inicia o `app`. Para acompanhar:

```bash
docker compose -f docker-compose-build.yaml ps -a
docker compose -f docker-compose-build.yaml logs -f app
```

O serviço `migrate` deve aparecer como `Exited (0)` e o `app` como `healthy`.

### 3. Popular o banco (primeira execução)

Com o backend em execução, crie um superusuário e carregue os dados iniciais:

```bash
docker compose -f docker-compose-build.yaml exec app python manage.py createsuperuser
docker compose -f docker-compose-build.yaml exec app python manage.py seed_intencoes
docker compose -f docker-compose-build.yaml exec app python seed_catalogo_completo.py
```

> O `seed_catalogo_completo.py` apaga as trilhas, atividades e o progresso dos
> alunos antes de recriá-los. Não o execute em um banco com dados reais.

### 4. Subir o frontend

Na raiz do repositório `vite-cookiecutter`:

```bash
docker compose -f docker-compose-build.yaml up -d --build
```

### 5. Acessar a aplicação

| Endereço | Conteúdo |
| --- | --- |
| <http://localhost> | Aplicação (frontend) |
| <http://localhost/api/docs/> | Documentação da API (Swagger) |
| <http://localhost/admin/> | Admin do Django |
| <http://localhost/healthz> | Healthcheck do nginx |

Acesse sempre pelo frontend (porta `80`). Em outra máquina, troque `localhost` pelo IP ou domínio do servidor. A porta `8000` expõe o Django
diretamente, sem o rate limit e os cabeçalhos configurados no nginx.

### Atualizar após alterações no código

Repita o `up -d --build` da stack alterada. No backend, o serviço `migrate` é
executado novamente e aplica as novas migrations e os novos arquivos estáticos
antes de reiniciar o `app`.

```bash
docker compose -f docker-compose-build.yaml up -d --build
```

### Encerrar

Pare primeiro o frontend, que utiliza a rede criada pelo backend:

```bash
# em vite-cookiecutter/
docker compose -f docker-compose-build.yaml down

# em django-cookiecutter/
docker compose -f docker-compose-build.yaml down
```

Os dados do banco ficam no volume `postgres15_build_data` e são preservados
entre execuções. Para apagá-los junto com os arquivos estáticos, use
`down --volumes` na stack do backend.

## Execução dos testes

Execute a suíte em um ambiente separado, com PostgreSQL temporário:

```bash
docker compose -f docker-compose-test.yaml up --build --abort-on-container-exit --exit-code-from tests
```

O comando retorna o código de saída do pytest. Use `--build` para incluir as
alterações mais recentes no código. O banco de desenvolvimento não é utilizado.

Para executar apenas uma categoria de testes:

```bash
docker compose -f docker-compose-test.yaml run --build --rm tests uv run --locked pytest -m integration
# Troque integration por unit para selecionar testes unitários.
```

Remova os containers e a rede de testes após a execução:

```bash
docker compose -f docker-compose-test.yaml down --volumes
```

## Integração contínua

O workflow `.github/workflows/tests.yaml` executa a suíte de testes com o Compose
em cada push e pull request. Também é possível iniciá-lo manualmente pela aba
Actions do GitHub. Uma falha no pytest faz o job falhar; os serviços temporários
são removidos ao final da execução. Não é necessário configurar secrets.

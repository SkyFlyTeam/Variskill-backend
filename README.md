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

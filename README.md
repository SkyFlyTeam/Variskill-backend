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

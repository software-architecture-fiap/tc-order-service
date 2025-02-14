#!/bin/bash

# Aguarda o banco de dados estar pronto
echo "Aguardando o PostgreSQL iniciar..."
while ! nc -z postgres-db 5432; do
  sleep 1
done

echo "Banco de dados PostgreSQL está pronto!"

# Rodar as migrações do Alembic
echo "Rodando as migrações com Alembic..."
poetry run alembic upgrade head

# Inicia o FastAPI com Uvicorn
echo "Iniciando o FastAPI..."
exec poetry run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Usa uma imagem oficial do Python como base
FROM python:3.10

# Instala dependências do sistema (inclui netcat para esperar pelo banco)
RUN apt-get update && apt-get install -y postgresql-client netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Instala o Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    export PATH="/root/.local/bin:$PATH"

# Define a variável de ambiente do Poetry
ENV PATH="/root/.local/bin:$PATH"

# Define o diretório de trabalho dentro do container
WORKDIR /order-service

# Copia os arquivos do projeto para dentro do container
COPY . .

# Copia o script de entrada e garante a permissão de execução
COPY cmd/entrypoint.sh /cmd/entrypoint.sh
RUN chmod +x /cmd/entrypoint.sh

# Instala dependências com Poetry e evita instalação de pacotes desnecessários
RUN poetry install --no-root --no-interaction --no-ansi

# Expõe a porta que o FastAPI usará
EXPOSE 8001

# Define o script de entrada
ENTRYPOINT ["bash", "cmd/entrypoint.sh"]

# Order Service - Sistema de Pedidos

Este repositório contém o serviço de pedidos (`order-service`) de um sistema de lanchonete, onde os pedidos são gerenciados, os status são atualizados e as interações com o sistema de pagamento são realizadas.

## Visão Geral

O **Order Service** é responsável pela criação de pedidos, atualização de status e integração com o serviço de pagamento. Ele também gerencia a relação entre pedidos e produtos e oferece uma API para interagir com os dados de pedidos e produtos.

### Funcionalidades

- **Criação de pedidos**: Permite a criação de novos pedidos a partir de um cliente autenticado.
- **Atualização de status**: Permite que o status do pedido seja atualizado, como `paid`, `preparing`, `delivered`, etc.
- **Integração com serviço de pagamento**: Comunica-se com um serviço de pagamento para gerar links de pagamento ou QR codes.
- **Gerenciamento de produtos e categorias**: Ações CRUD (Create, Read, Update, Delete) para produtos e categorias.
- **Rastreamento de pedidos**: Permite o rastreamento do status de cada pedido.

## Tecnologias

- **FastAPI**: Framework para construir APIs rápidas.
- **SQLAlchemy**: ORM para interação com o banco de dados.
- **PostgreSQL**: Banco de dados relacional usado para armazenar dados de pedidos, produtos e categorias.
- **Docker**: Utilizado para containerizar o serviço.
- **Psycopg2**: Adaptador de banco de dados PostgreSQL para Python.

## Pré-requisitos

- **Python 3.10+**
- **Docker & Docker Compose** (para containers)
- **PostgreSQL** (como banco de dados relacional)

## Instalação

### 1. Clonar o repositório

Clone o repositório para sua máquina local:

```bash
git clone <<url>>
cd order-service
```

### 2. Criar um ambiente virtual

Crie e ative um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate  # Para macOS/Linux
.venv\Scripts\activate     # Para Windows
```

### 3. Instalar as dependências

Instale as dependências do projeto:

```bash
pip install poetry
poetry install
```

### 4. Configuração do banco de dados

O **Order Service** utiliza o PostgreSQL como banco de dados. Você pode usar o Docker para rodar uma instância do PostgreSQL localmente.

#### Usando Docker (para desenvolvimento)

Execute o seguinte comando para iniciar o PostgreSQL:

```bash
docker-compose up -d
```

#### Variáveis de ambiente

Crie um arquivo `.env` com as seguintes variáveis:

```bash
DATABASE_URL= "<<suaconexão>>"
AUTH_SERVICE_URL=http://auth-service:8000
PAYMENT_SERVICE_URL=http://payment-service:8002
```

- `DATABASE_URL` contém a URL de conexão do banco de dados PostgreSQL.
- `AUTH_SERVICE_URL` contém a URL de integração com o serviço de autorização.
- `PAYMENT_SERVICE_URL` contém a URL de integração com o serviço de pagamento.

### 5. Inicializar a aplicação

Execute o comando abaixo para iniciar a aplicação:

```bash
docker compose up --build -d
```

Isso criará o banco de dados e o serviço. Talvez seja necessário reiniciar o serviço caso o bd demore muito para ficar health.

### 6. Executar o servidor de desenvolvimento

Se estiver com o docker local, o servidor estará disponível em `http://127.0.0.1:8001`.

## Endpoints API

A API do **Order Service** possui os seguintes endpoints:

### Pedidos

- `POST /orders/`: Cria um novo pedido.
- `GET /orders/`: Recupera uma lista de pedidos ou,
- `GET /orders/{order_id}`: Recupera um pedido específico pelo ID.
- `PATCH /orders/{order_id}`: Atualiza o status de um pedido.

### Produtos

- `POST /products/`: Cria um novo produto.
- `GET /products/`: Recupera uma lista de produtos, ou
- `GET /products/{product_id}`: Recupera um produto específico.
- `PATCH /products/{product_id}`: Atualiza um produto.

### Categorias

- `POST /categories/`: Cria uma nova categoria.
- `GET /categories/`: Recupera uma lista de categorias, ou
- `GET /categories/{category_id}`: Recupera uma categoria específica.
- `PATCH /categories/{category_id}`: Atualiza uma categoria.

## Testes

Para executar os testes automatizados com `pytest`, use o seguinte comando:

```bash
pytest
```

Isso executará todos os testes definidos no repositório. (Necessidade de implementação).

### Testes de integração

Os testes de integração podem ser executados utilizando o banco de dados de testes configurado em um arquivo `docker-compose.test.yml` ou um banco de dados em memória.

### Testes unitários

A suíte de testes também inclui testes unitários para verificar o comportamento das funções e métodos principais.

## Deploy

Para produção, recomenda-se o uso de Docker e Docker Compose para orquestrar os containers de forma eficiente. O arquivo `docker-compose.yml` pode ser configurado para criar e gerenciar os containers em um ambiente de produção.

1. **Construir os containers**:

```bash
docker-compose up -d --build
```

2. **Acessar o serviço em produção**

Após o deploy, a API estará acessível no endereço especificado no arquivo `docker-compose.yml`.

## Contribuindo

1. Faça o fork deste repositório.
2. Crie uma nova branch (`git checkout -b feature/nova-feature`).
3. Faça suas alterações e commit (`git commit -am 'Adicionando nova feature'`).
4. Faça o push para a branch (`git push origin feature/nova-feature`).
5. Abra um pull request.

## Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

Se você encontrar problemas ou tiver dúvidas, sinta-se à vontade para abrir um *issue* ou fazer uma contribuição!

---



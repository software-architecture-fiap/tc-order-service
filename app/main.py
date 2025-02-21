import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html
from fastapi.responses import JSONResponse, HTMLResponse
from contextlib import asynccontextmanager
from app.database.database import Base, SessionLocal, engine
from app.middleware import ExceptionLoggingMiddleware
from app.routers import category, order, product
from app.tools.initialize_db import initialize_db
from app.tools.logging import logger

STATUS_CODE_KEY = "status code"

# Criando todas as tabelas no banco de dados
Base.metadata.create_all(bind=engine)


def init_admin_user() -> None:
    """Inicializa o usuário admin e configura o banco de dados.

    Cria um usuário administrador e inicializa o banco de dados com dados
    padrão.

    Returns:
        None
    """
    db = SessionLocal()
    try:
        initialize_db(db)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Executa tarefas antes de iniciar a API"""
    init_admin_user()
    yield
    print("Aplicação encerrando...")

app = FastAPI(lifespan=lifespan)
logger.info('Application startup')

# Configuração do CORS
origins = [
    'http://localhost',
    'http://localhost:8000',
    'http://localhost:8001',
    'http://localhost:8002'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Incluindo os roteadores
app.add_middleware(ExceptionLoggingMiddleware)
app.include_router(product.router, prefix='/products', tags=['products'])
app.include_router(order.router, prefix='/orders', tags=['orders'])
app.include_router(category.router, prefix='/category', tags=['category'])


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        content={
            STATUS_CODE_KEY: 422,
            "msg": (
                f"Validation error in request body or parameters: "
                f"{exc.errors()}"
            )
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP error: {exc.detail}")
    return JSONResponse(
        content={
            STATUS_CODE_KEY: exc.status_code,
            "msg": exc.detail,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unexpected server error: {str(exc)}", exc_info=True)
    return JSONResponse(
        content={
            STATUS_CODE_KEY: 500,
            "msg": (
                "An unexpected error occurred. Please try again later or "
                "contact your Support Team."
            )
        },
    )


@app.get('/health', tags=['health'])
def health_check() -> dict:
    """Retorna o status operacional da aplicação.

    Returns:
        dict: Um dicionário com o status da aplicação.
    """
    logger.debug('Status endpoint accessed')
    return {'status': 'Operational'}


# Adiciona a rota para a documentação do ReDoc
@app.get('/redoc', include_in_schema=False)
async def redoc() -> HTMLResponse:
    """Retorna o HTML para a documentação do ReDoc.

    Returns:
        HTMLResponse: O HTML da documentação do ReDoc.
    """
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + ' - ReDoc',
        redoc_js_url=(
            'https://cdn.jsdelivr.net/npm/redoc/bundles/redoc.standalone.js'
        ),
    )


@app.get("/docs", tags=['documentation'])
def get_docs():
    return app.openapi()


def run_server():
    uvicorn.run("app.main:app",
                host="127.0.0.1",
                port=8001,
                reload=True)


if __name__ == '__main__':
    run_server()

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..main import app
import os
from dotenv import load_dotenv
from ..database.database import Base, get_db

# Carregar .env.test
load_dotenv(".env.test")

# Criar engine do banco de teste usando .env.test
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine)

# Criar tabelas antes dos testes
Base.metadata.create_all(bind=engine)


# Função para substituir a conexão do banco de dados nos testes
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Substituir a dependência `get_db` pelo banco de testes
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Headers de autenticação fake para testes
AUTH_HEADERS = {
    "Authorization": "Bearer fake-jwt-token"
}


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Configura o banco de dados antes dos testes"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

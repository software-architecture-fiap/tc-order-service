from os import environ as env
from typing import Generator
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base
import os

# Força o carregamento do .env.test se os testes estiverem rodando
if "PYTEST_CURRENT_TEST" in os.environ:
    load_dotenv(".env.test")
else:
    load_dotenv()

SQLALCHEMY_DATABASE_URL: str = env.get('DATABASE_URL', '')

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError(
        "DATABASE_URL não foi definido! Verifique o .env ou .env.test"
        )

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Cria uma sessão de banco de dados e garante que ela seja fechada ao final.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

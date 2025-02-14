import requests
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_500_INTERNAL_SERVER_ERROR
from dotenv import load_dotenv
from os import environ as env

from ..tools.logging import logger

load_dotenv()

AUTH_SERVICE_URL = env.get('AUTH_SERVICE_URL')

security = HTTPBearer()

def authenticate_user(username: str, password: str):
    """Autentica um usuário com o auth-service e retorna um token."""
    url = f"{AUTH_SERVICE_URL}/token"
    try:
        response = requests.post(url, data={"username": username, "password": password})
        if response.status_code == 200:
            logger.info(f'{username} authorized')
            return response.json()
        else:
            logger.error(f'{username} unauthorized')
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
    except requests.RequestException as e:
        logger.error(HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao conectar com o serviço de autenticação"))
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao conectar com o serviço de autenticação")

def verify_token(token: str = Depends(security)) -> dict:
    """Valida o token JWT no auth-service e retorna os detalhes do usuário autenticado."""
    if isinstance(token, str):
        token_value = token  # Token já é uma string vinda da URL
    else:
        token_value = token.credentials  # Token veio do `Authorization` Header
    
    url = f"{AUTH_SERVICE_URL}/auth"
    headers = {"Authorization": f"Bearer {token_value}"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            logger.info(f"Resposta do auth-service: {response.status_code} - {response.text}")
            return response.json()  # Retorna os detalhes do usuário autenticado
        else:
            logger.error("Token inválido ou expirado")
            raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    except requests.RequestException:
        logger.error("Erro ao conectar com o auth-service")
        raise HTTPException(status_code=500, detail="Erro ao conectar com o auth-service")
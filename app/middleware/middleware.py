from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from ..tools.logging import logger

class ExceptionLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para capturar e registrar exceções não tratadas.

    Este middleware captura todas as exceções não tratadas durante o processamento das requisições
    e as registra no logger. Em seguida, retorna uma exceção HTTP 500 (Internal Server Error).

    Atributos:
        Nenhum.
    """

    async def dispatch(self, request: Request, call_next):  # noqa PLR6301
        """
        Manipula cada requisição, capturando e registrando exceções não tratadas.

        Args:
            request: A requisição atual.
            call_next: Função que chama o próximo middleware ou endpoint.

        Returns:
            A resposta da aplicação, caso nenhuma exceção ocorra.

        Raises:
            HTTPException: Se ocorrer uma exceção não tratada, uma exceção 500 é lançada.
        """
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f'Erro Não Tratado: {e}', exc_info=True)
            raise HTTPException(status_code=500, detail='Internal Server Error')

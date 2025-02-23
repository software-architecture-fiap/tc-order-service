import pytest
from unittest.mock import patch
import requests
from fastapi import HTTPException
from ..services.security import verify_token


def test_verify_token_valid():
    token = "valid-token"
    user_data = {"user_id": 1, "username": "testuser"}

    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = user_data

        result = verify_token(token)
        assert result == user_data


def test_verify_token_invalid():
    token = "invalid-token"

    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 401

        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Token inválido ou expirado"


def test_verify_token_service_error():
    token = "any-token"

    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.RequestException

        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Erro ao conectar com o auth-service"

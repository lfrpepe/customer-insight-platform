"""
Autenticação via API Key — camada de segurança da Fase 5 (ver ADR-007).

Não existe tabela de usuários/login no projeto; API Key simples é
suficiente para o escopo atual (proteger as 4 rotas de Create contra
acesso não autorizado), sem a complexidade de um sistema de autenticação
completo (OAuth2/JWT exigiria modelar usuários, senha, emissão de token —
fora de escopo por ora).
"""

import os

from dotenv import load_dotenv
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

load_dotenv()

NOME_HEADER = "X-API-Key"

_api_key_header = APIKeyHeader(name=NOME_HEADER, auto_error=False)


def verificar_api_key(chave: str = Security(_api_key_header)) -> None:
    """
    Dependência do FastAPI (`Depends(verificar_api_key)`).

    Compara o header 'X-API-Key' com a variável de ambiente API_KEY (nunca
    hardcoded — ver .env.example). auto_error=False no APIKeyHeader permite
    devolver 401 com mensagem própria em vez do 403 genérico do FastAPI
    quando o header está ausente.
    """
    chave_esperada = os.environ.get("API_KEY")
    if not chave_esperada:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API_KEY não configurada no servidor (.env).",
        )
    if chave != chave_esperada:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API Key inválida ou ausente.")

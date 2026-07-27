"""
Customer Insight Platform — Backend (Fase 5, ver ADR-006/ADR-007).

Executar localmente:
    uvicorn src.api.main:app --reload

Docs interativas (Swagger): http://127.0.0.1:8000/docs
Todas as rotas exigem o header 'X-API-Key' (ver ADR-007) — no Swagger, use
o botão "Authorize" (cadeado) para informar a chave uma única vez.
"""

from fastapi import Depends, FastAPI

from src.api.router_formulario_web import router as router_formulario_web
from src.api.router_pinpad import router as router_pinpad
from src.api.router_telemarketing import router as router_telemarketing
from src.api.router_totem import router as router_totem
from src.security.api_key import verificar_api_key

app = FastAPI(
    title="Customer Insight Platform — API de Cadastro de Avaliações",
    description="Create de avaliações vindas de Formulário Web, Pinpad, Totem e Telemarketing.",
    version="0.1.0",
)

# Autenticação aplicada a todas as rotas de uma vez, em vez de repetir
# Depends(verificar_api_key) em cada um dos 4 routers (ver ADR-007).
_dependencia_auth = [Depends(verificar_api_key)]

app.include_router(router_formulario_web, dependencies=_dependencia_auth)
app.include_router(router_pinpad, dependencies=_dependencia_auth)
app.include_router(router_totem, dependencies=_dependencia_auth)
app.include_router(router_telemarketing, dependencies=_dependencia_auth)


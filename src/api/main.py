"""
Customer Insight Platform — Backend (Fase 5, ver ADR-006/ADR-007).

Executar localmente:
    uvicorn src.api.main:app --reload

Docs interativas (Swagger): http://127.0.0.1:8000/docs
Tela de navegação entre as origens: /
Telas HTML: /formulario-web, /pinpad, /totem, /telemarketing-simulador
Todos os 4 POSTs de Create exigem o header 'X-API-Key' (ver ADR-007) — no
Swagger, use o botão "Authorize" (cadeado) para informar a chave uma única
vez. As telas HTML (GET) não exigem — a chave já vem embutida nelas,
injetada pelo servidor a partir do .env.
"""

import os

from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles

from src.api.router_formulario_web import router as router_formulario_web
from src.api.router_pinpad import router as router_pinpad
from src.api.router_telemarketing import router as router_telemarketing
from src.api.router_totem import router as router_totem
from src.api.router_views import router as router_views
from src.security.api_key import verificar_api_key

# Caminho absoluto (independente do diretório de onde `uvicorn` é iniciado)
# — evita 404 silencioso em /static/* se o comando rodar fora da raiz do repo.
_SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(
    title="Customer Insight Platform — API de Cadastro de Avaliações",
    description="Create de avaliações vindas de Formulário Web, Pinpad, Totem e Telemarketing.",
    version="0.1.0",
)

app.mount("/static", StaticFiles(directory=os.path.join(_SRC_DIR, "static")), name="static")

# Autenticação aplicada a todas as rotas de Create, de uma vez, em vez de
# repetir Depends(verificar_api_key) em cada um dos 4 routers (ver ADR-007).
_dependencia_auth = [Depends(verificar_api_key)]

app.include_router(router_formulario_web, dependencies=_dependencia_auth)
app.include_router(router_pinpad, dependencies=_dependencia_auth)
app.include_router(router_totem, dependencies=_dependencia_auth)
app.include_router(router_telemarketing, dependencies=_dependencia_auth)

# Telas HTML — sem autenticação (são as próprias telas, não os POSTs).
app.include_router(router_views)



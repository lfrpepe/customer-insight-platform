"""
Customer Insight Platform — Backend (Fase 5, ver ADR-006).

Executar localmente:
    uvicorn src.api.main:app --reload

Docs interativas (Swagger): http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI

from src.api.router_formulario_web import router as router_formulario_web
from src.api.router_pinpad import router as router_pinpad
from src.api.router_telemarketing import router as router_telemarketing
from src.api.router_totem import router as router_totem

app = FastAPI(
    title="Customer Insight Platform — API de Cadastro de Avaliações",
    description="Create de avaliações vindas de Formulário Web, Pinpad, Totem e Telemarketing.",
    version="0.1.0",
)

app.include_router(router_formulario_web)
app.include_router(router_pinpad)
app.include_router(router_totem)
app.include_router(router_telemarketing)

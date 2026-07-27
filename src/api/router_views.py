"""
Rotas de visualização (GET) — servem os templates HTML das 4 origens.

Separadas dos routers de Create (POST): estas rotas NÃO exigem API Key,
porque são as próprias telas que um cliente/operador vê antes de qualquer
chamada — o `main.py` só aplica `Depends(verificar_api_key)` nos 4 routers
de POST, não neste (ver ADR-007). A chave em si é injetada no HTML,
lida do .env no momento do render (ver aviso em cada template).
"""

import os

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from pg8000.dbapi import Connection

from src.crud.avaliacoes import listar_categorias, listar_clientes
from src.database.connection import get_connection

router = APIRouter(tags=["Telas"])

# Caminho absoluto (mesmo motivo do StaticFiles em main.py) — evita template
# não encontrado se o `uvicorn` rodar fora da raiz do repo.
_TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")
templates = Jinja2Templates(directory=_TEMPLATES_DIR)


def _contexto_base(request: Request) -> dict:
    return {"request": request, "api_key": os.environ.get("API_KEY", "")}


@router.get("/")
def tela_inicio(request: Request):
    return templates.TemplateResponse("index.html", _contexto_base(request))


@router.get("/formulario-web")
def tela_formulario_web(request: Request, conn: Connection = Depends(get_connection)):
    contexto = _contexto_base(request)
    contexto["categorias"] = listar_categorias(conn)
    return templates.TemplateResponse("formulario_web.html", contexto)


@router.get("/pinpad")
def tela_pinpad(request: Request, conn: Connection = Depends(get_connection)):
    contexto = _contexto_base(request)
    contexto["categorias"] = listar_categorias(conn)
    return templates.TemplateResponse("pinpad.html", contexto)


@router.get("/totem")
def tela_totem(request: Request):
    return templates.TemplateResponse("totem.html", _contexto_base(request))


@router.get("/telemarketing-simulador")
def tela_telemarketing_simulador(request: Request, conn: Connection = Depends(get_connection)):
    contexto = _contexto_base(request)
    contexto["categorias"] = listar_categorias(conn)
    contexto["clientes"] = listar_clientes(conn)
    return templates.TemplateResponse("telemarketing_simulador.html", contexto)

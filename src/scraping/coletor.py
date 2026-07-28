"""
Coleta HTTP das páginas fixture (ver ADR-010, ADR-011).

Faz requisição HTTP real (requests) contra as páginas servidas pelo
próprio processo FastAPI/uvicorn já em execução (StaticFiles) — não lê os
arquivos do disco diretamente. Isso preserva o objetivo técnico do
ADR-010: demonstrar scraping de verdade (requisição HTTP + parsing de
HTML), não apenas leitura de arquivo local.
"""
import requests
from bs4 import BeautifulSoup

BASE_URL = "http://localhost:8000/fixtures/reviews"
PRIMEIRA_PAGINA = "pagina_01.html"
TIMEOUT_SEGUNDOS = 5


def coletar_todas_paginas() -> list[str]:
    """
    Segue a paginação a partir do link 'Próxima' em cada página, em vez de
    assumir uma lista fixa de arquivos — simula um crawler real, que não
    conhece de antemão quantas páginas existem no site.
    """
    htmls = []
    proxima = PRIMEIRA_PAGINA

    while proxima:
        resposta = requests.get(f"{BASE_URL}/{proxima}", timeout=TIMEOUT_SEGUNDOS)
        resposta.raise_for_status()
        htmls.append(resposta.text)

        soup = BeautifulSoup(resposta.text, "html.parser")
        link_next = soup.select_one("a.pagination-next")
        proxima = link_next["href"] if link_next else None

    return htmls

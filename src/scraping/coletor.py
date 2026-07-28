"""
Coleta HTTP das páginas fixture (ver ADR-010, ADR-011).

Faz requisição HTTP real (requests) contra o site servido pelo próprio
processo FastAPI/uvicorn — não lê os arquivos do disco diretamente,
preservando o objetivo técnico do ADR-010 (scraping de verdade).

Navegação em 2 níveis, batendo com o site real:
    1. Páginas de listagem (1-5), descobertas pela paginação numerada
       (não assumidas por nome de arquivo).
    2. Para cada avaliação na listagem, a página de detalhe (onde estão
       todos os campos completos: nome, nota, comentário, respondido,
       resolvido, voltaria).

URL do servidor via variável de ambiente `URL_SERVIDOR` — necessário
porque no GitHub Codespaces a URL pública muda a cada Codespace
(ex.: https://<nome-do-codespace>-8000.app.github.dev), diferente de
`http://localhost:8000` em ambiente local.
"""
import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

TIMEOUT_SEGUNDOS = 5


def _base_url() -> str:
    """
    Lê a env var a cada chamada (em vez de constante fixada no import)
    para funcionar bem em testes/notebooks que ajustam a variável em
    tempo de execução.
    """
    url_servidor = os.environ["URL_SERVIDOR"]
    return f"{url_servidor.rstrip('/')}/fixtures/reviews"


def _buscar(caminho_relativo: str) -> str:
    resposta = requests.get(f"{_base_url()}/{caminho_relativo}", timeout=TIMEOUT_SEGUNDOS)
    resposta.raise_for_status()
    return resposta.text


def _descobrir_paginas_listagem(html_primeira_pagina: str) -> list[str]:
    """Lê a paginação numerada da própria página, em vez de assumir
    5 páginas fixas — simula um crawler real, que não sabe de antemão
    quantas páginas existem."""
    soup = BeautifulSoup(html_primeira_pagina, "html.parser")
    links = [a["href"] for a in soup.select(".paginacao a")]
    paginas = ["pagina_01.html"] + links
    # remove duplicatas mantendo a ordem
    vistas: list[str] = []
    for p in paginas:
        if p not in vistas:
            vistas.append(p)
    return vistas


def _extrair_links_avaliacoes(html_listagem: str) -> list[str]:
    soup = BeautifulSoup(html_listagem, "html.parser")
    return [a["href"] for a in soup.select(".review-link")]


def coletar_htmls_detalhe() -> list[str]:
    """
    Percorre todas as páginas de listagem e, para cada avaliação, coleta
    o HTML da página de detalhe correspondente (fonte de verdade — a
    listagem só tem o comentário truncado).
    """
    html_pagina_1 = _buscar("pagina_01.html")
    paginas_listagem = _descobrir_paginas_listagem(html_pagina_1)

    htmls_detalhe = []
    for i, pagina in enumerate(paginas_listagem):
        html_listagem = html_pagina_1 if i == 0 else _buscar(pagina)
        for link_avaliacao in _extrair_links_avaliacoes(html_listagem):
            htmls_detalhe.append(_buscar(link_avaliacao))

    return htmls_detalhe
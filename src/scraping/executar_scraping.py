"""
Orquestrador do scraping — entry point.

Uso:
    python src/scraping/executar_scraping.py

Pré-requisitos:
- FastAPI (uvicorn) já em execução, servindo as fixtures em
  /fixtures/reviews/ (ver main.py — mount de StaticFiles).
- Rodar em GitHub Codespaces: o script conecta diretamente ao Supabase
  (porta 5432), bloqueada na rede corporativa do autor (ver status.md).
"""
from src.scraping.coletor import coletar_todas_paginas
from src.scraping.conexao import obter_conexao
from src.scraping.gravacao import gravar_lote
from src.scraping.parser import extrair_avaliacoes
from src.scraping.tratamento import tratar_lote


def main() -> None:
    print("Coletando páginas via HTTP...")
    paginas_html = coletar_todas_paginas()
    print(f"{len(paginas_html)} página(s) coletada(s).")

    brutas = [item for html in paginas_html for item in extrair_avaliacoes(html)]
    print(f"{len(brutas)} avaliação(ões) extraída(s).")

    validas, descartadas = tratar_lote(brutas)
    if descartadas:
        print(f"{len(descartadas)} registro(s) descartado(s):")
        for item in descartadas:
            print(f"  - review_id={item.get('review_id')}: {item['motivo_descarte']}")

    conn = obter_conexao()
    try:
        total_gravado = gravar_lote(conn, validas)
        print(f"{total_gravado} avaliação(ões) gravada(s) em avaliacoes.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()

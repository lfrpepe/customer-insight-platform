"""
Parsing das páginas HTML coletadas — extrai cada review-card em um dict
bruto. Sem validação/limpeza aqui (ver tratamento.py) — este módulo só
sabe extrair o que está no DOM, não julgar se o dado é válido.
"""
from bs4 import BeautifulSoup


def extrair_avaliacoes(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    avaliacoes = []

    for card in soup.select("div.review-card"):
        rating_el = card.select_one(".review-rating")
        date_el = card.select_one(".review-date")
        location_el = card.select_one(".review-location")
        comment_el = card.select_one(".review-comment")

        avaliacoes.append({
            "review_id": card.get("data-review-id"),
            "nota_bruta": rating_el.get("data-nota") if rating_el else None,
            "data_bruta": date_el.get("datetime") if date_el else None,
            "localizacao_bruta": location_el.get_text(strip=True) if location_el else None,
            "comentario_bruto": comment_el.get_text(strip=True) if comment_el else None,
        })

    return avaliacoes

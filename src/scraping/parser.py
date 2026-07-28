"""
Parsing das páginas de DETALHE (não da listagem — lá o comentário vem
truncado). Extrai um dict bruto por avaliação, sem validação (ver
tratamento.py).

Campos extraídos, além de nota/comentário (já usados antes): nome do
autor, se a empresa respondeu, e — só quando respondida — se o problema
foi resolvido e se a pessoa voltaria a fazer negócio. Esses três últimos
não vão para `avaliacoes` (schema não tem essas colunas, ver ADR-012) —
são extraídos aqui só para permitir uma análise de sentimento mais
completa antes de decidir o que persistir.
"""
from bs4 import BeautifulSoup


def extrair_avaliacao_detalhe(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    card = soup.select_one(".review-card")

    nome_el = card.select_one(".review-meta .nome")
    local_data_el = card.select_one(".review-meta .local-data")
    rating_el = card.select_one(".review-rating")
    comentario_el = card.select_one(".review-comment")
    respondido_el = card.select_one(".respondido-tag")
    resolvido_el = card.select_one('.badge[data-campo="resolvido"]')
    voltaria_el = card.select_one('.badge[data-campo="voltaria"]')

    return {
        "review_id": card.get("data-review-id"),
        "nome_bruto": nome_el.get_text(strip=True) if nome_el else None,
        # Texto cru "Cidade/UF · dd/mm/aaaa" — não há atributo data-* limpo
        # para a data no site fixture; o regex fica em tratamento.py.
        "data_bruta": local_data_el.get_text(strip=True) if local_data_el else None,
        "nota_bruta": rating_el.get("data-nota") if rating_el else None,
        "comentario_bruto": comentario_el.get_text(strip=True) if comentario_el else None,
        # .respondido-tag sempre existe (ver template) — data-respondido é "sim"/"nao"
        "respondido_bruto": respondido_el.get("data-respondido") if respondido_el else None,
        # .badges só existe quando respondido="sim" (ver ADR-012) — ausente = None
        "resolvido_bruto": resolvido_el.get("data-valor") if resolvido_el else None,
        "voltaria_bruto": voltaria_el.get("data-valor") if voltaria_el else None,
    }


def extrair_avaliacoes(htmls_detalhe: list[str]) -> list[dict]:
    return [extrair_avaliacao_detalhe(html) for html in htmls_detalhe]
"""
Limpeza e validação do dado extraído, antes de qualquer gravação.

Nesta etapa (exploração de dados, ver status.md) o objetivo é só validar
a estrutura — nada aqui grava no banco. `resolvido`/`voltaria` ficam
`None` quando a avaliação não foi respondida pela empresa (não é erro,
é ausência esperada — ver ADR-012).
"""
import re
from datetime import date, datetime

_PADRAO_DATA = re.compile(r"(\d{2}/\d{2}/\d{4})")


class AvaliacaoInvalida(Exception):
    pass


def tratar_avaliacao(bruta: dict) -> dict:
    return {
        "review_id": bruta["review_id"],
        "nome": _tratar_nome(bruta["nome_bruto"]),
        "data_avaliacao": _tratar_data(bruta["data_bruta"]),
        "nota": _tratar_nota(bruta["nota_bruta"]),
        "comentario": _tratar_comentario(bruta["comentario_bruto"]),
        "respondido": _tratar_booleano(bruta["respondido_bruto"]),
        "resolvido": _tratar_booleano(bruta["resolvido_bruto"]),
        "voltaria": _tratar_booleano(bruta["voltaria_bruto"]),
    }


def _tratar_nome(nome_bruto: str | None) -> str:
    if not nome_bruto or not nome_bruto.strip():
        raise AvaliacaoInvalida("nome ausente")
    return nome_bruto.strip()


def _tratar_data(texto_bruto: str | None) -> date:
    """
    Extrai a data de um texto misturado com cidade/estado, ex.:
    "Porto Alegre/RS · 24/03/2026" -> date(2026, 3, 24).

    Regex em vez de atributo data-* limpo: decisão consciente (o site
    fixture não tem <time datetime="...">), mais fiel a um cenário real
    de scraping, onde a data raramente vem isolada.
    """
    if not texto_bruto:
        raise AvaliacaoInvalida("texto de data/local ausente")

    match = _PADRAO_DATA.search(texto_bruto)
    if not match:
        raise AvaliacaoInvalida(f"nenhuma data no formato dd/mm/aaaa encontrada em: {texto_bruto!r}")

    return datetime.strptime(match.group(1), "%d/%m/%Y").date()


def _tratar_nota(nota_bruta: str | None) -> int:
    if nota_bruta is None:
        raise AvaliacaoInvalida("nota ausente")
    try:
        nota = int(nota_bruta)
    except ValueError:
        raise AvaliacaoInvalida(f"nota não numérica: {nota_bruta!r}")
    if not 1 <= nota <= 5:
        raise AvaliacaoInvalida(f"nota fora do intervalo 1-5: {nota}")
    return nota


def _tratar_comentario(comentario_bruto: str | None) -> str:
    if not comentario_bruto or not comentario_bruto.strip():
        raise AvaliacaoInvalida("comentário vazio")
    return comentario_bruto.strip()


def _tratar_booleano(valor_bruto: str | None) -> bool | None:
    """
    'sim' -> True, 'nao' -> False, ausente -> None (empresa ainda não
    respondeu, então resolvido/voltaria estruturalmente não existem —
    ver ADR-012). Diferente de nota/comentário, ausência aqui não é erro.
    """
    if valor_bruto is None:
        return None
    return valor_bruto == "sim"


def tratar_lote(brutas: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    Retorna (validas, descartadas). Registros descartados carregam o
    motivo, para log/auditoria — um item malformado não derruba o lote
    inteiro.
    """
    validas, descartadas = [], []
    for bruta in brutas:
        try:
            validas.append(tratar_avaliacao(bruta))
        except AvaliacaoInvalida as erro:
            descartadas.append({**bruta, "motivo_descarte": str(erro)})
    return validas, descartadas
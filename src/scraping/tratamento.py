"""
Limpeza e validação do dado extraído, antes da gravação.

As regras espelham as constraints já existentes no banco (nota entre 1 e
5, ver data_model_relational.md) — validar aqui evita depender só do
CHECK do Postgres e permite descartar/logar registros malformados sem
interromper o processamento do lote inteiro.
"""
from datetime import date, datetime


class AvaliacaoInvalida(Exception):
    pass


def tratar_avaliacao(bruta: dict) -> dict:
    return {
        "data_avaliacao": _tratar_data(bruta["data_bruta"]),
        "nota": _tratar_nota(bruta["nota_bruta"]),
        "comentario": _tratar_comentario(bruta["comentario_bruto"]),
    }


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


def _tratar_data(data_bruta: str | None) -> date:
    if not data_bruta:
        raise AvaliacaoInvalida("data ausente")
    try:
        return datetime.strptime(data_bruta, "%Y-%m-%d").date()
    except ValueError:
        raise AvaliacaoInvalida(f"data em formato inesperado: {data_bruta!r}")


def _tratar_comentario(comentario_bruto: str | None) -> str:
    if not comentario_bruto or not comentario_bruto.strip():
        # Origem Scraping exige comentário conhecido (ver tabela
        # "Preenchimento por origem" em data_model_relational.md).
        raise AvaliacaoInvalida("comentário vazio")
    return comentario_bruto.strip()


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

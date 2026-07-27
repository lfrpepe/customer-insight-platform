"""
Extração de dados do PostgreSQL (Supabase) para pandas DataFrame.

Sem transformação de nenhum tipo aqui — Bronze é cópia raw (ver
architecture.md). A única coluna adicionada fora da origem é a de
auditoria (`_carregado_em`), tratada em carga.py.
"""

from datetime import datetime
from typing import Optional

import pandas as pd
import pg8000


def extrair_completa(conn: pg8000.Connection, tabela: str) -> pd.DataFrame:
    """Lê a tabela inteira — usado para tabelas com estratégia 'full'."""
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {tabela}")
    colunas = [desc[0] for desc in cursor.description]
    linhas = cursor.fetchall()
    return pd.DataFrame(linhas, columns=colunas)


def extrair_incremental(
    conn: pg8000.Connection,
    tabela: str,
    coluna_watermark: str,
    desde: Optional[datetime],
) -> pd.DataFrame:
    """
    Lê apenas as linhas novas desde a última carga bem-sucedida
    (`desde`). Se `desde` for None (primeira execução), lê a tabela
    inteira — mesmo efeito de uma carga full na primeira vez.
    """
    cursor = conn.cursor()
    if desde is None:
        cursor.execute(f"SELECT * FROM {tabela}")
    else:
        cursor.execute(
            f"SELECT * FROM {tabela} WHERE {coluna_watermark} > %s",
            (desde,),
        )
    colunas = [desc[0] for desc in cursor.description]
    linhas = cursor.fetchall()
    return pd.DataFrame(linhas, columns=colunas)

"""
Conexão com o banco operacional (Supabase/PostgreSQL).

Generaliza o mesmo padrão usado em `database/scripts/generate_seed_dev.py`
(ver ADR-001 e ADR-005): pg8000, Python puro, sem dependência de pg_config
no sistema operacional local.
"""

import os
from typing import Iterator

import pg8000.dbapi
from dotenv import load_dotenv

load_dotenv()


def _conectar() -> pg8000.dbapi.Connection:
    """
    Abre uma nova conexão com o Supabase.

    Lê credenciais do .env (nunca hardcoded — repositório é público).
    Variáveis esperadas: SUPABASE_DB_HOST, SUPABASE_DB_PORT,
    SUPABASE_DB_NAME, SUPABASE_DB_USER, SUPABASE_DB_PASSWORD.
    """
    return pg8000.connect(
        host=os.environ["SUPABASE_DB_HOST"],
        port=int(os.environ.get("SUPABASE_DB_PORT", "5432")),
        database=os.environ.get("SUPABASE_DB_NAME", "postgres"),
        user=os.environ["SUPABASE_DB_USER"],
        password=os.environ["SUPABASE_DB_PASSWORD"],
    )


def get_connection() -> Iterator[pg8000.dbapi.Connection]:
    """
    Dependência do FastAPI: `conn = Depends(get_connection)`.

    Uma conexão nova por requisição. Comita se a rota terminar sem
    exceção; reverte (rollback) e propaga o erro caso contrário. A conexão
    é sempre fechada ao final, devolvendo o socket ao pooler do Supabase.

    Isolamento: cada requisição de Create (Formulário Web/Pinpad/Totem/
    Telemarketing) é uma transação única e independente — não há motivo
    para reaproveitar conexão entre requisições neste volume de tráfego.
    """
    conn = _conectar()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

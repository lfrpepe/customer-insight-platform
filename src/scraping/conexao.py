"""
Conexão isolada com o PostgreSQL (Supabase) para o módulo de scraping.

Desacoplada de src/database/connection.py por decisão de projeto — ver
ADR-011 (docs/decisions/011-scraper-gravacao-propria-desacoplada.md): o
scraper deve rodar como processo independente do backend, sem importar
nenhum código do FastAPI.

Driver: pg8000, mesmo padrão do restante do projeto (ADR-001, ADR-005) —
Python puro, sem dependência nativa compilada.

Variáveis de ambiente esperadas (mesmas credenciais do Supabase já usadas
pelo backend — ajuste os nomes abaixo para bater com o .env.example real
do projeto, caso os nomes lá sejam diferentes):
    DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT (opcional, default 5432)
"""
import os

import pg8000
from dotenv import load_dotenv

load_dotenv()


def obter_conexao() -> pg8000.Connection:
    """Abre uma conexão isolada com o Supabase via Session Pooler (porta 5432)."""
    return pg8000.connect(
        user=os.environ["SUPABASE_DB_USER"],
        password=os.environ["SUPABASE_DB_PASSWORD"],
        host=os.environ["SUPABASE_DB_HOST"],
        port=int(os.environ.get("SUPABASE_DB_PORT", 5432)),
        database=os.environ.get("SUPABASE_DB_NAME", "postgres"),
        timeout=10,
    )

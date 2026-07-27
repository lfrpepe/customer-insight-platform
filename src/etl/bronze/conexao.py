"""
Conexão PostgreSQL (Supabase) a partir do Databricks, via `pg8000`.

Driver `pg8000` por decisão do ADR-001/ADR-005 (Python puro, sem
dependência nativa compilada — requisito do compute serverless do
Databricks Free Edition).

Credenciais nunca hardcoded: lidas via Databricks Secrets (scope
`customer-insight-platform`, ver config.py), o equivalente ao `.env` já
usado no backend FastAPI (Codespaces/local), adaptado ao ambiente
Databricks.
"""

import pg8000

from src.etl.bronze.config import SECRET_SCOPE


def _obter_dbutils():
    """
    Retorna o objeto `dbutils`, disponível automaticamente em notebooks
    Databricks, mas que precisa ser reconstruído quando o código roda a
    partir de um módulo .py (ex.: task do tipo "Python script" num Job).
    """
    try:
        return dbutils  # noqa: F821 - injetado pelo runtime do notebook
    except NameError:
        from pyspark.dbutils import DBUtils
        from pyspark.sql import SparkSession

        spark = SparkSession.builder.getOrCreate()
        return DBUtils(spark)


def conectar() -> pg8000.Connection:
    """
    Abre uma conexão com o Supabase via Session Pooler (porta 5432),
    mesmo padrão de conexão usado no backend (ver ADR-001).
    """
    du = _obter_dbutils()

    host = du.secrets.get(scope=SECRET_SCOPE, key="pg-host")
    database = du.secrets.get(scope=SECRET_SCOPE, key="pg-database")
    user = du.secrets.get(scope=SECRET_SCOPE, key="pg-user")
    password = du.secrets.get(scope=SECRET_SCOPE, key="pg-password")

    return pg8000.connect(
        host=host,
        port=5432,
        database=database,
        user=user,
        password=password,
        timeout=10,
    )

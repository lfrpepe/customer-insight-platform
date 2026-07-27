"""
Gravação de DataFrames extraídos do Postgres nas tabelas Delta do Bronze.

Sem regra de negócio, sem deduplicação, sem enriquecimento — só a
coluna de auditoria `_carregado_em` é adicionada (ver architecture.md,
seção Bronze).
"""

from datetime import datetime, timezone

import pandas as pd
from pyspark.sql import SparkSession


def _lit_agora():
    from pyspark.sql.functions import lit

    return lit(datetime.now(timezone.utc))


def gravar_full(spark: SparkSession, pdf: pd.DataFrame, tabela_bronze: str) -> int:
    """
    Overwrite completo da tabela Bronze — usado para catálogo e
    `clientes` (ver ADR-008). Retorna a quantidade de linhas gravadas.
    """
    if pdf.empty:
        return 0
    df = spark.createDataFrame(pdf).withColumn("_carregado_em", _lit_agora())
    df.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(tabela_bronze)
    return df.count()


def gravar_incremental(spark: SparkSession, pdf: pd.DataFrame, tabela_bronze: str) -> int:
    """
    Append apenas das linhas novas — usado para `avaliacoes` (ver
    ADR-008). Se não houver linhas novas, não faz nada (evita escrita
    vazia desnecessária). Retorna a quantidade de linhas gravadas.
    """
    if pdf.empty:
        return 0
    df = spark.createDataFrame(pdf).withColumn("_carregado_em", _lit_agora())
    df.write.mode("append").saveAsTable(tabela_bronze)
    return df.count()

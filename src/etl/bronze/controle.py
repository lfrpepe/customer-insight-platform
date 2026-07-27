"""
Controle de watermark da ingestão incremental (ver ADR-008).

A tabela `bronze.controle_ingestao` guarda, por tabela de origem, o
timestamp mais recente já carregado com sucesso — usado para saber a
partir de onde continuar na próxima execução (hoje, só `avaliacoes`
usa isso; ver config.py).
"""

from datetime import datetime
from typing import Optional

from pyspark.sql import Row, SparkSession

from src.etl.bronze.config import TABELA_CONTROLE


def obter_ultima_carga(spark: SparkSession, tabela_postgres: str) -> Optional[datetime]:
    """
    Retorna o timestamp da última carga bem-sucedida para a tabela, ou
    None se ainda não houve nenhuma carga registrada (primeira execução).
    """
    df = spark.table(TABELA_CONTROLE).filter(f"nome_tabela = '{tabela_postgres}'")
    linha = df.select("ultima_carga_em").collect()
    return linha[0]["ultima_carga_em"] if linha else None


def atualizar_ultima_carga(
    spark: SparkSession, tabela_postgres: str, novo_watermark: datetime
) -> None:
    """
    Grava (upsert manual) o novo watermark para a tabela — só deve ser
    chamado depois que a carga no Bronze já foi confirmada com sucesso,
    nunca antes, para não perder linhas em caso de falha no meio da
    execução.
    """
    spark.sql(f"DELETE FROM {TABELA_CONTROLE} WHERE nome_tabela = '{tabela_postgres}'")
    novo_registro = spark.createDataFrame(
        [Row(nome_tabela=tabela_postgres, ultima_carga_em=novo_watermark)]
    )
    novo_registro.write.mode("append").saveAsTable(TABELA_CONTROLE)

"""
Ingestão PostgreSQL (Supabase) -> Databricks Bronze.

Entry point do Job do Databricks (ADR-009: Databricks Jobs nativo,
execução sob demanda). Configurar o Job com:
  - Task type: "Python script"
  - Source: este arquivo (via Databricks Repos, apontando para o clone
    do repositório GitHub do projeto)
  - Trigger: nenhum (manual) nesta fase

Percorre `TABELAS_BRONZE` (config.py) e, para cada tabela, aplica a
estratégia definida no ADR-008 (full overwrite ou incremental por
watermark). Uma falha em uma tabela não impede a tentativa nas
demais — o resumo final reporta o que funcionou e o que falhou.
"""

from pyspark.sql import SparkSession

from src.etl.bronze.carga import gravar_full, gravar_incremental
from src.etl.bronze.conexao import conectar
from src.etl.bronze.config import TABELAS_BRONZE
from src.etl.bronze.controle import atualizar_ultima_carga, obter_ultima_carga
from src.etl.bronze.extracao import extrair_completa, extrair_incremental


def ingerir_tabela(spark: SparkSession, conn, config: dict) -> tuple[str, int, str]:
    """
    Executa a ingestão de uma única tabela.
    Retorna (nome_tabela, linhas_gravadas, status) para o resumo final.
    """
    tabela_postgres = config["tabela_postgres"]
    tabela_bronze = config["tabela_bronze"]
    estrategia = config["estrategia"]

    if estrategia == "full":
        pdf = extrair_completa(conn, tabela_postgres)
        linhas = gravar_full(spark, pdf, tabela_bronze)
        return tabela_postgres, linhas, "ok (full)"

    if estrategia == "incremental":
        coluna_watermark = config["coluna_watermark"]
        ultima_carga = obter_ultima_carga(spark, tabela_postgres)
        pdf = extrair_incremental(conn, tabela_postgres, coluna_watermark, ultima_carga)
        linhas = gravar_incremental(spark, pdf, tabela_bronze)

        if not pdf.empty:
            novo_watermark = pdf[coluna_watermark].max()
            atualizar_ultima_carga(spark, tabela_postgres, novo_watermark)

        return tabela_postgres, linhas, "ok (incremental)"

    raise ValueError(f"Estratégia desconhecida para {tabela_postgres}: {estrategia}")


def main() -> None:
    spark = SparkSession.builder.getOrCreate()
    spark.sql("CREATE SCHEMA IF NOT EXISTS bronze")

    conn = conectar()
    resumo: list[tuple[str, int, str]] = []

    try:
        for config in TABELAS_BRONZE:
            tabela = config["tabela_postgres"]
            try:
                resultado = ingerir_tabela(spark, conn, config)
                resumo.append(resultado)
            except Exception as erro:  # noqa: BLE001 - resumo cobre a falha pontual
                resumo.append((tabela, 0, f"falhou: {erro}"))
    finally:
        conn.close()

    print("Resumo da ingestão Bronze:")
    for tabela, linhas, status in resumo:
        print(f"  - {tabela}: {linhas} linha(s) — {status}")

    falhas = [r for r in resumo if r[2].startswith("falhou")]
    if falhas:
        raise RuntimeError(
            f"{len(falhas)} tabela(s) falharam na ingestão: "
            f"{', '.join(t for t, _, _ in falhas)}"
        )


if __name__ == "__main__":
    main()

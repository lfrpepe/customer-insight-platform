-- Setup da camada Bronze no Databricks (ver ADR-008).
-- Rodar uma única vez (manualmente, num notebook SQL do Databricks)
-- antes da primeira execução do Job de ingestão.

CREATE SCHEMA IF NOT EXISTS bronze;

-- Tabela de controle de watermark para as tabelas com estratégia
-- "incremental" (hoje, apenas `avaliacoes` — ver config.py).
-- Uma linha por tabela de origem monitorada.
CREATE TABLE IF NOT EXISTS bronze.controle_ingestao (
    nome_tabela      STRING    NOT NULL,
    ultima_carga_em  TIMESTAMP NOT NULL
)
USING DELTA;

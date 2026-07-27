"""
Configuração declarativa das tabelas ingeridas na camada Bronze.

Cada entrada descreve UMA tabela de origem (PostgreSQL) e como ela deve
ser carregada no Bronze (Databricks). A estratégia por tabela segue o
ADR-008 (docs/decisions/008-estrategia-ingestao-bronze.md):

- "full"        -> overwrite completo a cada execução (catálogo + clientes)
- "incremental" -> append apenas das linhas novas, via watermark de coluna
                   de data/timestamp (usado só em `avaliacoes`)

Adicionar uma nova tabela ao Bronze = adicionar uma entrada aqui, sem
tocar no restante do pipeline.
"""

from typing import Literal, TypedDict


class ConfigTabela(TypedDict, total=False):
    tabela_postgres: str       # nome da tabela na origem (schema public)
    tabela_bronze: str          # nome completo no Databricks (schema.tabela)
    estrategia: Literal["full", "incremental"]
    coluna_watermark: str       # obrigatória apenas quando estrategia == "incremental"


TABELAS_BRONZE: list[ConfigTabela] = [
    {
        "tabela_postgres": "estados",
        "tabela_bronze": "bronze.estados",
        "estrategia": "full",
    },
    {
        "tabela_postgres": "cidades",
        "tabela_bronze": "bronze.cidades",
        "estrategia": "full",
    },
    {
        "tabela_postgres": "categorias",
        "tabela_bronze": "bronze.categorias",
        "estrategia": "full",
    },
    {
        "tabela_postgres": "origens_avaliacao",
        "tabela_bronze": "bronze.origens_avaliacao",
        "estrategia": "full",
    },
    {
        "tabela_postgres": "clientes",
        "tabela_bronze": "bronze.clientes",
        "estrategia": "full",
    },
    {
        "tabela_postgres": "avaliacoes",
        "tabela_bronze": "bronze.avaliacoes",
        "estrategia": "incremental",
        "coluna_watermark": "criado_em",
    },
]

# Nome da tabela de controle de watermarks (ver ADR-008)
TABELA_CONTROLE = "bronze.controle_ingestao"

# Scope de secrets do Databricks onde as credenciais do Supabase estão
# cadastradas (ver conexao.py) — criado via:
#   databricks secrets create-scope customer-insight-platform
#   databricks secrets put-secret customer-insight-platform pg-host
#   databricks secrets put-secret customer-insight-platform pg-database
#   databricks secrets put-secret customer-insight-platform pg-user
#   databricks secrets put-secret customer-insight-platform pg-password
SECRET_SCOPE = "customer-insight-platform"

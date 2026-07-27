# ADR 008 — Estratégia de ingestão PostgreSQL → Databricks Bronze

**Status:** Aceito
**Data:** 2026-07-27
**Fase:** 6 — ETL

## Contexto

Com o backend (Fase 5) concluído e gravando em produção no PostgreSQL
(Supabase), a Fase 6 precisa definir como os dados chegam à camada Bronze
(Databricks), conforme já estabelecido em `architecture.md`: Bronze é cópia
raw, sem regras de negócio, sem agregações, apenas ingestão.

Duas perguntas técnicas precisavam de decisão antes de qualquer código:

1. Qual driver/método de extração usar a partir do Databricks?
2. A carga deve ser sempre um snapshot completo, ou incremental?

## Decisão

### Extração: `pg8000` + pandas + `spark.createDataFrame()`

Reaproveita o driver já validado no ADR-001 (`pg8000`, Python puro, sem
dependência nativa compilada — requisito do compute serverless do
Databricks Free Edition). Para o volume atual (centenas/milhares de
linhas), ler via `pg8000` para um `pandas.DataFrame` e converter para Spark
é simples, sem overhead relevante, e não introduz um driver novo no
projeto.

### Carga por tabela: full snapshot para catálogo/dimensão, incremental por watermark para `avaliacoes`

| Tabela                                              | Estratégia                          | Motivo |
|------------------------------------------------------|--------------------------------------|--------|
| `estados`, `cidades`, `categorias`, `origens_avaliacao` | Full overwrite a cada execução        | Catálogo, baixíssimo volume — reprocessar tudo é mais simples que rastrear mudanças e não tem custo relevante |
| `clientes`                                            | Full overwrite a cada execução        | Volume ainda baixo (centenas de linhas), mas sofre `UPDATE` (ex.: normalização de telefone já feita, futura API ViaCEP) — overwrite captura essas mudanças sem exigir lógica de CDC |
| `avaliacoes`                                          | Incremental, por watermark `criado_em` | Única tabela append-only e que cresce continuamente — full reload ficaria caro sem necessidade conforme o volume aumenta |

Controle do watermark: tabela `bronze.controle_ingestao`
(`nome_tabela`, `ultima_carga_em`), atualizada ao final de cada execução
bem-sucedida. Consulta de extração de `avaliacoes`:

```sql
SELECT * FROM avaliacoes WHERE criado_em > :ultima_carga_em
```

Todas as tabelas Bronze recebem a coluna de auditoria `_carregado_em`
(timestamp da execução do job), além dos campos originais — incluindo
`natureza_registro`, que **não é filtrado** nesta camada (Bronze ingere
tudo, conforme já definido em `architecture.md`).

## Alternativas consideradas

| Alternativa | Motivo de descarte |
|---|---|
| `spark.read.jdbc()` direto com driver JDBC do Postgres | Exigiria instalar biblioteca Maven (`org.postgresql:postgresql`) no cluster; Free Edition é serverless-only, sem configuração de cluster tradicional, tornando a instalação de biblioteca incerta. `pg8000` já está validado no ambiente (ADR-001). Reavaliar se o volume crescer para múltiplos milhões de linhas. |
| Full reload também para `avaliacoes` | Simples de implementar, mas o custo cresce linearmente com o volume histórico a cada execução, sem necessidade — a tabela nunca é editada após o insert. |
| Structured Streaming / Auto Loader | Pensado para ingestão de arquivos (não é o caso — a fonte é uma tabela transacional via conexão JDBC/driver Python) ou CDC de streaming; overkill para o padrão de acesso deste projeto (execução sob demanda, não contínua — ver ADR-009). |

## Consequências

- Novo schema `bronze` no metastore do workspace Databricks.
- Nova tabela de controle `bronze.controle_ingestao`.
- Script/notebook de ingestão organizado por tabela, reaproveitando um
  módulo único de conexão (`pg8000`), análogo ao padrão já usado em
  `generate_seed_dev.py` e `src/database/connection.py`.
- Sem mudança em `schema.sql` nem nos ADRs 001-007 — decisão é inteiramente
  do lado Databricks/ETL.
- Rastreabilidade: este ADR complementa `architecture.md` (seção Bronze) e
  precede a implementação do notebook/script de ingestão.

# Status do Projeto — Customer Insight Platform

**Última atualização:** 2026-07-23
**Fase atual:** 1 — Modelagem de Dados → **Concluída**
**Próxima fase:** 2 — Estrutura do Repositório / Banco de Dados (implementação)

## Ambiente configurado

- [x] Repositório GitHub criado (`customer-insight-platform`), com README e `.gitignore` Python
- [x] Conta Supabase criada (organização Personal, plano Free)
- [x] Projeto Supabase provisionado
  - Data API: desabilitada (acesso será sempre via conexão direta ao Postgres)
  - Automatic exposure de novas tabelas: desabilitado
  - RLS automático: mantido habilitado (default seguro)
- [x] Conta Databricks Free Edition criada, workspace provisionado
- [x] PoC de conectividade Databricks ↔ Supabase realizada com sucesso

## Decisões técnicas registradas (ADRs)

- **ADR 001** — Uso de `pg8000` (não `psycopg2`) para conexões PostgreSQL a partir
  de código Python rodando no Databricks Free Edition, devido a incompatibilidade
  do driver nativo `psycopg2-binary` com o ambiente serverless.

## Decisões de ambiente (não formalizadas como ADR, mas relevantes)

- Ambiente de desenvolvimento local: GitHub Codespaces como opção principal
  (sem dependência de instalação aprovada por TI), com Python/Git/VS Code local
  já disponíveis como alternativa.
- Docker (quando liberado) será usado para Postgres local de desenvolvimento/teste,
  mantendo o Supabase como banco operacional real acessado pelo Databricks — os
  dois não são substitutos um do outro.
- Conexão ao Supabase via **Session Pooler** (porta 5432, IPv4), não via Direct
  Connection (IPv6-only no free tier) nem Transaction Pooler (voltado a conexões
  curtas/serverless, não é o padrão de uso aqui).
- Free tier do Supabase pausa após 7 dias de inatividade (dados preservados, sem
  backup automático). Decisão: aceitar pausa manual por enquanto; heartbeat via
  GitHub Actions fica para a Fase 2 (Qualidade e Automação), se necessário.

## Fase 1 — Modelagem de Dados

- [x] Modelo relacional definido (Clientes, Avaliações, Categorias, Origem,
  Cidade, Estado) — ver `docs/data_model_relational.md`
- [x] Script DDL de criação de schema — `src/database/scripts/schema.sql`
- [x] Rascunho inicial do modelo dimensional (Gold) — ver `docs/data_model_dimensional.md`

### Decisões de modelagem confirmadas

- Escala de nota: 1 a 5 (CHECK constraint)
- `id_cidade` em Clientes é opcional — resolvido via API (ViaCEP) a partir do CEP
- `comentario` em Avaliações é opcional — nem todo dado de scraping traz texto
- Sem constraint de deduplicação de avaliações no Postgres — responsabilidade
  da camada Silver (Databricks)

### Nota para a Fase de Ingestão (ainda não implementada)

Os dados fictícios devem simular clientes recorrentes, não um cliente novo por
avaliação. Estratégia definida: gerar um pool fixo de clientes fictícios
(ex. 200-500 registros) e, ao simular avaliações (scraping/geração), sortear
clientes existentes desse pool — idealmente com distribuição não uniforme
(poucos clientes concentrando a maioria das avaliações), para refletir o
padrão real de uma base de atendimento. Isso preserva o valor analítico de
`id_cliente` como chave estável (histórico por cliente, detecção de clientes
recorrentemente insatisfeitos etc.).

## Riscos monitorados

| Risco | Status |
|---|---|
| Databricks Free Edition bloquear acesso externo ao Supabase | **Descartado** — conectividade confirmada na PoC |
| `psycopg2` incompatível com serverless do Databricks | **Identificado e mitigado** — ver ADR 001 |
| Supabase free tier sem backup automático | Monitorado — mitigação via scripts de schema versionados no Git |
| Scraping de fontes como Reclame Aqui (ToS) | Ainda não avaliado — a validar na Fase de Ingestão |

## Próximos passos (Fase 1 — Modelagem de Dados)

- Modelagem relacional completa (Clientes, Avaliações, Categorias, Origem,
  Cidade, Estado)
- Scripts de criação de schema (DDL) versionados em `docs/database/`
- Rascunho inicial do modelo dimensional (Gold)

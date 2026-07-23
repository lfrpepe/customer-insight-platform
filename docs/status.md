# Status do Projeto — Customer Insight Platform

**Última atualização:** 2026-07-23
**Fase atual:** 0 — Fundação → **Concluída**
**Próxima fase:** 1 — Modelagem de Dados

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

# ADR 009 — Orquestração da ingestão Bronze via Databricks Jobs nativo

**Status:** Aceito
**Data:** 2026-07-27
**Fase:** 6 — ETL

## Contexto

A Fase 1 (Arquitetura) havia definido GitHub Actions como ferramenta de
orquestração geral do projeto (ver tabela "Ambiente e ferramentas" em
`architecture.md`), motivado por ser gratuito e versionado junto ao
código.

Ao detalhar a execução concreta da Fase 6 (ver
[ADR 008](008-estrategia-ingestao-bronze.md)), essa escolha foi
reavaliada: a alternativa de orquestrar via GitHub Actions exigiria uma
chamada de API do GitHub Actions para o Databricks Jobs API (token do
Databricks como secret no GitHub, chamada HTTP, tratamento de falha de
rede) — uma camada extra sem ganho real, já que o Databricks tem
scheduler e execução no mesmo lugar.

Verificação feita antes de decidir: o Databricks Free Edition suporta
nativamente Jobs (agendamento e execução), inclusive dentro da cota
gratuita — limite de 5 job tasks concorrentes por conta, bem acima da
necessidade deste projeto.

## Decisão

Usar o **agendador nativo de Jobs do Databricks** para disparar o
script/notebook de ingestão Bronze, com **execução sob demanda (disparo
manual)** nesta fase — sem agendamento automático por enquanto, por
decisão do autor.

GitHub Actions deixa de ser o orquestrador de pipeline de dados e passa a
ser reservado para **CI** (lint, testes automatizados do backend), papel
mais alinhado ao que a ferramenta resolve bem.

## Alternativas consideradas

| Alternativa | Motivo de descarte |
|---|---|
| GitHub Actions chamando a API de Jobs do Databricks (plano original da Fase 1) | Camada extra (token do Databricks como secret, chamada HTTP, tratamento de erro de rede) sem benefício real neste escopo — o Databricks já orquestra e executa no mesmo ambiente. |
| Agendamento automático (diário/horário) desde já | Descartado por ora — autor optou por controlar manualmente a execução nesta fase inicial do ETL, evitando cargas automáticas antes de validar o pipeline manualmente algumas vezes. Reavaliar quando o pipeline estiver maduro (possivelmente Fase 10 — Melhorias). |
| Lakeflow / Delta Live Tables (pipelines declarativos do Databricks) | Overengineering para o volume e a complexidade atual (poucas tabelas, sem múltiplos estágios encadeados ainda) — reavaliar se a Fase 7 (Engenharia de Dados) crescer em complexidade de dependências entre etapas. |

## Consequências

- `architecture.md`, tabela "Ambiente e ferramentas": linha de
  Orquestração atualizada de "GitHub Actions" para "Databricks Jobs
  (nativo)" — GitHub Actions permanece no projeto, mas com escopo de CI.
- Job configurado diretamente no workspace Databricks; não versionado
  automaticamente no Git nesta fase (pode ser exportado futuramente como
  Databricks Asset Bundle, se desejado — não necessário agora).
- Execução do notebook/script de ingestão Bronze é manual (autor dispara
  pelo Jobs UI) até uma decisão explícita de automatizar a cadência.
- Sem impacto em `schema.sql`, backend (Fase 5) ou ADRs 001-008.

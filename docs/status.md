# Status do Projeto — Customer Insight Platform

**Última atualização:** 2026-07-23
**Fase atual:** 2 — Estrutura do Repositório / Banco de Dados → **Em andamento**
**Próxima fase:** 5 — Backend (Flask, Pinpad/Totem, integração Telemarketing)

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
- **ADR 002** — FKs opcionais (`id_cliente`, `id_categoria`) em `avaliacoes`
  para suportar múltiplas origens de captura com preenchimento estruturalmente
  diferente.
- **ADR 003** — Coluna `natureza_registro` (`'Sintético'`/`'Real'`) em
  `clientes` e `avaliacoes`, para distinguir dado gerado pelo seed de
  desenvolvimento de dado capturado pelos sistemas reais (Flask, Pinpad,
  Totem, Telemarketing, Scraper).
- **ADR 004** — Nova origem de avaliação `Telemarketing - Pesquisa
  Pós-Atendimento` (IVR pós-ligação): cliente e categoria conhecidos, sem
  comentário (só o dígito da nota).
- **ADR 005** — Inicialmente propunha `psycopg2-binary` para scripts locais;
  **revertido no mesmo dia** após falha real de instalação no Windows
  (exigia compilação + `pg_config`, ausente no sistema). Decisão final:
  `pg8000` (Python puro, sem compilação) em todo o projeto — local e
  Databricks, um único driver.

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

## Fase 1 — Modelagem de Dados (Concluída)

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
- **`id_cliente` e `id_categoria` em Avaliações são opcionais (NULL, não
  sentinela)** — decisão tomada ao definir as origens de captura, cada uma
  com um subconjunto diferente de campos estruturalmente disponível:
  - `Formulário Web`: cliente conhecido, categoria conhecida, comentário opcional
  - `Pinpad - Atendente`: sem cliente, categoria conhecida (fixa por
    atendimento), sem comentário
  - `Totem - Autoatendimento`: sem cliente, sem categoria, sem comentário
  - `Telemarketing - Pesquisa Pós-Atendimento`: cliente conhecido, categoria
    conhecida, sem comentário (IVR só captura o dígito — ADR 004)
  - `Scraping`: sem cliente, sem categoria, comentário conhecido
  - `id_origem` continua `NOT NULL` em todos os casos — é sempre conhecido,
    independente da origem.
  - *Unknown member* (sentinela) para cliente/categoria fica para a camada
    Gold (`dim_cliente`/`dim_categoria`), não para o operacional.
- **`id_funcionario` propositalmente fora de escopo** — o Pinpad de
  atendente sugere naturalmente rastrear qual funcionário atendeu, mas essa
  FK só será adicionada quando a entidade `Funcionários` for modelada (fase
  futura do roadmap), para não antecipar dependência de algo ainda não
  definido. Mudança de baixo risco quando chegar a hora (`ALTER TABLE`
  aditivo, nullable).

### Nota para a Fase de Ingestão (ainda não implementada)

Os dados fictícios devem simular clientes recorrentes, não um cliente novo por
avaliação. Estratégia definida: gerar um pool fixo de clientes fictícios
(ex. 200-500 registros) e, ao simular avaliações (scraping/geração), sortear
clientes existentes desse pool — idealmente com distribuição não uniforme
(poucos clientes concentrando a maioria das avaliações), para refletir o
padrão real de uma base de atendimento. Isso preserva o valor analítico de
`id_cliente` como chave estável (histórico por cliente, detecção de clientes
recorrentemente insatisfeitos etc.). Aplica-se às origens `Formulário Web` e `Telemarketing` (únicas com
`id_cliente` conhecido); `Pinpad`, `Totem` e `Scraping` não capturam
`id_cliente`.

## Fase 2 — Estrutura do Repositório / Banco de Dados (Em andamento)

- [x] Estrutura de pastas do repositório definida (`src/`, `docs/`,
  `notebooks/`, `tests/`, `.github/`)
- [x] `schema.sql` atualizado com FKs opcionais em `avaliacoes` e seed das
  5 origens (`Formulário Web`, `Pinpad - Atendente`, `Totem -
  Autoatendimento`, `Telemarketing - Pesquisa Pós-Atendimento`, `Scraping`
  — ver ADR-004)
- [x] `docs/data_model_relational.md` atualizado com a tabela de
  preenchimento por origem
- [x] Seed de dados de desenvolvimento (pool de clientes fictícios) — ver
  `src/database/scripts/generate_seed_dev.py`. Passou por três versões:
  (1) geração de arquivos `.sql` para colar no SQL Editor — abandonada após
  erro de tamanho de query; (2) conexão direta via `psycopg2` — abandonada
  após falha de instalação no Windows (exigia compilar extensão C); (3)
  versão atual, conexão direta via `pg8000` (ADR-005). Volume: 500 clientes,
  5.000 avaliações, distribuídas 28/25/17/18/12% entre Formulário
  Web/Pinpad/Totem/Telemarketing/Scraping, todas com
  `natureza_registro = 'Sintético'`
- [x] Nota correlacionada ao cliente via perfis de satisfação
  (`insatisfeito_cronico` 15% / `neutro` 65% / `satisfeito_fiel` 20%),
  aplicável a Formulário Web e Telemarketing por serem as únicas origens
  com `id_cliente` conhecido — sustenta o objetivo de negócio "clientes
  recorrentemente insatisfeitos" citado acima. Recorrência calibrada
  (Pareto, alpha=3.5) para no máximo ~24 avaliações/cliente/ano, evitando
  concentração irreal
- [x] `generate_seed_dev.py` migrado de `psycopg2` para `pg8000` após falha
  de instalação (`psycopg2-binary` exigia compilar extensão C + `pg_config`
  ausente no Windows do autor) — ver atualização no ADR-005
- [ ] Rodar o script localmente e validar a carga no Supabase — pendente de
  execução pelo usuário
- [ ] Definição da tecnologia de interface do Pinpad/Totem (Streamlit
  standalone vs. rota Flask minimalista) — decisão adiada para a Fase 5

## Riscos monitorados

| Risco | Status |
|---|---|
| Databricks Free Edition bloquear acesso externo ao Supabase | **Descartado** — conectividade confirmada na PoC |
| `psycopg2` incompatível com serverless do Databricks | **Identificado e mitigado** — ver ADR 001 |
| Supabase free tier sem backup automático | Monitorado — mitigação via scripts de schema versionados no Git |
| Scraping de fontes como Reclame Aqui (ToS) | Ainda não avaliado — a validar na Fase de Ingestão |

## Próximos passos (Fase 2 — Banco de Dados)

- Seed de dados de desenvolvimento: pool de clientes fictícios + geração de
  avaliações distribuídas entre as 5 origens
- Confirmar estrutura de pastas com primeiro commit versionado
- Iniciar planejamento da Fase 5 (Backend): CRUD Flask + interface única
  Pinpad/Totem (com seleção de modo) + integração com sistema de
  Telemarketing

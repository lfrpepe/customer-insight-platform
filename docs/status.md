# Status do Projeto — Customer Insight Platform

**Última atualização:** 2026-07-24
**Fases concluídas:** 1 (Arquitetura), 2 (Modelagem de Dados), 3 (Estrutura
do Repositório), 4 (Banco de Dados)
**Próxima fase:** 5 — Backend (FastAPI, Pinpad/Totem, integração Telemarketing)

> Nota sobre numeração: as seções abaixo agrupam os passos 1-2 (Arquitetura
> + Modelagem de Dados) e 3-4 (Estrutura do Repositório + Banco de Dados)
> em blocos únicos, por terem sido executados em conjunto — mas os 10
> passos do roadmap original (Arquitetura → Modelagem → Estrutura do
> Repositório → Banco de Dados → Backend → ETL → Engenharia de Dados → ML
> → BI → Melhorias) continuam sendo a referência oficial de fases do
> projeto. Nenhum passo foi pulado.

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
  desenvolvimento de dado capturado pelos sistemas reais (FastAPI, Pinpad,
  Totem, Telemarketing, Scraper).
- **ADR 004** — Nova origem de avaliação `Telemarketing - Pesquisa
  Pós-Atendimento` (IVR pós-ligação): cliente e categoria conhecidos, sem
  comentário (só o dígito da nota).
- **ADR 005** — Inicialmente propunha `psycopg2-binary` para scripts locais;
  **revertido no mesmo dia** após falha real de instalação no Windows
  (exigia compilação + `pg_config`, ausente no sistema). Decisão final:
  `pg8000` (Python puro, sem compilação) em todo o projeto — local e
  Databricks, um único driver.
- **ADR 006** — FastAPI (não Flask) como framework de backend da Fase 5,
  para cadastro de avaliações (Formulário Web), Pinpad/Totem (rota
  dedicada, não Streamlit standalone) e integração Telemarketing. Motivos:
  validação nativa via Pydantic, documentação automática (OpenAPI/Swagger)
  e maior demanda de mercado — sem perda funcional para o escopo do
  projeto.

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
  GitHub Actions fica para uma fase futura (10 — Melhorias), se necessário.
- **Confirmado:** a rede corporativa do autor bloqueia ativamente a porta
  5432 (Postgres) para conexões de saída — testado com `Test-NetConnection`
  (`TcpTestSucceeded: False`), não é problema de driver/script. GitHub
  Codespaces deixa de ser "opção principal" e passa a ser **necessário**
  para qualquer script que precise de conexão direta ao banco a partir da
  máquina de trabalho.
- Confirmado (2026-07-24): com a Data API desabilitada, o Supabase não
  desliga o PostgREST internamente — ele passa a usar um schema sentinela
  inexistente (`pg_pgrst_no_exposed_schemas`), gerando o erro `schema
  "pg_pgrst_no_exposed_schemas" does not exist` nos logs. Confirmado pela
  [documentação oficial de troubleshooting do
  Supabase](https://supabase.com/docs/guides/troubleshooting/schema-pg_pgrst_no_exposed_schemas-does-not-exist):
  é comportamento esperado, não afeta o projeto (não interfere na conexão
  direta via `pg8000`, que não passa pelo PostgREST) — apenas ruído nos
  logs. Nenhuma ação necessária.

## Fases 1-2 — Arquitetura e Modelagem de Dados (Concluída)

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

## Fases 3-4 — Estrutura do Repositório e Banco de Dados (Concluída)

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
- [x] **Bug corrigido:** primeira execução via Codespaces completou sem
  erro aparente (todos os inserts e contagens corretas), mas faltava
  `conn.commit()` explícito — `pg8000` tem `autocommit=False` por padrão e
  `close()` não comita a transação, então os dados provavelmente não foram
  persistidos de fato. Corrigido: commit explícito ao final, rollback em
  caso de exceção, conexão fechada uma única vez (antes havia fechamento
  duplicado, causando o erro `connection is closed` no final da execução).
  Necessário reexecutar o script para confirmar a carga real dos dados.
- [x] Rodar o script corrigido via GitHub Codespaces e validar (via
  `SELECT COUNT(*)`) que os dados foram realmente persistidos —
  **confirmado em 2026-07-24: 500 clientes e 5.000 avaliações**, números
  batendo exatamente com o esperado. Fases 3-4 (Estrutura do Repositório e
  Banco de Dados) concluídas.
- [x] **Bugs de realismo corrigidos** (revisão manual dos dados gerados):
  - `email` não tinha nenhuma relação com `nome` (Faker gerava os dois de
    forma independente) — corrigido: e-mail agora derivado do nome
    (acentos removidos, títulos como "Dr./Dra." filtrados)
  - `telefone` vinha com formatos inconsistentes (`fake.phone_number()`
    misturava com/sem DDD, com/sem código de país) — corrigido: sempre
    `(DDD) 9XXXX-XXXX`, com DDD sorteado de uma lista de DDDs reais do Brasil
  - `id_cliente` começando em 1001 em vez de 1: **não é bug** — sequências
    do Postgres não são revertidas por rollback; execuções anteriores (antes
    da correção do `commit()`) consumiram IDs mesmo tendo sido descartadas.
    Documentado o comando para reset limpo (`TRUNCATE ... RESTART IDENTITY`)
    se desejado.
  - `id_cidade` com `NULL`: comportamento esperado (~30% dos clientes,
    simulando CEP não resolvido — ver ADR-002)
  - `criado_em` exibido em UTC: comportamento correto de `TIMESTAMPTZ`
    (armazena em UTC por padrão; conversão para horário local é
    responsabilidade da camada de consumo — documentado em
    `data_model_relational.md`)
- [x] Definição da tecnologia de interface do Pinpad/Totem: **rota
  dedicada no mesmo FastAPI** (não Streamlit standalone) — ver ADR-006

## Riscos monitorados

| Risco | Status |
|---|---|
| Databricks Free Edition bloquear acesso externo ao Supabase | **Descartado** — conectividade confirmada na PoC |
| `psycopg2` incompatível com serverless do Databricks | **Identificado e mitigado** — ver ADR 001 |
| Supabase free tier sem backup automático | Monitorado — mitigação via scripts de schema versionados no Git |
| Scraping de fontes como Reclame Aqui (ToS) | Ainda não avaliado — a validar na Fase de Ingestão |
| Rede corporativa bloqueia porta 5432 (Postgres) para conexões locais | **Confirmado e mitigado** — uso de GitHub Codespaces para qualquer script com conexão direta ao banco |

## Próximos passos (Fase 5 — Backend)

- [x] Framework de backend definido: **FastAPI** (não Flask) — ver ADR-006
- [x] Tecnologia da interface Pinpad/Totem definida: rota dedicada no mesmo
  FastAPI (não Streamlit standalone) — ver ADR-006
- [x] Escopo do Formulário Web definido: **apenas Create** (cadastro de
  avaliação), sem tela administrativa de edição/exclusão — confirmado
  explicitamente pelo autor
- [x] Deploy definido: apenas local/GitHub Codespaces por ora, sem
  publicação em free tier nesta fase
- [x] Cadastro (Create) via FastAPI para avaliações (Formulário Web)
- [x] Módulos de backend implementados: `src/database/connection.py`,
  `src/validators/cliente.py`, `src/crud/avaliacoes.py`, `src/schemas/`
  (4 schemas Pydantic, um por origem), `src/api/` (4 routers + `main.py`)
- [x] Correção: Pinpad **não** usa mapeamento fixo de guichê→categoria —
  é atendimento presencial único em caixa, o operador seleciona a
  categoria diretamente (mesmo mecanismo do Formulário Web). `config/
  settings.py` (guichê) foi removido; `data_model_relational.md` corrigido.
- [x] Correção: telefone normalizado para **somente dígitos** (DDD+número,
  sem parênteses/traço) — mesmo padrão do CPF, tanto no schema Pydantic
  (`validators/cliente.py::telefone_normalizado`) quanto no gerador do
  seed sintético (`generate_seed_dev.py::gerar_telefone()`); dados já
  seedados precisam de UPDATE de normalização (ver AI_USAGE.md).
- [x] Correção: Telemarketing devolvia erro `500` cru (violação de FK do
  Postgres) quando `id_cliente`/`id_categoria` inexistentes eram enviados
  — teste confirmou. Adicionado `verificar_cliente_existe`/
  `verificar_categoria_existe` em `crud/avaliacoes.py`, chamados antes do
  insert no `router_telemarketing.py`; agora devolve `422` legível, igual
  aos demais routers.
- [ ] Templates HTML (Jinja2) para Formulário Web, Pinpad e Totem — rotas
  já existem, faltam as telas
- [ ] Interface de Pinpad/Totem, com seleção de modo
- [ ] Integração com sistema de Telemarketing (pesquisa pós-atendimento)

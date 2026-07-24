# Modelo Relacional — Customer Insight Platform

**Fase:** 1 — Modelagem de Dados
**Status:** Aprovado
**Localização:** PostgreSQL (Supabase) — Banco Operacional (OLTP)

## Objetivo

Modelar o banco operacional responsável por armazenar os dados brutos gerados
pelas fontes do projeto (cadastro via FastAPI, pinpad de atendente, totem de
autoatendimento, resultado do scraping, dados enriquecidos via API), com
integridade referencial completa. Este banco **não** é a camada Bronze — ver
justificativa em [`architecture.md`](architecture.md).

Cada origem entrega um subconjunto diferente de campos preenchidos — o
modelo precisa suportar isso sem criar uma tabela por origem (ver seção
["Preenchimento por origem"](#preenchimento-por-origem-avaliacoes)).

Modelo normalizado (3NF), priorizando integridade transacional. A
desnormalização proposital para performance de leitura acontece apenas no
modelo dimensional da camada Gold (ver
[`data_model_dimensional.md`](data_model_dimensional.md)).

## Diagrama (relacionamentos)

```
estados (1) ──< (N) cidades (1) ──< (N) clientes (1) ──o< (N) avaliacoes
                                                              │
                                          categorias (1) ──o< (N)
                                                              │
                                    origens_avaliacao (1) ───< (N)
```
`──o<` indica relacionamento opcional (FK nullable); `───<` indica
relacionamento obrigatório.

## Tabelas

### `estados`

| Coluna     | Tipo         | Regra                          |
|------------|--------------|---------------------------------|
| id_estado  | SMALLINT     | PK, identity                    |
| sigla      | CHAR(2)      | NOT NULL, UNIQUE (ex: "SP")      |
| nome       | VARCHAR(50)  | NOT NULL                        |

Tabela de apoio, baixa cardinalidade (27 linhas). Existe separada de
`cidades` para evitar repetição do nome do estado em cada cidade e permitir
agrupamento direto por UF sem depender de texto.

### `cidades`

| Coluna     | Tipo          | Regra                                  |
|------------|---------------|------------------------------------------|
| id_cidade  | INTEGER       | PK, identity                             |
| nome       | VARCHAR(100)  | NOT NULL                                 |
| id_estado  | SMALLINT      | NOT NULL, FK -> estados                  |
|            |               | UNIQUE (nome, id_estado)                 |

`UNIQUE (nome, id_estado)` evita duplicar a mesma cidade dentro do mesmo
estado (ex.: duas linhas para "São José" em SC), mas permite nomes iguais em
estados diferentes.

### `categorias`

| Coluna       | Tipo         | Regra              |
|--------------|--------------|---------------------|
| id_categoria | INTEGER      | PK, identity        |
| nome         | VARCHAR(60)  | NOT NULL, UNIQUE     |

Categoria do atendimento avaliado (ex.: "Suporte Técnico", "Financeiro",
"Entrega"). Lista fechada, cadastro simples.

### `origens_avaliacao`

| Coluna     | Tipo         | Regra              |
|------------|--------------|---------------------|
| id_origem  | INTEGER      | PK, identity        |
| nome       | VARCHAR(60)  | NOT NULL, UNIQUE     |

Canal de onde a avaliação veio. Separada de `categorias` porque representa
uma dimensão de negócio diferente (canal de captura vs. assunto avaliado) —
misturar as duas impediria analisar, por exemplo, "nota média por origem"
sem contaminar com categoria.

Linhas (seed inicial):

| nome                      | Descrição                                                        |
|---------------------------|-------------------------------------------------------------------|
| `Formulário Web`          | Cadastro via sistema FastAPI — dado mais completo                  |
| `Pinpad - Atendente`      | Nota registrada pelo atendente ao final de um atendimento           |
| `Totem - Autoatendimento` | Nota registrada pelo próprio cliente, sem amarração a atendimento   |
| `Scraping`                | Avaliação pública coletada de sites de review                      |
| `Telemarketing - Pesquisa Pós-Atendimento` | Pesquisa por IVR ao final de uma ligação (ver [ADR 004](decisions/004-origem-telemarketing.md)) |

`id_origem` é a única FK de `avaliacoes` que é **sempre** `NOT NULL` —
independente da origem, o processo que grava o registro sempre sabe de onde
o dado veio.

### `clientes`

| Coluna     | Tipo          | Regra                                            |
|------------|---------------|----------------------------------------------------|
| id_cliente | INTEGER       | PK, identity                                        |
| nome       | VARCHAR(150)  | NOT NULL                                            |
| cpf        | CHAR(11)      | UNIQUE, apenas dígitos (sem máscara)                 |
| email      | VARCHAR(150)  | opcional                                            |
| telefone   | VARCHAR(20)   | opcional                                            |
| id_cidade  | INTEGER       | **opcional**, FK -> cidades                          |
| natureza_registro | VARCHAR(20) | NOT NULL, default `'Real'`, CHECK IN ('Sintético','Real') |
| criado_em  | TIMESTAMPTZ   | NOT NULL, default now()                             |

Decisões confirmadas na Fase 2 (Modelagem de Dados):

- **`id_cidade` opcional:** cliente pode ser cadastrado sem CEP/cidade
  resolvida no momento da avaliação; o dado é completado posteriormente via
  API ViaCEP (enriquecimento), não bloqueia a gravação inicial.
- **CPF sem máscara, validação fora do banco:** dígito verificador é regra de
  negócio complexa demais para `CHECK` — fica no `validators/` da aplicação.
  O banco garante apenas unicidade e formato de tamanho (`CHAR(11)`).
- **Pool fixo de clientes recorrentes:** conforme `status.md`, a ingestão de
  dados fictícios deve reaproveitar um pool de clientes (200–500) em vez de
  criar um cliente novo por avaliação — preserva `id_cliente` como chave
  estável para histórico e detecção de recorrência.
- **`natureza_registro` (Fase 4 — Banco de Dados, ver [ADR 003](decisions/003-natureza-registro-sintetico-real.md)):**
  distingue dado gerado pelo seed de desenvolvimento (`'Sintético'`) de dado
  capturado pelos sistemas reais — FastAPI, Pinpad, Totem, Scraper
  (`'Real'`, default). Necessário porque os dois tipos de registro coexistem
  na mesma tabela ao longo do desenvolvimento.

### `avaliacoes`

| Coluna         | Tipo        | Regra                                     |
|----------------|-------------|----------------------------------------------|
| id_avaliacao   | BIGINT      | PK, identity                                  |
| id_cliente     | INTEGER     | **opcional**, FK -> clientes                  |
| id_categoria   | INTEGER     | **opcional**, FK -> categorias                |
| id_origem      | INTEGER     | NOT NULL, FK -> origens_avaliacao             |
| data_avaliacao | DATE        | NOT NULL                                      |
| nota           | SMALLINT    | NOT NULL, CHECK (nota BETWEEN 1 AND 5)         |
| comentario     | TEXT        | opcional                                      |
| natureza_registro | VARCHAR(20) | NOT NULL, default `'Real'`, CHECK IN ('Sintético','Real') |
| criado_em      | TIMESTAMPTZ | NOT NULL, default now()                       |

Decisões confirmadas na Fase 2 (Modelagem de Dados):

- **Escala de nota fixa em 1–5**, garantida por `CHECK` no banco (não só na
  aplicação) — é a regra mais barata de impor na origem e evita dado inválido
  entrar mesmo por uma via de ingestão futura que pule a validação do
  FastAPI (ex.: script de carga direto). É o único campo garantido em
  **todas** as origens, inclusive pinpad e totem.
- **`id_cliente` e `id_categoria` opcionais (`NULL`, não sentinela):** cada
  origem entrega um subconjunto diferente de campos, por natureza da fonte —
  não é dado faltando por falha, é a fonte que estruturalmente não produz
  aquele dado (ver [Preenchimento por origem](#preenchimento-por-origem-avaliacoes)
  abaixo). Optou-se por `NULL` real em vez de um registro sentinela
  ("Cliente Não Identificado") no operacional porque `NULL` comunica
  corretamente "esse dado não existe para essa origem", sem inventar um
  valor. O *unknown member* (sentinela) é resolvido depois, na camada Gold
  (`dim_cliente`/`dim_categoria`), que é o lugar certo para essa decisão de
  modelagem dimensional.
- **`comentario` opcional:** apenas `Formulário Web` e `Scraping` trazem
  texto livre; pinpad, totem e telemarketing (IVR) não têm campo de
  comentário.
- **Sem constraint de deduplicação:** deduplicação de avaliações é
  responsabilidade da camada Silver (Databricks), não do Postgres — evita
  lógica de negócio duplicada em duas camadas e mantém o operacional como
  ingestão fiel da origem.
- **`natureza_registro` (Fase 4 — Banco de Dados, ver [ADR 003](decisions/003-natureza-registro-sintetico-real.md)):**
  distingue dado gerado pelo seed de desenvolvimento (`'Sintético'`) de dado
  capturado pelos sistemas reais — FastAPI, Pinpad, Totem, Scraper, Telemarketing
  (`'Real'`, default). Ortogonal a `id_origem`: uma avaliação de `Scraping`
  pode ser `Sintético` hoje (seed) e `Real` quando o scraper de fato rodar.

### Preenchimento por origem (`avaliacoes`)

| Origem                    | id_cliente | id_categoria | comentario | nota        |
|----------------------------|:----------:|:------------:|:----------:|:-----------:|
| `Formulário Web`           | conhecido  | conhecida    | opcional   | obrigatória |
| `Pinpad - Atendente`       | `NULL`     | **conhecida** (selecionada pelo operador no atendimento presencial em caixa) | `NULL` | obrigatória |
| `Totem - Autoatendimento`  | `NULL`     | `NULL` (sem amarração a local ou atendimento) | `NULL` | obrigatória |
| `Scraping`                 | `NULL`     | `NULL`       | conhecido  | obrigatória |
| `Telemarketing - Pesquisa Pós-Atendimento` | conhecido | conhecida | `NULL` (IVR só captura o dígito) | obrigatória |

Consequência analítica: métricas como "nota média por cliente" ou "clientes
recorrentemente insatisfeitos" existem para `Formulário Web` **e**
`Telemarketing` (ver [ADR 004](decisions/004-origem-telemarketing.md)) — as
duas únicas origens com `id_cliente` conhecido. Para as demais origens, a
análise possível é "nota (+ sentimento, quando houver texto) por
origem/categoria/período" — o que é coerente com o que cada fonte realmente
oferece, e não uma limitação a corrigir.

**Fora de escopo, decisão consciente:** não há `id_funcionario` em
`avaliacoes` nesta fase, mesmo o pinpad sendo operado por um atendente. Essa
FK só entra quando a entidade `Funcionários` for modelada (fase futura do
roadmap) — adicionar a coluna antes disso criaria dependência de uma
entidade ainda não definida. É uma mudança de baixo risco no futuro
(`ALTER TABLE avaliacoes ADD COLUMN id_funcionario ...`, nullable, não
quebra dado existente).

## Índices

```sql
CREATE INDEX idx_avaliacoes_cliente   ON avaliacoes(id_cliente);
CREATE INDEX idx_avaliacoes_categoria ON avaliacoes(id_categoria);
CREATE INDEX idx_avaliacoes_data      ON avaliacoes(data_avaliacao);
CREATE INDEX idx_clientes_cidade      ON clientes(id_cidade);
```

Justificativa: colunas usadas em FK e em filtros/joins mais prováveis
(consulta por cliente, por categoria, série temporal por data, e ingestão
Bronze filtrando por cidade). Não há índice em `comentario` (TEXT, não é
usado em filtro direto) nem em colunas de baixa seletividade como `nota`
(CHECK de 1 a 5 não justifica índice — scan filtrado é barato o suficiente
no volume esperado).

## Fuso horário de `criado_em`

`TIMESTAMPTZ` armazena o instante internamente em UTC — isso é proposital e
é boa prática (elimina ambiguidade de fuso na gravação). Ao consultar via
SQL Editor ou qualquer cliente sem `TimeZone` configurado, o valor aparece
em UTC, não em horário de Brasília (UTC-3) — isso é comportamento esperado
do tipo, não um dado incorreto. Para exibir no horário local:

```sql
SELECT criado_em AT TIME ZONE 'America/Sao_Paulo' FROM clientes;
```

Ferramentas de consumo (Power BI, relatórios) devem aplicar essa conversão
na camada de apresentação, não o banco.

## Fora de escopo na Fase 2 (Modelagem de Dados)

`funcionarios`, `departamentos`, `chamados` e SLA entram apenas quando a fase
correspondente do roadmap (ver `README.md`) for iniciada, reaproveitando esta
mesma arquitetura de banco operacional.

## Rastreabilidade

Script de criação correspondente:
[`src/database/scripts/schema.sql`](../src/database/scripts/schema.sql).

Modelo dimensional (Gold) derivado deste modelo:
[`data_model_dimensional.md`](data_model_dimensional.md).

Decisão de FKs opcionais em `avaliacoes` (motivo, alternativas descartadas):
[ADR 002](decisions/002-fks-opcionais-avaliacoes-multiplas-origens.md).

Decisão de rastreabilidade dado sintético vs. real (`natureza_registro`):
[ADR 003](decisions/003-natureza-registro-sintetico-real.md).

Decisão da 5ª origem de avaliação (Telemarketing):
[ADR 004](decisions/004-origem-telemarketing.md).

Driver PostgreSQL usado pelos scripts de carga (`pg8000`):
[ADR 005](decisions/005-driver-postgres-scripts-locais.md).

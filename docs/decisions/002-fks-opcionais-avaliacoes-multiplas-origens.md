# ADR 002 — FKs opcionais em `avaliacoes` para suportar múltiplas origens

**Status:** Aceito
**Data:** 2026-07-23
**Fase:** 2 — Modelagem de Dados

## Contexto

O projeto definiu 4 origens de captura de avaliação, cada uma entregando um
subconjunto diferente de campos, por natureza estrutural da fonte — não por
falha de captura:

| Origem                    | Cliente identificado | Categoria conhecida | Comentário |
|----------------------------|:---------------------:|:--------------------:|:----------:|
| Formulário Web (Flask)      | sim                    | sim                   | opcional    |
| Pinpad - Atendente            | não                    | sim (fixa por atendimento) | não   |
| Totem - Autoatendimento       | não                    | não                   | não        |
| Web Scraping                  | não                    | não                   | sim        |

O modelo relacional original (Fase 1, primeira versão) definia `id_cliente` e
`id_categoria` como `NOT NULL` em `avaliacoes`, assumindo que toda avaliação
nasceria de um cadastro completo via Flask. Isso deixou de ser válido ao
incluir Pinpad, Totem e Scraping como origens de primeira classe.

## Decisão

`id_cliente` e `id_categoria` em `avaliacoes` passam a ser **colunas
opcionais** (FK nullable), com o valor `NULL` representando "esta origem não
produz este dado" — não um valor desconhecido a ser preenchido depois.

`id_origem` permanece `NOT NULL`: independente da origem, o processo que
grava o registro sempre sabe de onde o dado veio.

O tratamento de "membro desconhecido" (linha "Não Identificado" em
`dim_cliente`/`dim_categoria`, para evitar `(Blank)` no Power BI) fica
delegado à camada Gold (Databricks), não ao banco operacional.

## Alternativas consideradas

| Alternativa | Motivo de descarte |
|---|---|
| Registro-sentinela no Postgres (ex.: cliente `id=0` "Não Identificado", categoria `id=0` "Não Identificada"), mantendo `NOT NULL` | Mistura semânticas diferentes: um cliente cadastrado sem cidade resolvida (caso real, já tratado como FK opcional em `clientes.id_cidade`) não é a mesma coisa que uma avaliação de scraping sem nenhum cliente associado. Forçar um valor artificial no operacional esconde essa distinção dentro do próprio dado, em vez de comunicá-la. |
| Criar uma tabela `avaliacoes` por origem (ex.: `avaliacoes_scraping`, `avaliacoes_pinpad`) | Duplica schema e lógica de ETL/BI por origem; qualquer métrica cross-origem (ex. "nota geral por período") exigiria `UNION` manual em vez de uma única tabela fato. Vai contra o objetivo de arquitetura evolutiva sem reestruturação. |
| Cliente "fraco" (linha em `clientes` sem CPF, só com identificador textual do scraping/pinpad) | Descartada nesta fase porque nenhuma das origens sem cliente (Pinpad, Totem, Scraping) fornece qualquer identificador do autor — não há dado para popular esse registro fraco. Fica em aberto para reavaliação se uma origem futura trouxer algum identificador parcial (ex. nickname). |

## Consequências

- **Postgres (operacional):** `id_cliente` e `id_categoria` em `avaliacoes`
  passam a aceitar `NULL`. Índices existentes (`idx_avaliacoes_cliente`,
  `idx_avaliacoes_categoria`) continuam válidos — B-tree do Postgres não
  indexa `NULL`s por padrão, sem impacto de performance.
- **Databricks Gold:** `dim_cliente` e `dim_categoria` precisam implementar
  *unknown member* (surrogate key reservada, ex. `-1`, nome "Não
  Identificado"), mapeando todo `NULL` do operacional. Toda medida DAX que
  agrupar por cliente/categoria passa a exibir essa linha em vez de
  `(Blank)`.
- **Análise de negócio:** métricas como "nota média por cliente" ou
  "clientes recorrentemente insatisfeitos" só são possíveis para avaliações
  vindas do Formulário Web. Para as demais origens, a granularidade máxima é
  origem/categoria (quando houver)/período — limitação real da fonte, não do
  modelo.
- **`id_funcionario` explicitamente fora de escopo:** o Pinpad de atendente
  sugeriria rastrear qual funcionário atendeu, mas essa FK não foi
  adicionada agora — depende da entidade `Funcionários`, ainda não modelada
  (fase futura do roadmap). Adição futura é aditiva e de baixo risco
  (`ALTER TABLE avaliacoes ADD COLUMN id_funcionario ...`, nullable, não
  quebra dado existente).
- Documentado para não ser re-descoberto por tentativa e erro ao construir o
  ETL Silver → Gold ou o dashboard Power BI.

# Modelo Dimensional — Customer Insight Platform

**Fase:** 1 — Modelagem de Dados
**Status:** Rascunho aprovado (materialização real na Fase de Engenharia de Dados)
**Localização:** Databricks — camada Gold

## Estratégia: Modelo Estrela (Star Schema)

Uma tabela fato central, cercada por dimensões **desnormalizadas** (achatadas).
Diferente do modelo relacional (Postgres, 3NF), aqui o objetivo não é
integridade transacional, é **performance de leitura e simplicidade para o
Power BI** — menos joins significa DAX mais simples e mais rápido.

## Fato: `fato_avaliacoes`

```
fato_avaliacoes
├── sk_avaliacao          PK (surrogate key)
├── sk_cliente            FK -> dim_cliente
├── sk_categoria          FK -> dim_categoria
├── sk_origem             FK -> dim_origem
├── data_avaliacao        date               -- relaciona com a tabela calendário do Power BI
├── nota                  smallint           -- medida
├── sentimento            varchar            -- "Positivo"/"Negativo"/"Neutro" (gerado no Silver, via ML)
├── confianca_sentimento  decimal            -- score do modelo de ML
└── natureza_registro     varchar            -- "Sintético"/"Real" (ver ADR-003)
```

**`sentimento` e `confianca_sentimento` são nulos para a maioria das
origens.** A análise de sentimento depende de texto livre, que só existe em
`Formulário Web` (opcional) e `Scraping` (sempre) — `Pinpad`, `Totem` e
`Telemarketing` não capturam comentário (ver tabela de preenchimento por
origem em [`data_model_relational.md`](data_model_relational.md)). Medidas
DAX de sentimento devem, portanto, filtrar por origem ou tratar o nulo
explicitamente, em vez de assumir cobertura total da base.

**Comentário (texto) fica fora do Gold.** Texto livre não é medida analítica e
infla o modelo sem necessidade — Power BI não precisa carregar o texto de cada
avaliação para gerar KPI, gráfico ou card. O comentário permanece disponível
na camada Silver, caso seja necessário um relatório de drill-through pontual
no futuro.

**`natureza_registro` fica como atributo direto do fato, não como dimensão
separada.** Cardinalidade de 2 valores (`Sintético`/`Real`, ver
[ADR 003](decisions/003-natureza-registro-sintetico-real.md)) não justifica
uma `dim_natureza_dado` — mesmo raciocínio já aplicado a não criar dimensão
para `sentimento`. Serve como slicer no Power BI para alternar entre "ver
tudo", "só dado real" ou "só dado de demonstração" (útil tanto durante o
desenvolvimento do projeto quanto para deixar explícito, na apresentação do
portfólio, o que é simulação).

## Dimensões

```
dim_cliente
├── sk_cliente        PK (surrogate key)
├── id_cliente         natural key (do Postgres)
├── nome
├── cidade             -- achatado, sem necessidade de dimensão de localidade separada
└── estado

dim_categoria
├── sk_categoria       PK
├── id_categoria        natural key
└── nome

dim_origem
├── sk_origem          PK
├── id_origem           natural key
└── nome
```

### Por que achatar cidade/estado dentro de `dim_cliente`

No Postgres, Cidade e Estado são tabelas separadas (3NF, para não duplicar
dado e manter integridade). No Gold, essa separação não traz benefício — só
forçaria o Power BI a fazer join entre múltiplas tabelas para responder algo
simples como "quantas avaliações por estado?". Achatar em `dim_cliente`
resolve isso com uma única dimensão.

## Calendário: sem dimensão de tempo materializada no Gold

Decisão: **não** materializar uma `dim_tempo` no Databricks. A tabela
calendário será criada diretamente no Power BI via DAX:

```dax
Calendario = CALENDAR(MIN(fato_avaliacoes[data_avaliacao]), MAX(fato_avaliacoes[data_avaliacao]))
```

com colunas calculadas de mês/trimestre/ano, marcada como **tabela de datas**,
relacionada 1-para-muitos com `fato_avaliacoes[data_avaliacao]`.

Justificativa: apenas o Power BI consome o Gold, e não há regra de calendário
especial (ano fiscal diferente, feriados customizados). Nesse cenário, a
tabela calendário nativa do Power BI é mais simples e evita um job de ETL
extra no Databricks sem ganho real. Se no futuro múltiplas ferramentas
passarem a consumir o mesmo Gold e precisarem da mesma definição de
calendário, essa decisão é revisitada.

## Tratamento de mudanças de atributo (SCD)

Modelo usa **SCD Tipo 1** (sobrescreve o valor antigo, sem manter histórico)
— por exemplo, se um cliente mudar de cidade, o registro em `dim_cliente` é
atualizado, sem preservar o valor anterior. Suficiente para o escopo atual.

Se no futuro for necessário analisar "onde o cliente estava quando fez a
avaliação" (histórico real de atributos), evolui-se para **SCD Tipo 2** (nova
linha a cada mudança, com data de validade). Não implementado agora para
evitar complexidade desnecessária frente ao volume e propósito do MVP.

## Próximos passos

- Materialização real das tabelas (Delta Tables) na Fase de Engenharia de
  Dados, via ETL Silver → Gold
- Criação da tabela calendário e relacionamentos no Power BI, na Fase de
  Business Intelligence

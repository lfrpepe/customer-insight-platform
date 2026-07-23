# ADR 003 — Rastreabilidade de dado sintético vs. real (`natureza_registro`)

**Status:** Aceito
**Data:** 2026-07-23
**Fase:** 2 — Estrutura do Repositório / Banco de Dados

## Contexto

O projeto precisa existir e ser demonstrável antes de os sistemas reais de
captura (Flask, Pinpad, Totem, Scraper) estarem prontos — por isso a Fase 2
inclui um seed de dados de desenvolvimento (`generate_seed_dev.py`, Faker),
com 500 clientes fictícios e 5.000 avaliações distribuídas entre as 4
origens.

Sem alguma marca no próprio dado, não há como diferenciar depois — no banco,
no ETL ou no dashboard — o que é dado fictício de povoamento do que será
dado real, capturado pelos sistemas depois de implementados. Isso é
particularmente importante porque ambos podem coexistir na mesma tabela ao
longo do desenvolvimento (seed continua servindo de base de volume enquanto
os sistemas reais começam a gravar registros novos).

## Decisão

Adicionar a coluna `natureza_registro` em `clientes` e `avaliacoes`, com
dois valores possíveis:

| Valor        | Significado                                                          |
|--------------|------------------------------------------------------------------------|
| `Sintético`  | Dado gerado artificialmente (seed de desenvolvimento, Faker)           |
| `Real`       | Dado capturado pelos sistemas de produção (Flask, Pinpad, Totem, Scraper) |

```sql
natureza_registro VARCHAR(20) NOT NULL DEFAULT 'Real'
    CHECK (natureza_registro IN ('Sintético', 'Real'))
```

`DEFAULT 'Real'` é proposital: os sistemas que ainda serão construídos (Fase
5 em diante) não precisam saber dessa coluna para inserir corretamente — o
default já assume produção. Só o script de seed precisa declarar
explicitamente `'Sintético'` em cada `INSERT`.

Não é aplicado em `estados`, `cidades`, `categorias` ou `origens_avaliacao`:
são tabelas de catálogo/referência (verdade de negócio fixa), não instâncias
de dado gerado — a distinção sintético/real só faz sentido para registros
que representam fatos do mundo (cliente, avaliação), não para o vocabulário
de apoio.

## Alternativas consideradas

| Alternativa | Motivo de descarte |
|---|---|
| Coluna booleana (`eh_sintetico BOOLEAN`) | Mais simples de validar, mas menos legível em dashboards Power BI (segmentação "Sintético/Real" como texto é mais direta que `TRUE/FALSE` numa slicer) e menos extensível caso surja um terceiro estado no futuro (ex.: "Homologação"). |
| Nome `origem_dado` ou `tipo_origem` | Colide conceitualmente com `id_origem`/`origens_avaliacao`, que já representa o canal de captura (Web, Pinpad, Totem, Scraping). Usar um nome parecido para um conceito diferente (sintético vs. real) geraria ambiguidade em queries e documentação. |
| Tabela separada de "lotes de carga" (`lotes_importacao`, com FK em cada registro) | Overengineering para o escopo atual — o objetivo é apenas marcar a natureza do dado, não seu histórico de execução de carga (isso poderia ser relevante numa fase futura de auditoria de ETL, mas não agora). |
| Aplicar em todas as tabelas, incluindo catálogos | Catálogos (`categorias`, `origens_avaliacao`, `estados`, `cidades`) não são "gerados por simulação" no mesmo sentido — são vocabulário fixo de negócio, sempre real, independente da fase do projeto. |

## Consequências

- **Schema (`schema.sql`):** `clientes` e `avaliacoes` ganham a coluna
  `natureza_registro`, com `CHECK` e `DEFAULT 'Real'`.
- **Seed (`generate_seed_dev.py` / `seed_dev.sql`):** todo `INSERT` gerado
  passa a declarar `'Sintético'` explicitamente.
- **Databricks Bronze/Silver:** nenhuma mudança de responsabilidade — o
  Bronze continua ingerindo tudo sem filtro; a decisão de excluir dado
  sintético de análises "reais" fica para o Silver/Gold (ver seção
  correspondente em `data_model_dimensional.md`).
- **Gold/Power BI:** `fato_avaliacoes` carrega `natureza_registro` como
  atributo direto (não como dimensão separada — cardinalidade de 2 valores
  não justifica uma `dim_natureza_dado`). Dashboards podem usar como slicer
  para alternar entre "ver tudo", "só dado real" ou "só dado de demonstração"
  — útil tanto durante o desenvolvimento quanto para deixar claro, ao
  apresentar o portfólio, o que é simulação e o que seria produção real.
- **Baixa cardinalidade, sem índice dedicado:** 2 valores possíveis não
  justificam índice — mesmo raciocínio já aplicado a `nota` no modelo
  relacional.
- Documentado para que a distinção não seja perdida quando os sistemas reais
  (Flask, Pinpad, Totem, Scraper) começarem a gravar dado ao lado do seed já
  existente.

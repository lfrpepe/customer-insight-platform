# ADR 012 — Campos adicionais do site de avaliações simulado não são extraídos pelo scraper

**Status:** Aceito
**Data:** 2026-07-28
**Fase:** 6 — ETL / Fontes de Dados (Scraping)

## Contexto

O site de avaliações fixture (ADR-010, ADR-011) evoluiu, a pedido do
autor, para incluir elementos além de nota e comentário: reações
(útil/não útil, com toggle via JS), um indicador de "respondido pela
empresa" (~85% das avaliações) e, apenas quando respondido, os campos
"problema resolvido" e "voltaria a fazer negócio" (correlacionados com a
nota). Esses elementos foram adicionados por dois motivos explícitos do
autor: tornar o site mais realista/moderno, e dificultar a extração e a
análise de sentimento de propósito (ruído estrutural).

O schema atual de `avaliacoes` (ver [ADR
002](002-fks-opcionais-avaliacoes-multiplas-origens.md) e
`data_model_relational.md`) só contempla `id_cliente`, `id_categoria`,
`id_origem`, `data_avaliacao`, `nota`, `comentario` e
`natureza_registro` — não há coluna para reações, resposta da empresa,
resolvido ou voltaria. Sem uma decisão explícita, ficaria ambíguo se o
scraper deveria tentar capturar esses campos extras de alguma forma (ex.:
concatenados no comentário, ou descartados silenciosamente).

## Decisão

O scraper (`parser.py`/`tratamento.py`) extrai **apenas nota e
comentário** — os únicos campos que a origem `Scraping` efetivamente
popula em `avaliacoes` (ver tabela "Preenchimento por origem" em
`data_model_relational.md`). Os demais elementos do site (reações,
respondido, resolvido, voltaria) são tratados como **ruído estrutural a
ignorar**, não como dado a capturar — coerente com o propósito original
desses elementos, que foi justamente dificultar a raspagem e a análise
de sentimento, não enriquecer o modelo de dados.

## Alternativas consideradas

| Alternativa | Motivo de descarte |
|---|---|
| Extrair todos os campos e alterar `schema.sql` para armazená-los | Fora de escopo desta fase — mudaria o modelo relacional (ADR-002) só para acomodar um dado que nenhuma outra origem produz; se isso for útil no futuro (ex.: enriquecimento via análise de resposta da empresa), deve ser uma decisão de modelagem própria, com seu próprio ADR, não um efeito colateral do redesenho visual do fixture. |
| Extrair e descartar em memória, sem persistir | Considerada, mas sem benefício real sobre simplesmente não extrair — adicionaria código morto ao parser (campos lidos e nunca usados). |

## Consequências

- `parser.py` continua extraindo apenas `review_id`, `nota_bruta`,
  `data_bruta` e `comentario_bruto` — sem mudança de escopo em relação à
  versão anterior do site fixture.
- Se no futuro o projeto quiser capturar "resolvido"/"voltaria"/
  "respondido" como enriquecimento (ex.: nova coluna, ou tabela separada
  de metadados de scraping), isso exige uma decisão de modelagem nova,
  não implícita a este ADR.
- Documentado para não gerar confusão futura sobre por que o HTML do
  site fixture tem mais campos do que o banco operacional realmente
  grava.
- Sem impacto em `schema.sql` ou nos ADRs 001-011.

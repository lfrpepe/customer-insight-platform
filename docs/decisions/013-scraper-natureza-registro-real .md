# ADR 013 — `natureza_registro` do scraper revisado para 'Real' (alinhamento com ADR-003)

**Status:** Aceito
**Data:** 2026-07-28
**Fase:** 6 — ETL / Fontes de Dados (Scraping)

## Contexto

O [ADR 003](003-natureza-registro-sintetico-real.md) definiu
`natureza_registro` para distinguir dado gerado pelo seed de
desenvolvimento (`'Sintético'`) de dado capturado pelos sistemas de
produção (`'Real'`), listando explicitamente **"Flask, Pinpad, Totem,
Scraper"** como os sistemas que produzem dado `'Real'`.

Já o [ADR 010](010-scraping-fonte-simulada.md), ao decidir que o scraper
rodaria contra um site fixture em vez de um site de avaliações real (por
conformidade legal — Termos de Uso + LGPD, não limitação técnica),
registrou que o dado resultante manteria `natureza_registro = 'Sintético'`
"porque a fonte é simulada" — uma afirmação que conflita com a
classificação original do ADR-003.

Na prática, o scraper (`coletor.py`/`parser.py`/`tratamento.py`/
`gravacao.py`) é um sistema de captura real e funcional: faz requisição
HTTP de verdade, faz parsing, valida e grava — igual a Formulário
Web/Pinpad/Totem. O fato de a fonte apontada ser um site simulado (por
decisão de conformidade legal) não muda a natureza do dado capturado —
continua sendo produção real, só que lendo de uma fonte fixture em vez
da internet real.

## Decisão

`gravacao.py` grava `natureza_registro = 'Real'` para toda avaliação
inserida pelo scraper, alinhando com a definição original do ADR-003.
Isso revisa pontualmente o trecho do ADR-010 sobre esse campo — o
restante do ADR-010 (decisão de rodar contra fixture por conformidade
legal) permanece válido e inalterado.

## Alternativas consideradas

| Alternativa | Motivo de descarte |
|---|---|
| Manter `'Sintético'`, como registrado originalmente no ADR-010 | Descartada — contradiz a definição do ADR-003, que já classifica o Scraper como sistema de produção real; misturava dois conceitos diferentes (fonte simulada vs. natureza do dado gerado). |

## Consequências

- `src/scraping/gravacao.py`: `INSERT` passa a gravar `'Real'` em vez de
  `'Sintético'`.
- **ADR-010**: campo "Status" atualizado para apontar esta revisão
  pontual — o corpo do ADR-010 permanece inalterado por completude
  histórica (ADRs aceitos são imutáveis no conteúdo, ver
  `AI_WORKFLOW_RULES.md`).
- Dashboards/slicers de Power BI que filtrarem por `natureza_registro`
  ("só dado de demonstração" vs. "produção real") passam a incluir os
  dados do scraper como `'Real'`, junto com Formulário Web, Pinpad, Totem
  e Telemarketing — só o seed de desenvolvimento (`generate_seed_dev.py`)
  continua marcado como `'Sintético'`.
- Sem impacto em `schema.sql` ou nos ADRs 001-009, 011, 012.
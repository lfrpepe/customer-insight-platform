# ADR 010 — Scraping contra fonte simulada (páginas HTML locais), por conformidade legal

**Status:** Aceito
**Data:** 2026-07-28
**Fase:** 6 — ETL / Fontes de Dados (Scraping)

## Contexto

A visão original do projeto (Fonte 1 — Web Scraping) já prevendo esse risco,
citava explicitamente: coletar avaliações públicas de consumidores (ex.
Reclame Aqui), "sempre respeitando os termos de uso e, se necessário,
substituindo por fontes abertas" ou "páginas HTML locais para demonstração".
`status.md` mantinha esse ponto como risco monitorado, ainda não avaliado:
"Scraping de fontes como Reclame Aqui (ToS) — a validar na Fase de
Ingestão".

Na Fase 6, ao planejar a implementação real do scraper (as origens
`Formulário Web`, `Pinpad`, `Totem` e `Telemarketing` já têm captura real
desde a Fase 5; `Scraping` só existe como dado sintético do seed — ver
ADR-003), essa validação foi feita:

- **Termos de Uso:** sites brasileiros de avaliação de consumidor (ex.
  Reclame Aqui) proíbem explicitamente scraping/coleta automatizada em seus
  Termos de Uso.
- **LGPD:** uma reclamação pública ainda carrega dado pessoal do
  reclamante (nome, cidade, às vezes CPF parcial). A ANPD já se posicionou
  que raspagem de dado pessoal, mesmo publicamente visível, é tratamento
  sujeito à LGPD — exige base legal e observância dos princípios da lei,
  não bastando o dado estar acessível.
- **Risco de exposição:** este repositório é público no GitHub. Um scraper
  funcional contra um site que proíbe expressamente essa prática ficaria
  documentado como evidência de descumprimento de Termos de Uso — risco
  desproporcional para uma peça de portfólio.
- **Fragilidade técnica:** esses sites tipicamente têm proteção anti-bot
  (ex. Cloudflare), tornando o scraper frágil e dependente de fatores fora
  do controle do projeto — ruim para reprodutibilidade por quem for avaliar
  o portfólio.

## Decisão

O scraper é **real** (HTTP request + parsing de HTML com `requests` +
`BeautifulSoup`, tratamento de erro, limpeza de dado) — o que muda é a
**fonte**: em vez de um site de avaliações real, o scraper roda contra um
pequeno conjunto de **páginas HTML estáticas, versionadas no próprio
repositório**, simulando a estrutura de um site de avaliações públicas
(empresa, nota, comentário, data, cidade/estado).

Isso preserva integralmente o objetivo técnico do projeto (demonstrar
scraping de verdade — requisição HTTP, parsing de DOM, extração e limpeza
de dado não estruturado) sem os riscos legais e de reprodutibilidade
listados acima. A limitação **não é técnica, é de conformidade legal** —
isso é documentado explicitamente em `README.md`/`architecture.md` para não
parecer que a etapa foi simplificada por falta de capacidade.

O dado resultante mantém `natureza_registro = 'Sintético'` (mesmo
raciocínio do ADR-003) — a fonte é simulada, ainda que o mecanismo de
coleta seja real.

## Alternativas consideradas

| Alternativa | Motivo de descarte |
|---|---|
| Scraping real contra Reclame Aqui ou site similar | Descartada — proibição explícita nos Termos de Uso, exposição a LGPD (dado pessoal do reclamante), risco reputacional de um repositório público demonstrando descumprimento de ToS, e fragilidade técnica por proteção anti-bot. |
| Usar um dataset público já pronto (ex. Kaggle), sem rodar scraper algum | Descartada — não demonstra a habilidade técnica de scraping em si, que é objetivo explícito do projeto (ver seção "Objetivos" da visão original). |
| API paga de terceiros para reviews (ex. Trustpilot API) | Descartada — contraria o requisito do projeto de usar exclusivamente ferramentas 100% gratuitas. |

## Consequências

- Novo conjunto de páginas HTML estáticas (fixtures) simulando um site de
  avaliações, versionado no repositório (caminho definido na
  implementação, feita em chat dedicado para não misturar assuntos).
- Scraper real (`requests` + `BeautifulSoup`) implementado contra essas
  páginas locais — detalhes de código ficam para essa implementação.
- `README.md`/`architecture.md` precisam declarar explicitamente que a
  fonte de Scraping é simulada por motivo de conformidade legal (ToS +
  LGPD), não por limitação técnica.
- `status.md`: risco "Scraping de fontes como Reclame Aqui (ToS)" passa de
  "ainda não avaliado" para "avaliado e mitigado" (ver este ADR).
- Sem impacto em `schema.sql`, backend (Fase 5) ou nos ADRs 001-009 — é
  uma decisão isolada à origem `Scraping`.

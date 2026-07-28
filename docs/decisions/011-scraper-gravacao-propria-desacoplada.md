# ADR 011 — Scraper com camada de conexão/gravação própria, desacoplada de `crud/avaliacoes.py`

**Status:** Aceito
**Data:** 2026-07-28
**Fase:** 6 — ETL / Fontes de Dados (Scraping)

## Contexto

O ADR-010 definiu que o scraper roda de verdade (HTTP request + parsing
com `requests`/`BeautifulSoup`) contra páginas HTML fixture versionadas no
repositório, por motivo de conformidade legal (ToS + LGPD) — não técnico.

Faltava decidir como o dado coletado chega ao PostgreSQL (Supabase). O
padrão vigente no backend (Fase 5) é um **ponto único de escrita**,
`src/crud/avaliacoes.py`, reaproveitado pelos 4 routers FastAPI (ver
AI_USAGE.md). A dúvida era se o scraper deveria reaproveitar esse mesmo
módulo (import direto, no mesmo processo Python) ou ter sua própria
camada de gravação.

## Decisão

O scraper terá **conexão e gravação totalmente próprias**
(`src/scraping/conexao.py`, `src/scraping/gravacao.py`), sem importar
nenhum código de `src/crud/`, `src/database/` ou qualquer módulo do
backend FastAPI.

Único ponto de reaproveitamento, e não é código da aplicação: o processo
`uvicorn` já em execução serve as páginas fixture via `StaticFiles`, para
que o scraper faça uma requisição HTTP real (não leitura de arquivo local)
— sem isso, o objetivo técnico do ADR-010 (scraping de verdade) não seria
cumprido.

Motivação: simular fielmente um cenário real de scraping corporativo, no
qual o processo de coleta roda como um job independente — muitas vezes em
infraestrutura separada, sem acesso ao codebase da aplicação principal
que expõe a API. Isso é mais representativo do mundo real do que um
scraper que importa a camada de persistência do próprio backend.

Isso quebra conscientemente o padrão de "ponto único de escrita" que vale
para as outras 4 origens (Formulário Web, Pinpad, Totem, Telemarketing) —
é uma exceção documentada, não um esquecimento.

Driver mantido: **`pg8000`**, consistente com ADR-001/005 (Python puro,
sem dependência nativa compilada) — a decisão de driver é do projeto como
um todo, não do módulo de backend especificamente.

## Alternativas consideradas

| Alternativa | Motivo de descarte |
|---|---|
| Import direto de `crud/avaliacoes.py` (como um script batch, mesmo padrão do `generate_seed_dev.py`) | Descartada a pedido do autor — o objetivo aqui é isolamento total do scraper em relação ao backend, não reaproveitamento de código, mesmo que ambos sejam scripts Python no mesmo repositório. |
| POST no endpoint FastAPI existente (`X-API-Key`, ADR-007), como um cliente HTTP externo | Descartada — scraping é um job batch, não uma origem de captura em tempo real como Pinpad/Totem; adicionar HTTP + autenticação para gravação seria uma camada extra sem ganho real neste escopo. |
| Servir as fixtures via processo HTTP separado (`python -m http.server`) | Descartada — o FastAPI já está em execução no mesmo ambiente (Codespaces); um segundo processo para documentar/manter não traz benefício proporcional. |

## Consequências

- **Duplicação de lógica de INSERT** entre `crud/avaliacoes.py` (backend)
  e `src/scraping/gravacao.py` (scraper) — aceita conscientemente. Risco
  de divergência é baixo: a regra mais crítica (`nota` entre 1 e 5) já é
  garantida por `CHECK` no banco (ADR já vigente em
  `data_model_relational.md`), independente de qual código faz o INSERT.
- **Sem dedup entre execuções** — rodar `executar_scraping.py` duas vezes
  duplica os registros. Mesmo racional já aplicado a `avaliacoes` no
  operacional (ADR-002: dedup é responsabilidade da camada Silver, não do
  Postgres).
- **`id_origem` resolvido dinamicamente** (`SELECT ... WHERE nome =
  'Scraping'`), nunca hardcoded — evita acoplar o script a um valor de
  surrogate key que pode variar entre ambientes (dev/Codespaces vs.
  produção futura).
- **`requirements.txt`**: adicionar `beautifulsoup4` (parsing HTML);
  `requests` e `pg8000` já são dependências existentes do projeto.
- **`main.py`**: novo `app.mount("/fixtures/reviews", StaticFiles(...))`
  para servir as páginas fixture — único ponto de contato entre scraper e
  o processo do backend, e mesmo assim só como servidor HTTP passivo, não
  como código importado.
- Sem impacto em `schema.sql` ou nos ADRs 001-010.

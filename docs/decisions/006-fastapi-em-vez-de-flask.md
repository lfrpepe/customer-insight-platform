# ADR 006 — FastAPI em vez de Flask como framework de backend

**Status:** Aceito
**Data:** 2026-07-24
**Fase:** 5 — Backend

## Contexto

A Fase 1 (Arquitetura) e a documentação inicial do projeto (`README.md`,
`architecture.md`) haviam definido **Flask** como framework de backend para
o cadastro de avaliações (Formulário Web — apenas *Create*, sem tela
administrativa de edição/exclusão) e para a interface de Pinpad/Totem.

Ao iniciar a Fase 5, foi levantada a possibilidade de usar **FastAPI** no
lugar do Flask, motivada inicialmente por relevância de mercado (framework
mais recente, maior demanda em vagas da área).

## Decisão

Adotar **FastAPI** como framework de backend para toda a Fase 5 (cadastro
de avaliações via Formulário Web, interface Pinpad/Totem, integração
Telemarketing), substituindo a escolha original de Flask.

Além do motivo de mercado, a troca tem justificativa técnica própria para
este projeto:

- **Validação de payload via Pydantic**, nativa do FastAPI — reduz código
  comparado a WTForms para o mesmo nível de validação, e reforça a exigência
  de tipagem já definida como boa prática do projeto.
- **Documentação automática (OpenAPI/Swagger)** sem esforço adicional.
- Formulários HTML (Pinpad/Totem/Formulário Web) continuam viáveis via
  `Jinja2Templates` (Starlette) — menos idiomático que Flask+Jinja2, mas sem
  perda funcional para o escopo (terminais internos sem sessão de usuário,
  formulário público simples).

## Alternativas consideradas

| Alternativa | Motivo de descarte |
|---|---|
| Manter Flask (decisão original da Fase 1) | Descartada — não havia nenhuma implementação de código Flask ainda (Fase 5 não iniciada), custo de troca é zero; FastAPI atende igualmente bem ao escopo e agrega Pydantic + docs automáticas. |
| Streamlit standalone para Pinpad/Totem, mantendo Flask ou FastAPI só para o Formulário Web | Descartada — duplicaria stack (dois frameworks web), duas formas de conexão ao banco, e dois processos para manter/documentar/deployar, sem ganho funcional proporcional ao escopo (interfaces de captura minimalistas). |

## Consequências

- **`requirements.txt`**: adicionar `fastapi`, `uvicorn`, `pydantic`,
  `jinja2`, `python-multipart`.
- **Estrutura de código**: rotas organizadas como `APIRouter` (FastAPI) em
  vez de Blueprint (Flask); validação de forma/tipo de campo via schemas
  Pydantic em `src/schemas/`; `src/validators/` mantido apenas para regras
  de negócio que Pydantic não cobre (ex.: dígito verificador de CPF).
- **Deploy**: servido via `uvicorn` em vez de `flask run`; free tier (Render
  ou execução local/Codespaces) segue compatível sem mudança de plano.
- **Documentação a atualizar**: `README.md` (tabela de stack),
  `architecture.md` (menções a Flask), `status.md` (log de decisões e
  próximos passos da Fase 5). Nenhum impacto em `schema.sql` ou nos ADRs
  001-005 (camada de banco não muda).

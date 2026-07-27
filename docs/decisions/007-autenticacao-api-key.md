# ADR 007 — Autenticação via API Key nas rotas do backend

**Status:** Aceito
**Data:** 2026-07-27
**Fase:** 5 — Backend

## Contexto

As 4 rotas de Create (Formulário Web, Pinpad, Totem, Telemarketing) foram
implementadas e testadas sem nenhuma camada de autenticação — qualquer
requisição bem formada, de qualquer origem, era aceita e gravava no
Supabase. Isso é aceitável enquanto o backend roda só localmente/Codespaces
(ver `status.md`), mas o autor pediu proativamente uma camada de segurança
antes de considerar a Fase 5 encerrada, prevendo uma futura publicação em
free tier.

Não existe, no projeto, nenhuma entidade de usuário/login — `clientes` é
quem *recebe* o atendimento, não quem *acessa* o sistema.

## Decisão

Proteger **as 4 rotas** com autenticação via **API Key simples**, enviada
no header `X-API-Key` e conferida contra a variável de ambiente `API_KEY`
(nunca hardcoded — mesmo padrão de `.env` já usado para credenciais do
Supabase).

Implementação como uma dependência do FastAPI
(`src/security/api_key.py::verificar_api_key`), aplicada centralizadamente
no `main.py` via `dependencies=[Depends(verificar_api_key)]` em cada
`include_router(...)` — em vez de repetir a dependência dentro de cada um
dos 4 routers. O FastAPI reconhece automaticamente o esquema `APIKeyHeader`
e expõe um botão "Authorize" no Swagger, então testar continua possível sem
precisar montar o header manualmente a cada chamada.

Todas as 4 rotas foram incluídas — mesmo Formulário Web e Totem, que em
outro cenário poderiam ser formulários públicos sem login — porque, neste
projeto, são terminais/telas operadas dentro do ambiente da empresa
fictícia, não endpoints públicos da internet.

## Alternativas consideradas

| Alternativa | Motivo de descarte |
|---|---|
| OAuth2/JWT completo | Exigiria modelar uma entidade de usuário (tabela, senha com hash, endpoint de login, emissão/renovação de token) — infraestrutura desproporcional ao escopo atual, que não tem conceito de "usuário do sistema" definido em nenhuma fase do roadmap. Fica como evolução possível na Fase 10 (Melhorias), se o projeto ganhar uma tela administrativa real. |
| HTTP Basic Auth | Também simples, mas transmite usuário/senha em vez de um segredo único por integração; menos natural para as origens que são sistemas (Pinpad, Totem, Telemarketing) e não pessoas logando. API Key comunica melhor a intenção: "quem está integrando", não "quem está logado". |
| Proteger só as rotas internas (Pinpad/Telemarketing) | Descartada pelo autor — todas as 4 rotas ficam atrás da mesma chave, por simplicidade (uma única forma de acesso a proteger, não duas regras diferentes para lembrar). |

## Consequências

- **`.env` / `.env.example`:** nova variável `API_KEY` (valor aleatório,
  gerado localmente — ver comentário no `.env.example`).
- **`src/security/api_key.py`:** novo módulo, sem dependência nova em
  `requirements.txt` (`fastapi.security` já vem com o FastAPI).
- **Testes via Swagger:** precisa clicar em "Authorize" (cadeado no topo da
  página `/docs`) e informar a API Key uma vez por sessão do navegador,
  antes de testar qualquer rota.
- **Testes via `curl`/script:** precisa incluir o header manualmente, ex.:
  `curl -X POST .../avaliacoes/totem -H "X-API-Key: <valor>" -H "Content-Type: application/json" -d '{"nota": 5}'`
- **Sem impacto em `schema.sql`** nem nos ADRs 001-006 — autenticação é
  camada de aplicação (FastAPI), não de banco.
- **Evolução futura:** se o projeto ganhar login de usuário administrativo
  (fora do escopo atual), a API Key pode conviver com um esquema
  OAuth2/JWT adicional para rotas de leitura/edição — não é
  mutuamente exclusivo, só não é necessário agora.

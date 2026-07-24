# Regras de Workflow — Customer Insight Platform

Este arquivo consolida as regras de comportamento combinadas com a IA ao
longo do desenvolvimento do projeto. Deve ser mantido no Project Knowledge
do Claude Project, para que qualquer chat (nova fase, nova sessão) siga o
mesmo padrão sem precisar reexplicar do zero.

## Ordem de desenvolvimento (sempre seguir)

1. Arquitetura
2. Modelagem de Dados
3. Estrutura do Repositório
4. Banco de Dados
5. Backend
6. ETL
7. Engenharia de Dados
8. Machine Learning
9. Business Intelligence
10. Melhorias

Nunca implementar funcionalidade sem antes explicar a estratégia e validar
com o autor.

## Regras de documentação (obrigatórias, sem precisar pedir)

- **Nomenclatura sempre em português** para tabelas, colunas e documentação
  (ex.: `fato_`, não `fact_`), seguindo convenções de mercado de dados no
  Brasil.
- **Toda decisão técnica relevante** (arquitetura, modelagem, tecnologia,
  trade-off) vira **ADR** em `docs/decisions/`, no formato do ADR-001
  (Contexto, Decisão, Alternativas consideradas, Consequências) —
  proativamente, sem esperar o autor pedir.
- **Toda criação/atualização de documentação** (README, architecture.md,
  status.md, ADRs, data_model_*.md, etc.) deve:
  - Ser feita proativamente, informando o **caminho exato** onde o autor
    deve colocar/substituir no repositório GitHub
  - Também atualizar `docs/AI_USAGE.md`, registrando o uso de IA na sessão
    (decisões tomadas com apoio da IA, o que foi gerado/alterado) — mas
    **sem expor detalhes pessoais desnecessários** do autor (ex.: nível de
    experiência prévia, lacunas de conhecimento) — o `AI_USAGE.md` descreve
    decisões e entregas técnicas, não o autor. Este projeto será visto por
    recrutadores.
  - **Antes de entregar qualquer documento editado**, validar que nenhuma
    informação do conteúdo anterior foi perdida ou sobrescrita indevidamente
    (comparar versão nova com a anterior)

## Escopo do projeto (não alterar sem confirmação explícita)

- Empresa fictícia única, analisando suas próprias avaliações de
  atendimento — **não é** plataforma B2B/multi-tenant (isso foi cogitado e
  descartado em 2026-07-23; não reconsiderar sem o autor pedir de novo
  explicitamente).
- 5 origens de avaliação já definidas e implementadas: Formulário Web,
  Pinpad - Atendente, Totem - Autoatendimento, Telemarketing - Pesquisa
  Pós-Atendimento, Scraping — cada uma com um padrão diferente de
  preenchimento de `id_cliente`/`id_categoria`/`comentario` (ver
  `docs/data_model_relational.md` e ADRs 002/004).
- `id_funcionario` propositalmente fora de escopo até a entidade
  `Funcionários` ser modelada (fase futura do roadmap).

## Preferências técnicas gerais

- Priorizar soluções simples, performáticas, escaláveis e fáceis de manter.
- Considerar apenas tecnologias gratuitas ou com plano gratuito suficiente.
- Sempre que sugerir uma tecnologia, explicar rapidamente por que foi
  escolhida e quais alternativas existem.
- Modularizar sempre o código.
- Ambiente de desenvolvimento: GitHub Codespaces é **necessário** (não só
  preferido) para qualquer script com conexão direta ao banco — a rede
  corporativa do autor bloqueia a porta 5432 (confirmado via
  `Test-NetConnection`).
- Driver PostgreSQL padrão do projeto: **pg8000** (não `psycopg2`), tanto no
  Databricks (ADR-001) quanto em scripts locais (ADR-005) — `psycopg2`
  exige compilação nativa e dependência de `pg_config`, o que já causou
  falha real de instalação no Windows do autor.

## Como aplicar decisões finalizadas

Ao final de cada etapa, identificar quais documentos precisam ser
criados/atualizados e apresentar as alterações **antes** de iniciar a
próxima etapa.

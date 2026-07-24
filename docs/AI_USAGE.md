# Uso de IA no desenvolvimento deste projeto

Este projeto foi desenvolvido com apoio do **Claude** (Anthropic), atuando como
Tech Lead consultivo ao longo de todas as fases: arquitetura, modelagem,
implementação, engenharia de dados e documentação.

## Como a IA foi utilizada

- **Revisão e validação de arquitetura** antes de qualquer implementação —
  incluindo identificação de inconsistências conceituais (ex.: distinção entre
  banco operacional e camada Bronze) e riscos técnicos antes de escrever
  código.
- **Discussão de trade-offs técnicos**, com alternativas e justificativas para
  cada tecnologia escolhida, não apenas a escolha em si.
- **Modelagem de dados incremental e validada por regra de negócio** — o
  modelo relacional evoluiu em várias rodadas de discussão (FKs opcionais por
  origem, ADR-002; rastreabilidade de dado sintético vs. real, ADR-003; nova
  origem de captura via Telemarketing, ADR-004), sempre com o racional
  registrado antes da implementação, não apenas o resultado.
- **Geração de dados sintéticos com validação estatística** — o seed de
  desenvolvimento (`generate_seed_dev.py`) não foi apenas gerado, mas
  auditado quanto a realismo: a IA identificou e corrigiu uma concentração
  de recorrência de cliente irreal (Pareto com cauda longa demais, chegando a
  200+ avaliações/cliente/ano) e implementou perfis de satisfação por cliente
  para que a nota deixasse de ser puramente aleatória e passasse a refletir
  um padrão de comportamento coerente com o objetivo de negócio de
  "identificar clientes recorrentemente insatisfeitos".
- **Correção de rumo em decisão de escopo** — ao cogitar transformar o projeto
  em uma plataforma B2B multi-tenant, a IA detalhou as implicações estruturais
  antes de qualquer implementação; a decisão final (manter escopo de empresa
  única) foi do autor, e o pivô descartado ficou registrado para não ser
  reconsiderado sem intenção explícita em conversas futuras.
- **Evolução do seed de arquivos `.sql` para conexão direta no banco** — o
  seed de desenvolvimento evoluiu de "gerar arquivos `.sql` para colar
  manualmente" para "conectar e gravar direto no banco". A primeira escolha
  de driver (`psycopg2-binary`) falhou na instalação real (exigia compilar
  extensão C, dependência ausente no Windows do autor); a IA diagnosticou a
  causa e migrou o script para `pg8000` (Python puro), unificando o projeto
  em um único driver PostgreSQL — decisão registrada e corrigida no próprio
  ADR, não escondida. Credenciais isoladas em `.env` (não versionado), com
  `.env.example` documentando as variáveis esperadas — necessário por este
  ser um repositório público.
- **Diagnóstico de restrição de rede corporativa** — ao falhar a conexão
  local com o Supabase (`ConnectionRefusedError`), a IA orientou um teste
  isolado de conectividade de rede (`Test-NetConnection`) antes de suspeitar
  do código, confirmando bloqueio de porta pela rede corporativa e
  direcionando para a solução já prevista na arquitetura (GitHub Codespaces).
- **Correção de bug próprio** — uma execução aparentemente bem-sucedida do
  script de seed ocultava a ausência de um `commit()` explícito na
  transação (o driver usado não comita automaticamente ao fechar a
  conexão); a IA identificou o problema ao investigar um erro secundário,
  corrigiu e orientou a reexecução — confirmada com sucesso (500 clientes,
  5.000 avaliações persistidos).
- **Diagnóstico de erro de infraestrutura do Supabase** — investigação de
  um erro (`schema "pg_pgrst_no_exposed_schemas" does not exist`) via busca
  na documentação oficial, confirmando tratar-se de comportamento esperado
  (consequência de uma configuração já decidida pelo autor — Data API
  desabilitada) e não uma falha real do projeto.
- **Suporte a debugging de problemas reais de ambiente** — por exemplo, o
  diagnóstico passo a passo de um driver PostgreSQL incompatível com o
  compute serverless do Databricks Free Edition, isolando a causa (DNS → TCP →
  driver) até a resolução, documentado no
  [ADR 001](decisions/001-driver-postgres-databricks-serverless.md).
- **Correção de numeração de fases** — o `status.md` havia agrupado os
  passos 3 e 4 do roadmap original (Estrutura do Repositório e Banco de
  Dados) sob um rótulo próprio ("Fase 2"), criando ambiguidade quando o
  autor questionou se a Fase 5 (Backend) representava um "pulo" de fase; a
  IA identificou a causa raiz (numeração interna divergente do roadmap
  oficial de 10 passos) e corrigiu a rotulagem em todos os documentos afetados.
- **Revisão de realismo dos dados gerados** — após a primeira carga real no
  Supabase, o autor revisou os dados manualmente e apontou inconsistências
  (e-mail sem relação com o nome, telefone em formatos variados); a IA
  corrigiu ambos, e também esclareceu, distinguindo de bugs reais, três
  comportamentos que eram esperados por design (IDs não sequenciais desde 1
  por causa de sequências não-transacionais do Postgres, `id_cidade` nulo
  por design, e exibição em UTC de colunas `TIMESTAMPTZ`).
- **Auditoria de consistência da documentação** — varredura final
  cruzando schema, script de carga e todos os documentos: validou as regras
  de negócio das 5 origens por teste automatizado (zero violações),
  identificou e corrigiu numeração de fases divergente nos ADRs, um ADR sem
  referência cruzada, arquivos obsoletos remanescentes e uma lacuna não
  documentada (cobertura parcial da análise de sentimento entre origens).
- **Geração e revisão de documentação técnica** (ADRs, arquitetura, modelo de
  dados, status do projeto, README), mantida atualizada a cada decisão relevante —
  não apenas ao final de cada fase, mas incrementalmente, à medida que cada
  discussão técnica gerava uma mudança real no schema ou na estratégia.

## O que não foi delegado

Todas as decisões arquiteturais foram avaliadas e compreendidas antes de serem
adotadas — a IA propôs, questionou e explicou; a condução técnica, validação
prática (contas, ambientes, testes reais), execução dos scripts no banco de
dados real e as decisões finais (incluindo reverter um pivô de escopo
proposto) são do autor.

## Por que documentar isso

Este projeto é peça de portfólio profissional. Uso de IA como parceiro técnico
é uma prática real e crescente em engenharia de software e dados — o objetivo
aqui é demonstrar não apenas conhecimento técnico das ferramentas envolvidas,
mas também a capacidade de conduzir um projeto complexo utilizando IA de forma
crítica e estratégica, e não como substituto do raciocínio técnico.

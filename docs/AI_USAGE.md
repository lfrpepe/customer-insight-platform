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
- **Avaliação técnica de troca de framework antes de codar** — ao iniciar a
  Fase 5, foi levantada a possibilidade de usar FastAPI em vez do Flask
  originalmente planejado (Fase 1), por indicação de mercado; a IA avaliou
  o trade-off tecnicamente (validação via Pydantic, documentação automática,
  viabilidade de servir formulários HTML) antes de confirmar a mudança,
  registrada em [ADR 006](decisions/006-fastapi-em-vez-de-flask.md), com
  atualização de todos os documentos que citavam Flask.
- **Geração dos módulos de backend da Fase 5** (FastAPI) — `connection.py`
  (conexão pg8000 generalizada a partir do padrão do seed), `crud/avaliacoes.py`
  (ponto único de escrita, parametrizado por origem), validador de CPF,
  4 schemas Pydantic e 4 routers (um por origem: Formulário Web, Pinpad,
  Totem, Telemarketing) mais `main.py`.
- **Correção do mecanismo de categoria do Pinpad** — a IA havia assumido um
  mapeamento fixo guichê→categoria (`config/settings.py`) como placeholder;
  o usuário esclareceu que a categoria do atendimento presencial em caixa é
  selecionada pelo próprio operador, não fixa por guichê (não há múltiplos
  guichês com categorias distintas no projeto). Corrigido: schema/router do
  Pinpad passaram a receber `categoria` diretamente (igual ao Formulário
  Web), `config/settings.py` foi removido, e a descrição do Pinpad em
  `data_model_relational.md` foi ajustada para refletir a regra real.
- **Correção de normalização de telefone** — teste real via Swagger revelou
  que o schema do Formulário Web gravava o telefone sem padronização. A IA
  propôs inicialmente replicar o formato `(DDD) 9XXXX-XXXX` já usado no
  seed sintético; o usuário preferiu, por boa prática, o formato somente
  dígitos (mesmo padrão do CPF), mais simples para busca/deduplicação e
  sem necessidade de reprocessar formatação em ETL/BI. Ajustado em 3
  pontos para manter consistência: `validators/cliente.py`
  (`telefone_normalizado`), schema do Formulário Web, e
  `generate_seed_dev.py::gerar_telefone()` (para futuras repopulações).
  Dados já existentes no banco precisam do UPDATE de normalização abaixo
  antes de considerar a coluna consistente:
  `UPDATE clientes SET telefone = regexp_replace(telefone, '\D', '', 'g') WHERE telefone IS NOT NULL;`
- **Correção de bug real no router de Telemarketing** — teste com
  `id_cliente`/`id_categoria` inexistentes retornou erro `500` cru
  (violação de foreign key do Postgres) em vez de um erro tratado.
  Adicionadas verificações explícitas (`verificar_cliente_existe`,
  `verificar_categoria_existe`) antes do `INSERT`, devolvendo `422` com
  mensagem legível — mesmo padrão de tratamento já usado nos outros 3
  routers.
- **Adição de camada de autenticação (API Key)** — a pedido do autor, após
  as 4 rotas estarem testadas e funcionando sem nenhuma proteção de
  acesso. Como o projeto não tem entidade de usuário/login, a IA avaliou
  as alternativas (API Key vs. OAuth2/JWT completo vs. HTTP Basic Auth) e
  recomendou API Key por ser proporcional ao escopo atual — decisão
  confirmada pelo autor e registrada em
  [ADR 007](decisions/007-autenticacao-api-key.md). Implementada como
  dependência única do FastAPI (`src/security/api_key.py`), aplicada
  centralizadamente no `main.py` em vez de repetida em cada router.
- **Templates HTML das 4 origens, com correção de expectativa sobre o
  Telemarketing** — ao planejar a tela do Telemarketing, a IA apontou que
  essa origem é uma integração de sistema (ADR-004), não uma tela operada
  por pessoa, e ofereceu duas opções: seguir só com a API (mais fiel ao
  cenário real) ou construir uma tela rotulada como "simulador de
  integração" para fins de demonstração no portfólio. O autor escolheu a
  segunda opção; a tela foi construída com aviso explícito de que
  representa o CRM/discador chamando a API automaticamente, não um
  atendente. Também identificado e sinalizado no código: a chave de API
  injetada no HTML renderizado só é apropriada porque essas telas rodam
  no ambiente interno da empresa fictícia (ADR-007) — se o Formulário Web
  virasse público na internet, esse padrão precisaria mudar.
- **Proposta de login individual avaliada e adiada conscientemente** — o
  autor pediu uma tela de login que autentica o operador e distribui a
  API Key. A IA apontou que isso exigiria uma tabela de
  usuários/operadores agora, antecipando parte da entidade `Funcionários`
  (fora de escopo até ser modelada oficialmente, ver ADR-002), e ofereceu
  duas opções (usuário/senha único vs. tabela de operadores). O autor
  optou por adiar todo esse ponto para a Fase 10 (Melhorias), mantendo a
  API Key (ADR-007) como suficiente por ora — registrado em `status.md`
  para não ser reconsiderado sem pedido explícito.
- **Melhorias de UI implementadas** (as duas que não exigiam decisão de
  arquitetura, diferente do login): nota trocada de botões numéricos para
  um picker de estrelas com animação de seleção, e a mensagem de
  sucesso/erro trocada de um bloco inline (que passava despercebido em
  envios seguidos rápidos, ex. Pinpad/Totem) para um toast fixo no topo
  da tela, com animação de entrada/saída — reutilizados via
  `src/static/app.js` em todas as 4 telas. Adicionada também uma tela de
  navegação (`/`) listando as 4 origens.
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

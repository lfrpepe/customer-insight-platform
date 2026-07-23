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
- **Suporte a debugging de problemas reais de ambiente** — por exemplo, o
  diagnóstico passo a passo de um driver PostgreSQL incompatível com o
  compute serverless do Databricks Free Edition, isolando a causa (DNS → TCP →
  driver) até a resolução, documentado no
  [ADR 001](decisions/001-driver-postgres-databricks-serverless.md).
- **Geração e revisão de documentação técnica** (ADRs, arquitetura, modelo de
  dados, status do projeto), mantida atualizada a cada decisão relevante —
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

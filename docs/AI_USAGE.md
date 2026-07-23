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
- **Suporte a debugging de problemas reais de ambiente** — por exemplo, o
  diagnóstico passo a passo de um driver PostgreSQL incompatível com o
  compute serverless do Databricks Free Edition, isolando a causa (DNS → TCP →
  driver) até a resolução, documentado no
  [ADR 001](decisions/001-driver-postgres-databricks-serverless.md).
- **Geração e revisão de documentação técnica** (ADRs, arquitetura, status do
  projeto), mantida atualizada ao final de cada fase/sprint.

## O que não foi delegado

Todas as decisões arquiteturais foram avaliadas e compreendidas antes de serem
adotadas — a IA propôs, questionou e explicou; a condução técnica, validação
prática (contas, ambientes, testes reais) e as decisões finais são do autor.

## Por que documentar isso

Este projeto é peça de portfólio profissional. Uso de IA como parceiro técnico
é uma prática real e crescente em engenharia de software e dados — o objetivo
aqui é demonstrar não apenas conhecimento técnico das ferramentas envolvidas,
mas também a capacidade de conduzir um projeto complexo utilizando IA de forma
crítica e estratégica, e não como substituto do raciocínio técnico.

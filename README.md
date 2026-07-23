# Customer Insight Platform

Plataforma de dados end-to-end, simulando um ambiente corporativo real, para
centralizar, tratar, enriquecer e analisar avaliações de clientes sobre um
serviço de atendimento.

Projeto de portfólio profissional — não é um exercício isolado, e sim uma
simulação de solução de dados moderna usada por empresas: da ingestão bruta até
dashboards executivos, passando por Engenharia de Dados, Machine Learning e
boas práticas de arquitetura de software.

## Objetivo

Demonstrar capacidade de projetar, construir e documentar uma solução de dados
completa, utilizando exclusivamente ferramentas gratuitas, com arquitetura
evolutiva (permite crescer em funcionalidades sem reestruturação).

## Stack

| Camada | Tecnologia | Papel |
|---|---|---|
| Banco operacional (OLTP) | PostgreSQL (Supabase) | Armazena dados brutos de origem |
| Engenharia de Dados | Databricks Free Edition + Apache Spark | ETL, Bronze/Silver/Gold, Machine Learning |
| Backend / Cadastro | Flask | CRUD de avaliações com validações |
| Ingestão | Web Scraping + APIs Públicas | Múltiplas fontes de dados |
| BI | Power BI | Dashboards executivos sobre a camada Gold |
| Versionamento | GitHub + GitHub Actions | Código, documentação, automação |

## Arquitetura

Ver detalhes completos em [`docs/architecture.md`](docs/architecture.md).

Resumo:
```
Fontes de Dados (Scraping, Formulário, API)
        ↓
PostgreSQL / Supabase  (Banco Operacional — OLTP)
        ↓
Databricks — Bronze  (dado bruto, ingestão sem regras de negócio)
        ↓
Databricks — Silver  (limpeza, padronização, enriquecimento, sentimento)
        ↓
Databricks — Gold    (modelo estrela, KPIs, agregações)
        ↓
Power BI              (dashboards executivos)
```

## Estrutura do repositório

```
src/            código-fonte modular (api, crud, database, etl, scraping, ml, etc.)
docs/           documentação técnica e decisões de arquitetura (ADRs)
notebooks/      notebooks de exploração e ETL (Databricks)
tests/          testes automatizados
.github/        workflows de CI/CD e agendamento
```

## Status do projeto

O andamento por fase é mantido em [`docs/status.md`](docs/status.md).

## Documentação

- [Arquitetura](docs/architecture.md)
- [Modelo Relacional](docs/data_model_relational.md)
- [Modelo Dimensional](docs/data_model_dimensional.md)
- [Decisões técnicas (ADRs)](docs/decisions/)

## Sobre o processo de desenvolvimento

Este projeto foi construído com apoio de IA (Claude, Anthropic) como parceiro
técnico — [detalhes em `docs/AI_USAGE.md`](docs/AI_USAGE.md).

## Licença

Projeto de portfólio pessoal, uso livre para fins de estudo e referência.

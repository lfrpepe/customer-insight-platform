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
| Ingestão | Web Scraping + Pinpad + Totem + Telemarketing + APIs Públicas | Múltiplas fontes de dados, com níveis de estrutura diferentes |
| BI | Power BI | Dashboards executivos sobre a camada Gold |
| Versionamento | GitHub + GitHub Actions | Código, documentação, automação |

## Fontes de avaliação

O projeto simula 4 canais distintos de captura, cada um com um grau diferente
de estrutura — o que é proposital, para demonstrar modelagem de dados capaz
de lidar com dado estruturado e não estruturado ao mesmo tempo:

| Origem | Cliente identificado | Categoria | Texto livre |
|---|:---:|:---:|:---:|
| Formulário Web (Flask) | ✅ | ✅ | opcional |
| Pinpad - Atendente | ❌ | ✅ (fixa por atendimento) | ❌ |
| Totem - Autoatendimento | ❌ | ❌ | ❌ |
| Telemarketing - Pesquisa Pós-Atendimento | ✅ | ✅ | ❌ |
| Web Scraping | ❌ | ❌ | ✅ |

Detalhamento em [`docs/data_model_relational.md`](docs/data_model_relational.md).

## Arquitetura

Ver detalhes completos em [`docs/architecture.md`](docs/architecture.md).

Resumo:
```
Fontes de Dados (Scraping, Formulário, Pinpad, Totem, Telemarketing, API)
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

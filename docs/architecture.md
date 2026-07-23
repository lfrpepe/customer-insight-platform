# Arquitetura — Customer Insight Platform

## Visão geral

A plataforma segue uma arquitetura em camadas, inspirada no padrão **Medallion
Architecture** (Bronze / Silver / Gold), separando claramente o banco
operacional (onde os dados nascem) da plataforma analítica (onde os dados são
tratados e preparados para consumo).

```
Fontes de Dados
   ├── Web Scraping (avaliações públicas)
   ├── Sistema Web / Flask (CRUD de avaliações)
   └── APIs Públicas (ViaCEP, IBGE, Open-Meteo, etc. — enriquecimento)
        ↓
PostgreSQL (Supabase) — Banco Operacional (OLTP)
        ↓  [ingestão]
Databricks — Bronze (Delta Table, dado bruto, sem regras de negócio)
        ↓  [limpeza, padronização, enriquecimento, ML]
Databricks — Silver
        ↓  [agregações, modelo estrela, KPIs]
Databricks — Gold
        ↓
Power BI — Dashboards executivos
```

## Por que Postgres não é a camada Bronze

Um ponto importante, corrigido ainda na fase de planejamento: o PostgreSQL
(Supabase) é modelado com chaves primárias, chaves estrangeiras, constraints e
normalização — características de um banco **operacional (OLTP)**, não de uma
camada Bronze.

Bronze, na Medallion Architecture, é dado bruto, schema-on-read, sem regras de
integridade aplicadas na ingestão. Por isso:

- **PostgreSQL/Supabase** = sistema de origem (onde o dado é criado/cadastrado)
- **Databricks Bronze** = cópia raw desses dados, materializada como Delta
  Table, sem transformação — é o ponto real de ingestão para a plataforma
  analítica

Essa distinção evita confundir "banco de dados da aplicação" com "camada de
data lake", que são conceitos e responsabilidades diferentes.

## Camadas

### Banco Operacional — PostgreSQL (Supabase)

Responsável por armazenar todos os dados brutos gerados pelas fontes
(cadastro via Flask, resultado do scraping, enriquecimento via API). Modelado
com integridade referencial completa.

Conexão: Session Pooler (porta 5432, compatível com IPv4) — ver
[ADR 001](decisions/001-driver-postgres-databricks-serverless.md) para a
decisão de driver usada no lado Databricks.

### Bronze (Databricks)

- Ingestão do PostgreSQL para Delta Table, sem transformação
- Sem regras de negócio, sem agregações, sem enriquecimento

### Silver (Databricks)

- Padronização e limpeza (datas, texto, duplicidades)
- Enriquecimento com dados das APIs públicas
- Análise de sentimento (Machine Learning)
- Validações de qualidade de dados

### Gold (Databricks)

- Modelo estrela (fatos e dimensões)
- KPIs e métricas agregadas
- Tabelas prontas para consumo direto pelo Power BI

### Power BI

Consome exclusivamente a camada Gold — nunca acessa Bronze, Silver ou o
Postgres operacional diretamente.

## Ambiente e ferramentas

| Componente | Ferramenta | Motivo da escolha |
|---|---|---|
| Banco operacional | Supabase (Postgres free tier) | Postgres gerenciado gratuito, com painel completo |
| Plataforma analítica | Databricks Free Edition | Spark gerenciado, gratuito, sem necessidade de infraestrutura própria |
| Orquestração | GitHub Actions | Gratuito, versionado junto ao código, evita dependência de agendador externo pago |
| Ambiente de desenvolvimento | GitHub Codespaces | Elimina dependência de instalação local aprovada por TI |
| BI | Power BI Desktop | Ferramenta de mercado, gratuita para uso individual |

## Decisões técnicas registradas

Decisões arquiteturais relevantes (motivo, alternativas descartadas,
consequências) ficam documentadas como ADRs em
[`docs/decisions/`](decisions/), não apenas no histórico de conversas — isso
mantém o racional das escolhas acessível para qualquer pessoa lendo o
repositório, inclusive recrutadores avaliando o projeto.

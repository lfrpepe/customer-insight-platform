# Arquitetura — Customer Insight Platform

## Visão geral

A plataforma segue uma arquitetura em camadas, inspirada no padrão **Medallion
Architecture** (Bronze / Silver / Gold), separando claramente o banco
operacional (onde os dados nascem) da plataforma analítica (onde os dados são
tratados e preparados para consumo).

```
Fontes de Dados
   ├── Web Scraping (avaliações públicas — dado não estruturado: nota + comentário)
   ├── Sistema Web / FastAPI (cadastro de avaliações, apenas Create — dado estruturado completo)
   ├── Pinpad - Atendente (nota ao final de um atendimento — sem cliente, com categoria)
   ├── Totem - Autoatendimento (nota espontânea do cliente — sem cliente, sem categoria)
   ├── Telemarketing - Pesquisa Pós-Atendimento (nota por IVR — cliente e categoria conhecidos, sem comentário)
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

## Rastreabilidade de dado sintético vs. real

Como o projeto precisa existir e ser demonstrável antes dos sistemas reais de
captura (Flask, Pinpad, Totem, Telemarketing, Scraper) estarem prontos, o
banco operacional é populado por um seed de desenvolvimento
(`generate_seed_dev.py`, Faker). Para não confundir dado de demonstração com
dado que os sistemas reais vão gravar mais adiante, `clientes` e
`avaliacoes` possuem a coluna `natureza_registro` (`'Sintético'` ou
`'Real'`, default `'Real'`) — ver
[ADR 003](decisions/003-natureza-registro-sintetico-real.md).

O Bronze ingere tudo sem filtrar; a decisão de segmentar ou excluir dado
sintético de uma análise fica para o Silver/Gold e para o próprio dashboard
Power BI (slicer de "Sintético"/"Real").

## Fontes de avaliação: preenchimento variável por origem

Diferente da primeira versão da arquitetura (que assumia toda avaliação com
cliente e categoria conhecidos), o projeto passou a suportar cinco origens
com níveis de estrutura diferentes:

| Origem                     | Cliente | Categoria | Comentário | O que é possível analisar |
|-----------------------------|:-------:|:---------:|:----------:|-----------------------------|
| Formulário Web (FastAPI)      | ✅      | ✅        | opcional   | Histórico por cliente, recorrência, sentimento |
| Pinpad - Atendente            | ❌      | ✅ (fixa por guichê) | ❌ | Nota por categoria/atendimento, sem rastrear cliente |
| Totem - Autoatendimento       | ❌      | ❌        | ❌         | Nota geral por origem/período |
| Telemarketing - Pesquisa Pós-Atendimento | ✅ | ✅ | ❌ | Histórico por cliente e recorrência (ver [ADR 004](decisions/004-origem-telemarketing.md)), sem sentimento (sem texto) |
| Web Scraping                  | ❌      | ❌        | ✅         | Nota + sentimento (análise de texto) por origem/período |

Essa variação é modelada no banco operacional como **FKs opcionais**
(`id_cliente`, `id_categoria` nullable em `avaliacoes`), não como dado
faltando por falha — é a natureza estrutural de cada canal. Detalhamento
completo em [`data_model_relational.md`](data_model_relational.md).

Consequência para a camada Gold: `dim_cliente` e `dim_categoria` precisarão
de um *unknown member* (linha "Não Identificado") para mapear os `NULL`s de
cada origem sem gerar `(Blank)` no Power BI — ver
[`data_model_dimensional.md`](data_model_dimensional.md).

## Pinpad e Totem: interface

Ambos são interfaces de captura minimalista (poucos cliques, sem
autenticação de cliente), desenvolvidas na **Fase 5 — Backend**, junto com
o sistema principal. A tecnologia foi definida como **rota dedicada no
mesmo FastAPI** (não um app Streamlit separado) — ver
[ADR 006](decisions/006-fastapi-em-vez-de-flask.md), que também documenta a
troca de Flask por FastAPI como framework de backend.

Ambos gravam diretamente na tabela `avaliacoes`, reaproveitando o mesmo
módulo `database/connection.py` do backend — não é um serviço separado com
banco próprio.

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
(cadastro via FastAPI, pinpad, totem, resultado do scraping, enriquecimento
via API). Modelado com integridade referencial completa, com FKs opcionais
onde a origem estruturalmente não produz aquele dado (ver seção acima).

Conexão: Session Pooler (porta 5432, compatível com IPv4) — ver
[ADR 001](decisions/001-driver-postgres-databricks-serverless.md) para a
decisão de driver usada no lado Databricks.

### Bronze (Databricks)

- Ingestão do PostgreSQL para Delta Table, sem transformação
- Sem regras de negócio, sem agregações, sem enriquecimento

### Silver (Databricks)

- Padronização e limpeza (datas, texto, duplicidades)
- Enriquecimento com dados das APIs públicas
- Análise de sentimento (Machine Learning) — aplicável apenas onde há
  `comentario` (Formulário Web e Scraping)
- Validações de qualidade de dados

### Gold (Databricks)

- Modelo estrela (fatos e dimensões)
- *Unknown member* em `dim_cliente`/`dim_categoria` para avaliações de
  origens que não produzem esses dados
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

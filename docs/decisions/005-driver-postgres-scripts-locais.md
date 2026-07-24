# ADR 005 — Driver PostgreSQL para scripts locais

**Status:** Revisado — a proposta inicial (`psycopg2-binary`) foi revertida
no mesmo dia; **decisão vigente: `pg8000` em todo o projeto** (ver seção
"Atualização" ao final)
**Data:** 2026-07-23
**Fase:** 4 — Banco de Dados

## Contexto

O ADR-001 definiu `pg8000` como driver PostgreSQL para código rodando **no
Databricks Free Edition**, porque `psycopg2-binary` é incompatível com o
compute serverless daquele ambiente especificamente.

Ao evoluir `generate_seed_dev.py` de "gera arquivos `.sql` para colar
manualmente" para "conecta e grava direto no banco", surge a dúvida: usar o
mesmo driver do Databricks (`pg8000`) por consistência, ou `psycopg2-binary`?

## Decisão

Usar **`psycopg2-binary`** em `generate_seed_dev.py` e em qualquer outro
script que rode **localmente** (máquina do desenvolvedor ou GitHub
Codespaces) — não no Databricks.

Motivo: a incompatibilidade documentada no ADR-001 é específica do compute
serverless do Databricks (driver nativo em C não disponível naquele
ambiente restrito). Rodando localmente, essa restrição não existe —
`psycopg2-binary` é o driver PostgreSQL mais usado no ecossistema Python,
com melhor documentação e mais direto para scripts simples (`RETURNING`,
`execute_values` para insert em lote).

Não é inconsistência usar dois drivers no mesmo projeto — é usar a
ferramenta certa para cada ambiente de execução, documentado explicitamente
para não parecer descuido.

## Alternativas consideradas

| Alternativa | Motivo de descarte |
|---|---|
| `pg8000` também localmente, por uniformidade | Descartada — não há ganho real; forçaria sintaxe menos comum sem necessidade, já que a restrição do ADR-001 não se aplica aqui. |
| SQLAlchemy (ORM/toolkit) | Descartada por ora — overhead desnecessário para um script de seed que faz inserts diretos e simples; sem necessidade de abstração de múltiplos bancos. |

## Consequências

- `requirements.txt` passa a listar `psycopg2-binary` (scripts locais) e
  `pg8000` (uso no Databricks) — ambos coexistem, com contexto de uso
  diferente e documentado.
- Credenciais de conexão ficam em `.env` (nunca commitado — ver
  `.gitignore`), lidas via `python-dotenv`. Necessário porque o repositório
  é público no GitHub.

## Atualização (2026-07-23, mesmo dia) — decisão revertida

Na prática, `psycopg2-binary` falhou ao instalar no ambiente Windows do
autor: o `pip` não encontrou wheel pré-compilada compatível e tentou compilar
a extensão em C a partir do source, exigindo `pg_config` (ferramenta de
desenvolvimento do PostgreSQL) instalado no sistema — dependência que um
script de seed não deveria exigir.

**Decisão revisada:** usar **`pg8000` também localmente**, unificando o
projeto em um único driver. `pg8000` é implementado em Python puro — sem
extensão nativa, sem compilação, sem dependência de `pg_config` ou de um
compilador C instalado no sistema operacional do desenvolvedor.

Isso invalida a distinção original deste ADR (driver diferente por
ambiente) — mantém-se o documento por completude histórica, mas a decisão
vigente é: **`pg8000` em todo o projeto**, tanto no Databricks (ADR-001)
quanto em scripts locais. Simplicidade e portabilidade entre sistemas
operacionais (Windows/Mac/Linux) superam a familiaridade um pouco maior do
`psycopg2` no ecossistema Python.

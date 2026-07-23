# ADR 001 — Driver de conexão PostgreSQL no Databricks (Free Edition)

**Status:** Aceito
**Data:** 2026-07-23
**Fase:** 0 — Fundação

## Contexto

Durante a PoC de conectividade entre o Databricks Free Edition (compute serverless)
e o PostgreSQL do Supabase (via Session Pooler), o driver `psycopg2-binary` travou
o kernel Python de forma consistente, tanto na tentativa de conexão quanto no
simples `import psycopg2`, sem lançar exceção — resultando em "Fatal error: The
Python kernel is unresponsive."

Diagnóstico realizado, em ordem:
1. Resolução DNS do host do pooler → **OK**
2. Conexão TCP na porta 5432 → **OK**
3. `import psycopg2` (sem tentar conectar) → **Trava o kernel**
4. `import pg8000` + conexão via Session Pooler → **OK**, retorno `[1]` do `SELECT 1`

Isso isola o problema como uma incompatibilidade do `psycopg2-binary` (que depende
da extensão nativa em C `libpq`) com o ambiente de compute serverless do Databricks
Free Edition. Não é um problema de rede, credenciais ou do Supabase.

## Decisão

Todo código Python que rodar **no Databricks** e precisar conectar diretamente ao
PostgreSQL (Supabase) deve usar o driver **`pg8000`** (implementação 100% Python do
protocolo PostgreSQL, sem dependência de biblioteca nativa compilada).

```python
%pip install pg8000
dbutils.library.restartPython()

import pg8000
conn = pg8000.connect(
    user="postgres.<project-ref>",
    password="<senha>",
    host="<host>.pooler.supabase.com",
    port=5432,
    database="postgres",
    timeout=10
)
```

## Alternativas consideradas

| Alternativa | Motivo de descarte |
|---|---|
| `psycopg2-binary` | Trava o kernel serverless do Databricks Free Edition, sem erro claro |
| `psycopg2` (build da fonte) | Mesmo problema de dependência nativa; sem controle sobre o ambiente serverless para compilar/instalar libpq |
| Spark JDBC direto (sem driver Python) | Viável para leitura em lote via `spark.read.jdbc(...)`, mas não cobre casos de script Python puro (ex. validações pontuais, scripts utilitários) |

## Consequências

- **Databricks (Silver/Gold, ETL, scripts utilitários):** usar `pg8000` como
  driver padrão de conexão direta ao Postgres.
- **Flask (aplicação local/Codespaces):** não é afetado por essa restrição — roda
  em ambiente Python padrão, onde `psycopg2` funciona normalmente. Não há
  obrigatoriedade de usar `pg8000` no Flask, mas é uma opção válida caso se
  prefira manter o mesmo driver nos dois lados por consistência.
- Ingestões via Spark nativo (`spark.read.jdbc`) continuam usando o driver JDBC do
  Spark, não afetadas por esta decisão — ela se aplica especificamente a código
  Python puro rodando no Databricks.
- Esta decisão fica registrada para não ser re-descoberta por tentativa e erro em
  fases futuras do projeto.

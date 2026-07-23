-- ============================================================
-- Customer Insight Platform — Schema Relacional (MVP)
-- Fase 1 — Modelagem de Dados
-- Banco: PostgreSQL (Supabase)
-- ============================================================
-- Ordem de criação respeita as dependências de chave estrangeira:
-- estados -> cidades -> clientes -> avaliacoes
-- categorias e origem_avaliacao são independentes, criadas antes
-- de avaliacoes por conveniência de leitura.
-- ============================================================

-- ============================
-- Tabelas de domínio geográfico
-- ============================

CREATE TABLE estados (
    id_estado   SERIAL PRIMARY KEY,
    sigla       CHAR(2)     NOT NULL UNIQUE,
    nome        VARCHAR(50) NOT NULL
);

CREATE TABLE cidades (
    id_cidade   SERIAL PRIMARY KEY,
    nome        VARCHAR(100) NOT NULL,
    id_estado   INTEGER NOT NULL REFERENCES estados (id_estado),
    UNIQUE (nome, id_estado)
);

-- ============================
-- Tabelas de domínio (lookup)
-- ============================

CREATE TABLE categorias (
    id_categoria SERIAL PRIMARY KEY,
    nome         VARCHAR(50) NOT NULL UNIQUE,
    descricao    TEXT
);

CREATE TABLE origem_avaliacao (
    id_origem SERIAL PRIMARY KEY,
    nome      VARCHAR(50) NOT NULL UNIQUE
);

-- ============================
-- Entidade principal: Clientes
-- ============================

CREATE TABLE clientes (
    id_cliente  SERIAL PRIMARY KEY,
    nome        VARCHAR(150) NOT NULL,
    cpf         CHAR(11)     NOT NULL UNIQUE,
    email       VARCHAR(150) NOT NULL,
    telefone    VARCHAR(20),
    cep         CHAR(8),
    id_cidade   INTEGER REFERENCES cidades (id_cidade),  -- nullable: ver docs/data_model_relational.md, decisão 2
    created_at  TIMESTAMP NOT NULL DEFAULT now(),
    updated_at  TIMESTAMP NOT NULL DEFAULT now()
);

-- ============================
-- Entidade principal: Avaliações
-- ============================

CREATE TABLE avaliacoes (
    id_avaliacao   SERIAL PRIMARY KEY,
    id_cliente     INTEGER NOT NULL REFERENCES clientes (id_cliente),
    id_categoria   INTEGER NOT NULL REFERENCES categorias (id_categoria),
    id_origem      INTEGER NOT NULL REFERENCES origem_avaliacao (id_origem),
    nota           SMALLINT NOT NULL CHECK (nota BETWEEN 1 AND 5),
    comentario     TEXT,  -- nullable: ver docs/data_model_relational.md, decisão 3
    data_avaliacao DATE NOT NULL,
    created_at     TIMESTAMP NOT NULL DEFAULT now()
    -- Sem constraint de deduplicação aqui: ver docs/data_model_relational.md, decisão 4
);

-- ============================
-- Índices
-- ============================

CREATE INDEX idx_avaliacoes_cliente ON avaliacoes (id_cliente);
CREATE INDEX idx_avaliacoes_data    ON avaliacoes (data_avaliacao);

-- ============================
-- Trigger: updated_at automático em clientes
-- ============================

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_clientes_updated_at
BEFORE UPDATE ON clientes
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

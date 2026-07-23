-- ============================================================================
-- Customer Insight Platform — Schema do Banco Operacional (PostgreSQL/Supabase)
-- Fase 1 — Modelagem de Dados / Fase 2 — Implementação
-- Documentação completa: docs/data_model_relational.md
-- ============================================================================

CREATE TABLE estados (
    id_estado   SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sigla       CHAR(2) NOT NULL UNIQUE,
    nome        VARCHAR(50) NOT NULL
);

CREATE TABLE cidades (
    id_cidade   INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome        VARCHAR(100) NOT NULL,
    id_estado   SMALLINT NOT NULL REFERENCES estados(id_estado),
    UNIQUE (nome, id_estado)
);

CREATE TABLE categorias (
    id_categoria INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome         VARCHAR(60) NOT NULL UNIQUE
);

CREATE TABLE origens_avaliacao (
    id_origem   INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome        VARCHAR(60) NOT NULL UNIQUE
);

CREATE TABLE clientes (
    id_cliente  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome        VARCHAR(150) NOT NULL,
    cpf         CHAR(11) UNIQUE,             -- validação de dígito verificador fica na aplicação
    email       VARCHAR(150),
    telefone    VARCHAR(20),
    id_cidade   INTEGER REFERENCES cidades(id_cidade),  -- opcional, resolvido via ViaCEP
    natureza_registro VARCHAR(20) NOT NULL DEFAULT 'Real'
        CHECK (natureza_registro IN ('Sintético', 'Real')),  -- ver ADR-003
    criado_em   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ----------------------------------------------------------------------------
-- avaliacoes: id_cliente e id_categoria são OPCIONAIS.
-- Cada origem entrega um subconjunto diferente de campos (ver
-- docs/data_model_relational.md, seção "Preenchimento por origem"):
--   Formulário Web            -> cliente conhecido, categoria conhecida, comentário opcional
--   Pinpad - Atendente        -> cliente NULL, categoria conhecida (fixa por guichê), sem comentário
--   Totem - Autoatendimento   -> cliente NULL, categoria NULL, sem comentário
--   Scraping                  -> cliente NULL, categoria NULL, comentário conhecido
--   Telemarketing - Pesquisa  -> cliente conhecido, categoria conhecida, sem comentário (ADR-004)
-- id_origem é a única FK sempre obrigatória: o processo que grava sempre
-- sabe de onde o dado veio, independente da origem.
-- ----------------------------------------------------------------------------
CREATE TABLE avaliacoes (
    id_avaliacao   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_cliente     INTEGER REFERENCES clientes(id_cliente),
    id_categoria   INTEGER REFERENCES categorias(id_categoria),
    id_origem      INTEGER NOT NULL REFERENCES origens_avaliacao(id_origem),
    data_avaliacao DATE NOT NULL,
    nota           SMALLINT NOT NULL CHECK (nota BETWEEN 1 AND 5),
    comentario     TEXT,
    natureza_registro VARCHAR(20) NOT NULL DEFAULT 'Real'
        CHECK (natureza_registro IN ('Sintético', 'Real')),  -- ver ADR-003
    criado_em      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Índices para os padrões de consulta mais prováveis
CREATE INDEX idx_avaliacoes_cliente   ON avaliacoes(id_cliente);
CREATE INDEX idx_avaliacoes_categoria ON avaliacoes(id_categoria);
CREATE INDEX idx_avaliacoes_data      ON avaliacoes(data_avaliacao);
CREATE INDEX idx_clientes_cidade      ON clientes(id_cidade);

-- ============================================================================
-- Seed — origens_avaliacao (5 canais definidos até a Fase 2 — ver ADR-004)
-- ============================================================================
INSERT INTO origens_avaliacao (nome) VALUES
    ('Formulário Web'),
    ('Pinpad - Atendente'),
    ('Totem - Autoatendimento'),
    ('Scraping'),
    ('Telemarketing - Pesquisa Pós-Atendimento');

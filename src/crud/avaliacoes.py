"""
CRUD de avaliações — ponto único de escrita na tabela `avaliacoes`,
reutilizado pelos 4 routers de origem (Formulário Web, Pinpad, Totem,
Telemarketing).

Centralizar aqui evita duplicar, em cada router, a regra de "quais campos
são opcionais por origem" — já documentada em docs/data_model_relational.md,
seção "Preenchimento por origem".
"""

from datetime import date
from typing import Optional

from pg8000.dbapi import Connection


def buscar_id_origem(conn: Connection, nome_origem: str) -> int:
    """Resolve id_origem a partir do nome (catálogo fixo, 5 linhas)."""
    with conn.cursor() as cur:
        cur.execute("SELECT id_origem FROM origens_avaliacao WHERE nome = %s", (nome_origem,))
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"Origem '{nome_origem}' não cadastrada em origens_avaliacao.")
        return row[0]


def buscar_id_categoria(conn: Connection, nome_categoria: str) -> int:
    """Resolve id_categoria a partir do nome (catálogo fixo, 6 linhas)."""
    with conn.cursor() as cur:
        cur.execute("SELECT id_categoria FROM categorias WHERE nome = %s", (nome_categoria,))
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"Categoria '{nome_categoria}' não cadastrada.")
        return row[0]


def buscar_ou_criar_cliente(
    conn: Connection,
    nome: str,
    cpf: str,
    email: Optional[str] = None,
    telefone: Optional[str] = None,
) -> int:
    """
    Usado pelo Formulário Web: se o CPF já existir, reaproveita o cliente
    (histórico/recorrência), evitando duplicidade; senão, cria um novo.

    id_cidade não é resolvido aqui (fica NULL) — enriquecimento via CEP faz
    parte da Fase 6/7 (ETL/Engenharia de Dados), fora do escopo de Create
    da Fase 5.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT id_cliente FROM clientes WHERE cpf = %s", (cpf,))
        row = cur.fetchone()
        if row is not None:
            return row[0]

        cur.execute(
            """
            INSERT INTO clientes (nome, cpf, email, telefone, natureza_registro)
            VALUES (%s, %s, %s, %s, 'Real')
            RETURNING id_cliente
            """,
            (nome, cpf, email, telefone),
        )
        return cur.fetchone()[0]


def inserir_avaliacao(
    conn: Connection,
    id_origem: int,
    nota: int,
    id_cliente: Optional[int] = None,
    id_categoria: Optional[int] = None,
    comentario: Optional[str] = None,
    data_avaliacao: Optional[date] = None,
) -> int:
    """
    Insere uma avaliação e devolve o id_avaliacao gerado.

    id_cliente, id_categoria e comentario são opcionais — cada router de
    origem passa apenas o que sua fonte real produz (ver
    docs/data_model_relational.md). natureza_registro é sempre 'Real' aqui:
    dado 'Sintético' só é gerado pelo seed de desenvolvimento (ADR-003).
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO avaliacoes
                (id_cliente, id_categoria, id_origem, data_avaliacao, nota, comentario, natureza_registro)
            VALUES (%s, %s, %s, %s, %s, %s, 'Real')
            RETURNING id_avaliacao
            """,
            (id_cliente, id_categoria, id_origem, data_avaliacao or date.today(), nota, comentario),
        )
        return cur.fetchone()[0]

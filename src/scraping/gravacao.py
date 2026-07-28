"""
Gravação em `avaliacoes`, isolada do backend (crud/avaliacoes.py) — ver
ADR-011 (docs/decisions/011-scraper-gravacao-propria-desacoplada.md).

O scraper não reaproveita a camada de escrita do FastAPI: usa sua própria
conexão (conexao.py) e seu próprio INSERT, simulando um processo de
scraping real, potencialmente rodando fora do codebase da aplicação
principal.
"""
from datetime import date

from pg8000 import Connection


def obter_id_origem_scraping(conn: Connection) -> int:
    """
    Busca o id_origem de 'Scraping' dinamicamente — nunca hardcoded, já
    que surrogate keys do Postgres não são garantidas entre ambientes
    (dev, Codespaces, produção futura).
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id_origem FROM origens_avaliacao WHERE nome = %s", ("Scraping",)
    )
    linha = cursor.fetchone()
    if linha is None:
        raise RuntimeError(
            "Origem 'Scraping' não encontrada em origens_avaliacao — "
            "verifique se o schema.sql foi aplicado com o seed de origens."
        )
    return linha[0]


def inserir_avaliacao_scraping(
    conn: Connection,
    id_origem: int,
    data_avaliacao: date,
    nota: int,
    comentario: str,
) -> None:
    """
    Insere uma avaliação vinda do scraping.

    id_cliente e id_categoria ficam NULL — a origem Scraping não produz
    esses dados (ver tabela "Preenchimento por origem" em
    data_model_relational.md). natureza_registro é 'Real' — o scraper é
    um sistema de captura de produção genuíno, igual a Formulário
    Web/Pinpad/Totem (ver ADR-003 e ADR-013; revisa o que o ADR-010
    havia registrado sobre este campo especificamente).
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO avaliacoes
            (id_cliente, id_categoria, id_origem, data_avaliacao, nota, comentario, natureza_registro)
        VALUES
            (NULL, NULL, %s, %s, %s, %s, 'Real')
        """,
        (id_origem, data_avaliacao, nota, comentario),
    )


def gravar_lote(conn: Connection, avaliacoes: list[dict]) -> int:
    """
    Grava uma lista de avaliações já tratadas (ver tratamento.py) em uma
    única transação. Retorna a quantidade de linhas inseridas.

    Nota sobre reexecução: não há verificação de duplicidade aqui — em
    linha com a decisão já registrada no projeto (ADR-002: deduplicação é
    responsabilidade da camada Silver, não do Postgres operacional).
    Rodar o script duas vezes duplica os registros; se necessário, limpe
    o lote anterior antes:
        DELETE FROM avaliacoes
        WHERE id_origem = (SELECT id_origem FROM origens_avaliacao WHERE nome = 'Scraping')
          AND natureza_registro = 'Real';
    """
    id_origem = obter_id_origem_scraping(conn)
    for item in avaliacoes:
        inserir_avaliacao_scraping(
            conn,
            id_origem=id_origem,
            data_avaliacao=item["data_avaliacao"],
            nota=item["nota"],
            comentario=item["comentario"],
        )
    conn.commit()
    return len(avaliacoes)
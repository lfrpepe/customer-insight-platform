"""Router do Pinpad — Create de avaliação (anônima, categoria selecionada pelo operador)."""

from fastapi import APIRouter, Depends, HTTPException
from pg8000.dbapi import Connection

from src.crud.avaliacoes import buscar_id_categoria, buscar_id_origem, inserir_avaliacao
from src.database.connection import get_connection
from src.schemas.avaliacao_pinpad import AvaliacaoPinpadCreate

router = APIRouter(prefix="/avaliacoes/pinpad", tags=["Pinpad"])

NOME_ORIGEM = "Pinpad - Atendente"


@router.post("", status_code=201)
def criar_avaliacao(payload: AvaliacaoPinpadCreate, conn: Connection = Depends(get_connection)) -> dict:
    try:
        id_origem = buscar_id_origem(conn, NOME_ORIGEM)
        id_categoria = buscar_id_categoria(conn, payload.categoria)
        id_avaliacao = inserir_avaliacao(
            conn,
            id_origem=id_origem,
            nota=payload.nota,
            id_categoria=id_categoria,
        )
    except ValueError as erro:
        raise HTTPException(status_code=422, detail=str(erro))

    return {"id_avaliacao": id_avaliacao}

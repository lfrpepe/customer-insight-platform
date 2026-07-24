"""Router do Totem — Create de avaliação (anônima, sem categoria)."""

from fastapi import APIRouter, Depends, HTTPException
from pg8000.dbapi import Connection

from src.crud.avaliacoes import buscar_id_origem, inserir_avaliacao
from src.database.connection import get_connection
from src.schemas.avaliacao_totem import AvaliacaoTotemCreate

router = APIRouter(prefix="/avaliacoes/totem", tags=["Totem"])

NOME_ORIGEM = "Totem - Autoatendimento"


@router.post("", status_code=201)
def criar_avaliacao(payload: AvaliacaoTotemCreate, conn: Connection = Depends(get_connection)) -> dict:
    try:
        id_origem = buscar_id_origem(conn, NOME_ORIGEM)
        id_avaliacao = inserir_avaliacao(conn, id_origem=id_origem, nota=payload.nota)
    except ValueError as erro:
        raise HTTPException(status_code=422, detail=str(erro))

    return {"id_avaliacao": id_avaliacao}

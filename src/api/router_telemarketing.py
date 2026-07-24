"""Router da integração Telemarketing — Create de avaliação (ADR-004)."""

from fastapi import APIRouter, Depends, HTTPException
from pg8000.dbapi import Connection

from src.crud.avaliacoes import buscar_id_origem, inserir_avaliacao
from src.database.connection import get_connection
from src.schemas.avaliacao_telemarketing import AvaliacaoTelemarketingCreate

router = APIRouter(prefix="/avaliacoes/telemarketing", tags=["Telemarketing"])

NOME_ORIGEM = "Telemarketing - Pesquisa Pós-Atendimento"


@router.post("", status_code=201)
def criar_avaliacao(payload: AvaliacaoTelemarketingCreate, conn: Connection = Depends(get_connection)) -> dict:
    try:
        id_origem = buscar_id_origem(conn, NOME_ORIGEM)
        id_avaliacao = inserir_avaliacao(
            conn,
            id_origem=id_origem,
            nota=payload.nota,
            id_cliente=payload.id_cliente,
            id_categoria=payload.id_categoria,
        )
    except ValueError as erro:
        raise HTTPException(status_code=422, detail=str(erro))

    return {"id_avaliacao": id_avaliacao}

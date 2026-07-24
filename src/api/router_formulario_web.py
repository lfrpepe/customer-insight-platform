"""Router do Formulário Web — Create de avaliação (cliente + categoria + comentário opcional)."""

from fastapi import APIRouter, Depends, HTTPException
from pg8000.dbapi import Connection

from src.crud.avaliacoes import buscar_id_categoria, buscar_id_origem, buscar_ou_criar_cliente, inserir_avaliacao
from src.database.connection import get_connection
from src.schemas.avaliacao_formulario_web import AvaliacaoFormularioWebCreate

router = APIRouter(prefix="/avaliacoes/formulario-web", tags=["Formulário Web"])

NOME_ORIGEM = "Formulário Web"


@router.post("", status_code=201)
def criar_avaliacao(payload: AvaliacaoFormularioWebCreate, conn: Connection = Depends(get_connection)) -> dict:
    try:
        id_origem = buscar_id_origem(conn, NOME_ORIGEM)
        id_categoria = buscar_id_categoria(conn, payload.categoria)
        id_cliente = buscar_ou_criar_cliente(
            conn,
            nome=payload.nome_cliente,
            cpf=payload.cpf,
            email=payload.email,
            telefone=payload.telefone,
        )
        id_avaliacao = inserir_avaliacao(
            conn,
            id_origem=id_origem,
            nota=payload.nota,
            id_cliente=id_cliente,
            id_categoria=id_categoria,
            comentario=payload.comentario,
        )
    except ValueError as erro:
        raise HTTPException(status_code=422, detail=str(erro))

    return {"id_avaliacao": id_avaliacao}

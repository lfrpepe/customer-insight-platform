"""
Schema de entrada do Pinpad — Create de avaliação.

Sem dados de cliente (avaliação anônima). A categoria é selecionada pelo
próprio operador de caixa no momento do atendimento presencial — não há
guichês distintos com categoria pré-fixada (única forma de captura
presencial do projeto), então o campo é igual ao do Formulário Web: nome
da categoria, validado contra `categorias` no banco.
"""

from pydantic import BaseModel, Field


class AvaliacaoPinpadCreate(BaseModel):
    categoria: str
    nota: int = Field(ge=1, le=5)

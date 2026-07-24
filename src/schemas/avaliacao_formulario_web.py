"""
Schema de entrada do Formulário Web — Create de avaliação.

Única origem com todos os campos preenchidos: cliente identificado (CPF),
categoria escolhida e comentário opcional (ver docs/data_model_relational.md).
"""

import re
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.validators.cliente import cpf_valido, telefone_normalizado


class AvaliacaoFormularioWebCreate(BaseModel):
    nome_cliente: str = Field(min_length=1, max_length=150)
    cpf: str
    email: Optional[EmailStr] = None
    telefone: Optional[str] = Field(default=None, max_length=20)
    categoria: str
    nota: int = Field(ge=1, le=5)
    comentario: Optional[str] = None

    @field_validator("cpf")
    @classmethod
    def valida_cpf(cls, v: str) -> str:
        """Remove formatação (pontos/traço) e valida o dígito verificador."""
        apenas_digitos = re.sub(r"\D", "", v)
        if not cpf_valido(apenas_digitos):
            raise ValueError("CPF inválido.")
        return apenas_digitos

    @field_validator("telefone")
    @classmethod
    def valida_telefone(cls, v: Optional[str]) -> Optional[str]:
        """Normaliza para somente dígitos (DDD+número) — mesmo padrão do CPF."""
        if v is None:
            return v
        return telefone_normalizado(v)

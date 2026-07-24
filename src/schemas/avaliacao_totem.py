"""
Schema de entrada do Totem — Create de avaliação.

Sem cliente, sem categoria — apenas a nota (autoatendimento genérico, ver
docs/data_model_relational.md).
"""

from pydantic import BaseModel, Field


class AvaliacaoTotemCreate(BaseModel):
    nota: int = Field(ge=1, le=5)

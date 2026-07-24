"""
Schema de entrada da integração Telemarketing — Create de avaliação (ADR-004).

Origem interna, não um formulário público: o sistema de discagem já liga
sabendo quem é o cliente e qual foi o atendimento (dados vindos do CRM que
originou a ligação), por isso chegam aqui como IDs já resolvidos — nunca
como dado bruto de cliente. Nunca há comentário: o IVR só captura o dígito
da nota.
"""

from pydantic import BaseModel, Field


class AvaliacaoTelemarketingCreate(BaseModel):
    id_cliente: int
    id_categoria: int
    nota: int = Field(ge=1, le=5)

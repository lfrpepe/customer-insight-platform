"""Validações de regra de negócio que o Pydantic não cobre nativamente."""

import re


def cpf_valido(cpf: str) -> bool:
    """
    Valida o dígito verificador do CPF (algoritmo padrão da Receita Federal).

    Recebe apenas dígitos (11 caracteres) — a limpeza de formatação
    (pontos/traço) é responsabilidade do schema Pydantic antes de chamar
    esta função (ver `src/schemas/avaliacao_formulario_web.py`).
    """
    if len(cpf) != 11 or not cpf.isdigit() or cpf == cpf[0] * 11:
        return False

    def _digito_verificador(cpf_parcial: str) -> int:
        peso_inicial = len(cpf_parcial) + 1
        soma = sum(int(digito) * (peso_inicial - i) for i, digito in enumerate(cpf_parcial))
        resto = (soma * 10) % 11
        return 0 if resto == 10 else resto

    digito_1 = _digito_verificador(cpf[:9])
    digito_2 = _digito_verificador(cpf[:9] + str(digito_1))
    return cpf[-2:] == f"{digito_1}{digito_2}"


def telefone_normalizado(telefone: str) -> str:
    """
    Normaliza para o único formato de telefone do projeto: apenas dígitos
    (DDD + número, sem parênteses/traço/espaço) — mesmo padrão adotado
    para o CPF. Mais simples para busca/deduplicação e evita reprocessar
    formatação nas camadas seguintes (ETL, BI); formatação para exibição,
    se necessária, fica a cargo da camada de apresentação.

    Aceita qualquer entrada com 10 ou 11 dígitos, com ou sem formatação
    prévia (parênteses, traço, espaço); rejeita o resto.
    """
    digitos = re.sub(r"\D", "", telefone)

    if len(digitos) == 11:  # DDD + 9 + 8 dígitos (celular, já com o 9)
        return digitos
    if len(digitos) == 10:  # DDD + 8 dígitos (sem o 9 — normaliza incluindo)
        return digitos[:2] + "9" + digitos[2:]
    raise ValueError("Telefone deve ter 10 ou 11 dígitos, incluindo o DDD.")


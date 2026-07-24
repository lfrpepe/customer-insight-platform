"""Validações de regra de negócio que o Pydantic não cobre nativamente."""


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

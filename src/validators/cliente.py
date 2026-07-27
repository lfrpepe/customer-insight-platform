"""Validações de regra de negócio que o Pydantic não cobre nativamente."""

import re

# DDDs válidos no Brasil — mesma lista usada em
# `database/scripts/generate_seed_dev.py::gerar_telefone()`. Duplicada aqui
# de propósito (script de seed roda fora do pacote `src`, sem import direto
# simples); mantenha as duas listas sincronizadas se um DDD novo for criado.
DDDS_VALIDOS = {
    11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 24, 27, 28, 31, 32, 33, 34,
    35, 37, 38, 41, 42, 43, 44, 45, 46, 47, 48, 49, 51, 53, 54, 55, 61, 62,
    63, 64, 65, 66, 67, 68, 69, 71, 73, 74, 75, 77, 79, 81, 82, 83, 84, 85,
    86, 87, 88, 89, 91, 92, 93, 94, 95, 96, 97, 98, 99,
}

_TOKEN_NOME_REGEX = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ'’\-]+$")


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


def nome_completo_valido(nome: str) -> str:
    """
    Exige nome e sobrenome (pelo menos 2 palavras) e rejeita números —
    o Pydantic sozinho só garante que é uma string, não o formato.

    Aceita letras acentuadas, hífen e apóstrofo (ex.: "Jean-Pierre",
    "D'Ávila"); normaliza espaços duplicados/nas pontas.

    Devolve o nome normalizado; levanta ValueError se inválido.
    """
    normalizado = " ".join(nome.split())
    partes = normalizado.split(" ")

    if len(partes) < 2:
        raise ValueError("Informe nome e sobrenome (nome completo).")
    if not all(_TOKEN_NOME_REGEX.match(parte) for parte in partes):
        raise ValueError("Nome deve conter apenas letras, sem números.")

    return normalizado


def telefone_normalizado(telefone: str) -> str:
    """
    Normaliza para o único formato de telefone do projeto: apenas dígitos
    (DDD + número, sem parênteses/traço/espaço) — mesmo padrão adotado
    para o CPF. Mais simples para busca/deduplicação e evita reprocessar
    formatação nas camadas seguintes (ETL, BI); formatação para exibição,
    se necessária, fica a cargo da camada de apresentação.

    Além do formato, valida minimamente que não é um número óbvio
    inventado (DDD inexistente, sem o "9" de celular, dígitos todos
    repetidos) — não substitui uma verificação real de operadora, mas
    barra os casos mais grosseiros de dado de teste digitado às pressas.
    """
    digitos = re.sub(r"\D", "", telefone)

    if len(digitos) == 10:  # DDD + 8 dígitos (sem o 9 — normaliza incluindo)
        digitos = digitos[:2] + "9" + digitos[2:]

    if len(digitos) != 11:
        raise ValueError("Telefone deve ter 10 ou 11 dígitos, incluindo o DDD.")

    ddd = int(digitos[:2])
    numero = digitos[2:]

    if ddd not in DDDS_VALIDOS:
        raise ValueError(f"DDD {ddd} não é válido.")
    if numero[0] != "9":
        raise ValueError("Celular deve começar com 9 logo após o DDD.")
    if len(set(numero)) == 1:
        raise ValueError("Telefone inválido (dígitos repetidos).")

    return digitos



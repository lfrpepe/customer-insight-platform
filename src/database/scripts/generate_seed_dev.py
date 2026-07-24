"""
Gerador de dados de desenvolvimento — Customer Insight Platform

Conecta diretamente no banco operacional (Supabase/PostgreSQL) e grava os
dados fictícios gerados com Faker — sem precisar de arquivos .sql
intermediários (ver ADR-005, atualizado: `pg8000` em vez de `psycopg2`,
por ser Python puro e não exigir compilação/pg_config no sistema local).

Como usar:
    1. pip install -r requirements.txt
    2. Copie .env.example para .env e preencha com os dados de conexão do
       Supabase (Project Settings > Database > Connection string > Session pooler)
    3. python src/database/scripts/generate_seed_dev.py

Pré-requisito: schema.sql já executado (tabelas + seed de origens_avaliacao).
Reexecutável: cada execução gera uma nova amostra de dados (ver random.seed
abaixo se quiser resultados reproduzíveis) e insere linhas ADICIONAIS —
não apaga dados existentes. Se quiser recomeçar do zero, rode o DROP/recreate
do schema.sql antes.
"""

import os
import random
import unicodedata
from datetime import datetime, timedelta

import pg8000
from dotenv import load_dotenv
from faker import Faker

load_dotenv()

fake = Faker("pt_BR")
random.seed(42)  # reprodutibilidade — remova esta linha para uma amostra diferente a cada execução

# ============================================================================
# Configuração
# ============================================================================

QTD_CLIENTES = 500
QTD_AVALIACOES = 5000
DIAS_JANELA = 365  # últimos 12 meses

DISTRIBUICAO_ORIGEM = {
    "Formulário Web": 0.28,
    "Pinpad - Atendente": 0.25,
    "Totem - Autoatendimento": 0.17,
    "Telemarketing - Pesquisa Pós-Atendimento": 0.18,
    "Scraping": 0.12,
}

ORIGENS_COM_CLIENTE_CONHECIDO = {"Formulário Web", "Telemarketing - Pesquisa Pós-Atendimento"}

DISTRIBUICAO_NOTA = {5: 0.30, 4: 0.30, 3: 0.20, 2: 0.12, 1: 0.08}

PERSONAS = {
    "insatisfeito_cronico": {1: 0.45, 2: 0.30, 3: 0.15, 4: 0.07, 5: 0.03},
    "neutro":               {5: 0.30, 4: 0.30, 3: 0.20, 2: 0.12, 1: 0.08},
    "satisfeito_fiel":      {5: 0.55, 4: 0.30, 3: 0.10, 2: 0.03, 1: 0.02},
}
DISTRIBUICAO_PERSONAS = {"insatisfeito_cronico": 0.15, "neutro": 0.65, "satisfeito_fiel": 0.20}

# ============================================================================
# Estados e cidades
# ============================================================================

ESTADOS = [
    ("AC", "Acre"), ("AL", "Alagoas"), ("AP", "Amapá"), ("AM", "Amazonas"),
    ("BA", "Bahia"), ("CE", "Ceará"), ("DF", "Distrito Federal"),
    ("ES", "Espírito Santo"), ("GO", "Goiás"), ("MA", "Maranhão"),
    ("MT", "Mato Grosso"), ("MS", "Mato Grosso do Sul"), ("MG", "Minas Gerais"),
    ("PA", "Pará"), ("PB", "Paraíba"), ("PR", "Paraná"), ("PE", "Pernambuco"),
    ("PI", "Piauí"), ("RJ", "Rio de Janeiro"), ("RN", "Rio Grande do Norte"),
    ("RS", "Rio Grande do Sul"), ("RO", "Rondônia"), ("RR", "Roraima"),
    ("SC", "Santa Catarina"), ("SP", "São Paulo"), ("SE", "Sergipe"),
    ("TO", "Tocantins"),
]

CIDADES_POR_ESTADO = {
    "AC": ["Rio Branco", "Cruzeiro do Sul"], "AL": ["Maceió", "Arapiraca"],
    "AP": ["Macapá", "Santana"], "AM": ["Manaus", "Parintins"],
    "BA": ["Salvador", "Feira de Santana"], "CE": ["Fortaleza", "Juazeiro do Norte"],
    "DF": ["Brasília", "Ceilândia"], "ES": ["Vitória", "Vila Velha"],
    "GO": ["Goiânia", "Anápolis"], "MA": ["São Luís", "Imperatriz"],
    "MT": ["Cuiabá", "Rondonópolis"], "MS": ["Campo Grande", "Dourados"],
    "MG": ["Belo Horizonte", "Uberlândia"], "PA": ["Belém", "Ananindeua"],
    "PB": ["João Pessoa", "Campina Grande"], "PR": ["Curitiba", "Londrina"],
    "PE": ["Recife", "Caruaru"], "PI": ["Teresina", "Parnaíba"],
    "RJ": ["Rio de Janeiro", "Niterói"], "RN": ["Natal", "Mossoró"],
    "RS": ["Porto Alegre", "Caxias do Sul"], "RO": ["Porto Velho", "Ji-Paraná"],
    "RR": ["Boa Vista", "Rorainópolis"], "SC": ["Florianópolis", "Joinville"],
    "SP": ["São Paulo", "Campinas"], "SE": ["Aracaju", "Nossa Senhora do Socorro"],
    "TO": ["Palmas", "Araguaína"],
}

CATEGORIAS = [
    "Suporte Técnico", "Financeiro", "Entrega",
    "Atendimento Geral", "Cancelamento", "Elogio",
]

COMENTARIOS_NEGATIVOS = [
    "Fui muito mal atendido, demorou mais de uma hora para resolver algo simples.",
    "Péssima experiência, ninguém sabia me explicar o motivo da cobrança extra.",
    "Já é a terceira vez que reclamo do mesmo problema e nada é resolvido.",
    "Atendimento horrível, o atendente foi grosseiro e não resolveu nada.",
    "Extremamente insatisfeito, produto chegou danificado e o suporte não ajudou.",
    "Não recomendo, fiquei muito tempo esperando resposta e desisti.",
    "Serviço muito abaixo do esperado, várias tentativas sem solução.",
    "Fui mal informado sobre o prazo e isso me causou prejuízo.",
    "Cancelaram meu pedido sem aviso, muito decepcionante.",
    "O sistema caiu no meio do atendimento e tive que recomeçar tudo.",
]
COMENTARIOS_NEUTROS = [
    "Atendimento dentro do esperado, sem grandes problemas.",
    "Resolveram minha solicitação, mas demorou um pouco mais que o normal.",
    "Foi ok, nada excepcional, mas também não tenho reclamações.",
    "Atendente foi educado, resolveu a maior parte do meu problema.",
    "Experiência mediana, funcionou mas poderia ser mais rápido.",
    "Sem grandes elogios ou críticas, cumpriu o que prometeu.",
]
COMENTARIOS_POSITIVOS = [
    "Excelente atendimento, resolveram meu problema rapidamente!",
    "Muito satisfeito, o atendente foi atencioso e claro nas explicações.",
    "Ótima experiência, recomendo o serviço para todos.",
    "Fui muito bem tratado, superou minhas expectativas.",
    "Suporte rápido e eficiente, parabéns pela equipe.",
    "Adorei o atendimento, resolveram tudo em poucos minutos.",
    "Muito bom, equipe atenciosa e prestativa do início ao fim.",
    "Fiquei impressionado com a agilidade na resolução do meu chamado.",
    "Sempre que preciso, sou bem atendido. Excelente serviço.",
    "Melhor experiência de atendimento que já tive com uma empresa.",
]


def comentario_por_nota(nota: int) -> str:
    if nota <= 2:
        return random.choice(COMENTARIOS_NEGATIVOS)
    if nota == 3:
        return random.choice(COMENTARIOS_NEUTROS)
    return random.choice(COMENTARIOS_POSITIVOS)


def data_aleatoria():
    return datetime.now().date() - timedelta(days=random.randint(0, DIAS_JANELA))


def sortear_nota() -> int:
    notas, pesos = zip(*DISTRIBUICAO_NOTA.items())
    return random.choices(notas, weights=pesos, k=1)[0]


def sortear_nota_por_persona(persona: str) -> int:
    notas, pesos = zip(*PERSONAS[persona].items())
    return random.choices(notas, weights=pesos, k=1)[0]


def sortear_persona() -> str:
    personas, pesos = zip(*DISTRIBUICAO_PERSONAS.items())
    return random.choices(personas, weights=pesos, k=1)[0]


# DDDs válidos no Brasil (todos os estados) — usados para gerar telefones
# padronizados, evitando a inconsistência de formato do fake.phone_number()
# (que mistura com/sem DDD e com/sem código de país aleatoriamente).
DDDS_VALIDOS = [
    11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 24, 27, 28, 31, 32, 33, 34,
    35, 37, 38, 41, 42, 43, 44, 45, 46, 47, 48, 49, 51, 53, 54, 55, 61, 62,
    63, 64, 65, 66, 67, 68, 69, 71, 73, 74, 75, 77, 79, 81, 82, 83, 84, 85,
    86, 87, 88, 89, 91, 92, 93, 94, 95, 96, 97, 98, 99,
]


def gerar_telefone() -> str:
    """
    Celular brasileiro (DDD + 9 dígitos), somente dígitos — sem formatação
    (parênteses/traço), mesmo padrão usado pelo backend (Fase 5, ver
    `src/validators/cliente.py::telefone_normalizado`). Formatação para
    exibição, se necessária, fica a cargo da camada de apresentação.
    """
    ddd = random.choice(DDDS_VALIDOS)
    parte1 = random.randint(0, 9999)
    parte2 = random.randint(0, 9999)
    return f"{ddd}9{parte1:04d}{parte2:04d}"


DOMINIOS_EMAIL = ["gmail.com", "hotmail.com", "outlook.com", "yahoo.com.br"]


def gerar_email(nome: str, emails_usados: set) -> str:
    """
    Deriva o e-mail do próprio nome (ex.: "Maite Souza" -> "maite.souza@...") —
    diferente de fake.unique.email(), que gera algo desconectado do nome.
    """
    sem_acento = unicodedata.normalize("NFKD", nome.lower()).encode("ascii", "ignore").decode("ascii")
    partes = [p for p in sem_acento.replace("'", "").split() if p.isalpha()]
    base = f"{partes[0]}.{partes[-1]}" if len(partes) > 1 else (partes[0] if partes else "cliente")

    dominio = random.choice(DOMINIOS_EMAIL)
    email = f"{base}@{dominio}"
    sufixo = 1
    while email in emails_usados:
        sufixo += 1
        email = f"{base}{sufixo}@{dominio}"
    emails_usados.add(email)
    return email


# ============================================================================
# Conexão
# ============================================================================

def conectar():
    """
    Lê as credenciais do .env (nunca hardcoded — repositório é público).
    Variáveis esperadas: SUPABASE_DB_HOST, SUPABASE_DB_PORT, SUPABASE_DB_NAME,
    SUPABASE_DB_USER, SUPABASE_DB_PASSWORD.
    """
    return pg8000.connect(
        host=os.environ["SUPABASE_DB_HOST"],
        port=int(os.environ.get("SUPABASE_DB_PORT", "5432")),
        database=os.environ.get("SUPABASE_DB_NAME", "postgres"),
        user=os.environ["SUPABASE_DB_USER"],
        password=os.environ["SUPABASE_DB_PASSWORD"],
    )


# ============================================================================
# Inserção — cada função grava uma tabela e devolve os IDs reais gerados
# (via RETURNING), eliminando a necessidade de subqueries no SQL.
# ============================================================================

def inserir_estados(cur) -> dict:
    ids = {}
    for sigla, nome in ESTADOS:
        cur.execute(
            "INSERT INTO estados (sigla, nome) VALUES (%s, %s) RETURNING id_estado",
            (sigla, nome),
        )
        ids[sigla] = cur.fetchone()[0]
    return ids


def inserir_cidades(cur, ids_estados: dict) -> dict:
    ids = {}
    for sigla, _ in ESTADOS:
        for nome_cidade in CIDADES_POR_ESTADO[sigla]:
            cur.execute(
                "INSERT INTO cidades (nome, id_estado) VALUES (%s, %s) RETURNING id_cidade",
                (nome_cidade, ids_estados[sigla]),
            )
            ids[(nome_cidade, sigla)] = cur.fetchone()[0]
    return ids


def inserir_categorias(cur) -> dict:
    ids = {}
    for nome in CATEGORIAS:
        cur.execute(
            "INSERT INTO categorias (nome) VALUES (%s) RETURNING id_categoria", (nome,)
        )
        ids[nome] = cur.fetchone()[0]
    return ids


def obter_origens(cur) -> dict:
    """origens_avaliacao já é populada pelo schema.sql — só lemos os IDs."""
    cur.execute("SELECT id_origem, nome FROM origens_avaliacao")
    return {nome: id_origem for id_origem, nome in cur.fetchall()}


def inserir_clientes(cur, ids_cidades: dict):
    """Retorna (lista de id_cliente na ordem de inserção, lista de persona por cliente)."""
    ids_clientes = []
    personas = []
    lista_cidades = list(ids_cidades.keys())
    cpfs_usados = set()
    emails_usados = set()

    for _ in range(QTD_CLIENTES):
        nome = fake.name()
        cpf = fake.cpf().replace(".", "").replace("-", "")
        while cpf in cpfs_usados:
            cpf = fake.cpf().replace(".", "").replace("-", "")
        cpfs_usados.add(cpf)
        email = gerar_email(nome, emails_usados)
        telefone = gerar_telefone()

        id_cidade = None
        if random.random() < 0.70:
            nome_cidade, sigla = random.choice(lista_cidades)
            id_cidade = ids_cidades[(nome_cidade, sigla)]

        cur.execute(
            """INSERT INTO clientes (nome, cpf, email, telefone, id_cidade, natureza_registro)
               VALUES (%s, %s, %s, %s, %s, 'Sintético') RETURNING id_cliente""",
            (nome, cpf, email, telefone, id_cidade),
        )
        ids_clientes.append(cur.fetchone()[0])
        personas.append(sortear_persona())

    return ids_clientes, personas


def gerar_linhas_avaliacoes(ids_clientes, personas, ids_categorias, ids_origens):
    """Gera as linhas em memória (lista de tuplas) — inserção em lote depois."""
    origens, pesos_origem = zip(*DISTRIBUICAO_ORIGEM.items())
    # Pareto calibrado (alpha=3.5): concentração realista, sem picos absurdos
    # (ver ADR sobre calibração no status.md)
    pesos_clientes = [random.paretovariate(3.5) for _ in ids_clientes]
    indices_clientes = list(range(len(ids_clientes)))

    linhas = []
    for _ in range(QTD_AVALIACOES):
        origem = random.choices(origens, weights=pesos_origem, k=1)[0]
        data = data_aleatoria()
        id_origem = ids_origens[origem]

        if origem in ORIGENS_COM_CLIENTE_CONHECIDO:
            idx = random.choices(indices_clientes, weights=pesos_clientes, k=1)[0]
            id_cliente = ids_clientes[idx]
            nota = sortear_nota_por_persona(personas[idx])
            id_categoria = ids_categorias[random.choice(CATEGORIAS)]
            comentario = None
            if origem == "Formulário Web" and random.random() < 0.5:
                comentario = comentario_por_nota(nota)

        elif origem == "Pinpad - Atendente":
            nota = sortear_nota()
            id_cliente = None
            id_categoria = ids_categorias[random.choice(CATEGORIAS)]
            comentario = None

        elif origem == "Totem - Autoatendimento":
            nota = sortear_nota()
            id_cliente = None
            id_categoria = None
            comentario = None

        else:  # Scraping
            nota = sortear_nota()
            id_cliente = None
            id_categoria = None
            comentario = comentario_por_nota(nota)

        linhas.append((id_cliente, id_categoria, id_origem, data, nota, comentario, "Sintético"))

    return linhas


def inserir_avaliacoes(cur, linhas, tamanho_lote: int = 500):
    """
    pg8000 não tem um helper equivalente ao execute_values do psycopg2;
    monta-se manualmente um INSERT multi-linha por lote (mesma ideia,
    mesma performance — um round-trip por lote, não por linha).
    """
    colunas = (
        "(id_cliente, id_categoria, id_origem, data_avaliacao, nota, "
        "comentario, natureza_registro)"
    )
    for inicio in range(0, len(linhas), tamanho_lote):
        lote = linhas[inicio: inicio + tamanho_lote]
        placeholders = ", ".join(["(%s, %s, %s, %s, %s, %s, %s)"] * len(lote))
        parametros = [valor for linha in lote for valor in linha]
        cur.execute(f"INSERT INTO avaliacoes {colunas} VALUES {placeholders}", parametros)


# ============================================================================
# Execução
# ============================================================================

def main():
    conn = conectar()
    try:
        with conn.cursor() as cur:
            print("Inserindo estados...")
            ids_estados = inserir_estados(cur)

            print("Inserindo cidades...")
            ids_cidades = inserir_cidades(cur, ids_estados)

            print("Inserindo categorias...")
            ids_categorias = inserir_categorias(cur)

            print("Lendo origens (já seedadas pelo schema.sql)...")
            ids_origens = obter_origens(cur)

            print(f"Inserindo {QTD_CLIENTES} clientes...")
            ids_clientes, personas = inserir_clientes(cur, ids_cidades)

            print(f"Gerando {QTD_AVALIACOES} avaliações em memória...")
            linhas_avaliacoes = gerar_linhas_avaliacoes(
                ids_clientes, personas, ids_categorias, ids_origens
            )

            print("Inserindo avaliações (em lote)...")
            inserir_avaliacoes(cur, linhas_avaliacoes)

        # COMMIT explícito — pg8000 tem autocommit=False por padrão, e o
        # close() da conexão NÃO comita a transação (diferente de alguns
        # outros drivers). Sem esta linha, tudo seria descartado ao fechar.
        conn.commit()

        print(
            f"\nConcluído: {len(ids_estados)} estados | {len(ids_cidades)} cidades | "
            f"{len(ids_categorias)} categorias | {len(ids_clientes)} clientes | "
            f"{len(linhas_avaliacoes)} avaliações."
        )
    except KeyError as e:
        print(f"\nErro: variável de ambiente {e} não encontrada. Confira seu arquivo .env "
              f"(veja .env.example para os nomes esperados).")
    except Exception:
        # Qualquer outro erro durante a transação: desfaz tudo, não deixa
        # dado parcial gravado (ex.: só metade das avaliações inseridas).
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()

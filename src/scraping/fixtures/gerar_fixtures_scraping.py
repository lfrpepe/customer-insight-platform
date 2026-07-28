"""
Gerador de fixtures HTML de scraping — script de DESENVOLVIMENTO, executado
uma única vez para produzir o "site" estático versionado no repositório
(src/scraping/fixtures/paginas_html/).

Não faz parte do fluxo de execução do scraper (coletor.py/parser.py/
executar_scraping.py) — equivalente, em espírito, ao
generate_seed_dev.py: gera dado sintético determinístico e reprodutível,
aqui como HTML/CSS/JS estático em vez de linhas de banco.

Todas as páginas de detalhe usam a MESMA estrutura HTML — o que muda é
só o dado. A única seção condicional é o bloco "resolvido"/"voltaria",
que só existe quando a avaliação foi respondida pela empresa (campo
`respondido`); isso é comportamento real do site simulado, não uma
inconsistência de template.

Uso:
    python src/scraping/fixtures/gerar_fixtures_scraping.py
"""
import random
from datetime import date, timedelta
from pathlib import Path

from faker import Faker

fake = Faker("pt_BR")
random.seed(42)  # reprodutibilidade — mesmo racional do generate_seed_dev.py

NOME_SITE = "ClienteFala"
NOME_EMPRESA = "Empresa Fictícia"

PAGINAS = 5
AVALIACOES_POR_PAGINA = 40
TAMANHO_SNIPPET = 130

PROB_ERRO_PALAVRAO = 0.10
PROB_EMOJI = 0.20
PROB_RESPONDIDO = 0.85

CIDADES_ESTADOS = [
    ("São Paulo", "SP"), ("Rio de Janeiro", "RJ"), ("Belo Horizonte", "MG"),
    ("Curitiba", "PR"), ("Porto Alegre", "RS"), ("Salvador", "BA"),
    ("Recife", "PE"), ("Fortaleza", "CE"), ("Brasília", "DF"), ("Manaus", "AM"),
]
CORES_AVATAR = ["#B8460E", "#2E5C8A", "#4B7B4F", "#8A4B7B", "#6B5B3E"]

# --- Bancos de comentários, por tom (nota alta/média/baixa) ---------------

FRASES = {
    "positivo": [
        "Atendimento excelente, resolveram meu problema rapidamente pelo chat. "
        "Fiquei surpreso com a agilidade, em menos de 10 minutos já tinha uma solução.",
        "Fui muito bem atendido pela equipe de suporte, recomendo o serviço para "
        "quem busca uma empresa que realmente resolve o que promete.",
        "Equipe atenciosa, resolveu tudo no mesmo dia. Já tive experiências ruins "
        "com outras empresas do setor, mas dessa vez fui surpreendido positivamente.",
        "Ótima experiência, superou minhas expectativas. O atendente entendeu meu "
        "problema de primeira e não precisei repetir a mesma informação várias vezes.",
        "Suporte rápido e educado, parabéns à equipe. Resolveram uma cobrança "
        "indevida em poucos minutos, sem burocracia nenhuma.",
    ],
    "neutro": [
        "Atendimento dentro do esperado, nada excepcional. Resolveram, mas o "
        "processo poderia ser mais simples do que foi.",
        "Resolveram meu problema, mas demorou um pouco mais do que eu esperava. "
        "No fim das contas, cumpriram o que prometeram.",
        "Ok, sem grandes problemas, mas também sem nenhum destaque. Atendimento "
        "mediano, típico de qualquer empresa do setor.",
        "Atendimento mediano, poderia ser mais ágil. Tive que ligar duas vezes "
        "para confirmar a mesma informação.",
    ],
    "negativo": [
        "Demorei muito para ser atendido, muito insatisfeito com o tempo de "
        "espera. Já são a terceira vez que preciso entrar em contato pelo mesmo motivo.",
        "Não resolveram meu problema, tive que entrar em contato de novo no dia "
        "seguinte e explicar tudo outra vez, como se fosse a primeira ligação.",
        "Atendimento ruim, sem retorno até hoje sobre o meu chamado. Já se "
        "passaram mais de duas semanas desde o primeiro contato.",
        "Péssima experiência, não recomendo o serviço para ninguém. Fui "
        "transferido entre setores sem nenhuma solução real.",
        "Fui mal atendido e ninguém retornou minha ligação como prometido. "
        "Cobraram um valor que eu já tinha contestado antes.",
    ],
}

# Variante "erro de português + palavrão censurado" (~10% das avaliações)
FRASES_ERRO_PALAVRAO = {
    "positivo": [
        "mto bom o atendimento slk, resolveram rapido D+, fikei surpreso pq nem "
        "esperava isso desse tipo de empresa",
        "cara q atendimento sinistro, nem acreditei, resolveram td numa call so, "
        "midia usar mais empresa assim",
    ],
    "neutro": [
        "atendimento ok, nada d mais, resolveu mas demorou um pouco, podia ser "
        "mais rapido pra ser sincero",
        "foi mais ou menos, nem bom nem ruim, resolveram o problema mas o "
        "atendente parecia meio perdido",
    ],
    "negativo": [
        "isso e uma p***a de atendimento, naum resolvem nd, ja liguei 3x e cada "
        "atendente fala uma coisa diferente, td errado",
        "q m***a de empresa, fikei 1hr esperando e no final cairam a ligação, "
        "um saco isso, naum indico pra ninguem",
        "atendimento eh um lixo mesmo, perdi mto tempo e naum resolveram pqp, "
        "vou cancelar td essa semana",
    ],
}

EMOJIS = {
    "positivo": ["😊", "👍", "🎉", "❤️"],
    "neutro": ["😐", "🤔"],
    "negativo": ["😡", "😤", "💔", "😞", "🤦‍♂️", "🤦‍♀️"],
}


def _tier(nota: int) -> str:
    if nota >= 4:
        return "positivo"
    if nota == 3:
        return "neutro"
    return "negativo"


def _aplicar_emojis(texto: str, tier: str) -> str:
    pool = EMOJIS[tier]
    escolhidos = random.sample(pool, k=min(2, len(pool)))
    partes = texto.split(". ")
    if len(partes) > 1:
        partes[0] = f"{partes[0]} {escolhidos[0]}"
        return ". ".join(partes) + f" {escolhidos[-1]}"
    return f"{texto} {' '.join(escolhidos)}"


def _gerar_comentario(nota: int) -> str:
    tier = _tier(nota)
    eh_erro_palavrao = random.random() < PROB_ERRO_PALAVRAO
    tem_emoji = random.random() < PROB_EMOJI

    pool = FRASES_ERRO_PALAVRAO[tier] if eh_erro_palavrao else FRASES[tier]
    texto = random.choice(pool)

    if tem_emoji:
        texto = _aplicar_emojis(texto, tier)

    return texto


def _truncar(texto: str, tamanho: int) -> str:
    if len(texto) <= tamanho:
        return texto
    return texto[:tamanho].rsplit(" ", 1)[0] + "…"


def _estrelas_html(nota: int) -> str:
    cheias = '<span class="star star-filled">★</span>' * nota
    vazias = '<span class="star">★</span>' * (5 - nota)
    return cheias + vazias


def _sortear_resolvido_voltaria(nota: int) -> tuple[bool, bool]:
    """Correlacionado à nota: quem deu nota alta tende a dizer que o
    problema foi resolvido e que voltaria a fazer negócio; nota baixa,
    o oposto. Só é chamado quando `respondido = True`."""
    if nota >= 4:
        p_resolvido, p_voltaria = 0.90, 0.85
    elif nota == 3:
        p_resolvido, p_voltaria = 0.50, 0.50
    else:
        p_resolvido, p_voltaria = 0.12, 0.08
    return random.random() < p_resolvido, random.random() < p_voltaria


def _gerar_avaliacoes(total: int) -> list[dict]:
    avaliacoes = []
    for i in range(1, total + 1):
        nota = random.choices([1, 2, 3, 4, 5], weights=[10, 10, 20, 30, 30])[0]
        comentario = _gerar_comentario(nota)
        cidade, estado = random.choice(CIDADES_ESTADOS)
        data_avaliacao = date.today() - timedelta(days=random.randint(1, 365))

        primeiro_nome = fake.first_name()
        sobrenome = fake.last_name()
        iniciais = (primeiro_nome[0] + sobrenome[0]).upper()
        cor_avatar = CORES_AVATAR[i % len(CORES_AVATAR)]
        pagina = ((i - 1) // AVALIACOES_POR_PAGINA) + 1

        respondido = random.random() < PROB_RESPONDIDO
        if respondido:
            resolvido, voltaria = _sortear_resolvido_voltaria(nota)
        else:
            resolvido = voltaria = None

        avaliacoes.append({
            "review_id": f"{i:04d}",
            "nota": nota,
            "comentario": comentario,
            "cidade": cidade,
            "estado": estado,
            "data_avaliacao": data_avaliacao,
            "nome_exibicao": f"{primeiro_nome} {sobrenome[0]}.",
            "iniciais": iniciais,
            "cor_avatar": cor_avatar,
            "pagina": pagina,
            "respondido": respondido,
            "resolvido": resolvido,
            "voltaria": voltaria,
            "util": random.randint(0, 35),
            "nao_util": random.randint(0, 6),
        })
    return avaliacoes


CSS = """@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Inter', Arial, Helvetica, sans-serif;
  background: #F1F2F5;
  color: #17181C;
  line-height: 1.55;
  -webkit-font-smoothing: antialiased;
}

.topbar {
  background: #FFFFFF;
  border-bottom: 1px solid #E7E8EC;
  padding: 14px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 10;
}
.topbar .logo { font-size: 19px; font-weight: 700; color: #B8460E; letter-spacing: -0.02em; }
.topbar nav { display: flex; gap: 4px; }
.topbar nav a {
  color: #5B5F6B; text-decoration: none; font-size: 13px; font-weight: 500;
  padding: 8px 14px; border-radius: 999px; transition: background .15s ease;
}
.topbar nav a:hover { background: #F1F2F5; color: #17181C; }

.container { max-width: 720px; margin: 0 auto; padding: 32px 20px 56px; }
.breadcrumb { font-size: 12px; color: #9B9EA8; margin-bottom: 18px; }
.breadcrumb a { color: #9B9EA8; text-decoration: none; }
.breadcrumb a:hover { color: #5B5F6B; }

h1 { font-size: 24px; font-weight: 700; letter-spacing: -0.02em; margin-bottom: 2px; }
.subtitulo { font-size: 13px; color: #9B9EA8; margin-bottom: 24px; }

.resumo {
  background: #FFFFFF;
  border-radius: 20px;
  box-shadow: 0 1px 2px rgba(23,24,28,.04), 0 4px 16px rgba(23,24,28,.05);
  padding: 24px 28px;
  display: flex;
  gap: 32px;
  align-items: center;
  margin-bottom: 28px;
}
.resumo .nota-media { text-align: center; min-width: 90px; }
.resumo .nota-media .numero { font-size: 40px; font-weight: 700; color: #B8460E; letter-spacing: -0.03em; }
.resumo .nota-media .total { font-size: 12px; color: #9B9EA8; margin-top: 2px; }
.distribuicao { flex: 1; }
.distribuicao .linha { display: flex; align-items: center; font-size: 12px; color: #9B9EA8; margin-bottom: 6px; }
.distribuicao .linha .rotulo { width: 28px; font-weight: 500; }
.distribuicao .barra-fundo { flex: 1; background: #F1F2F5; border-radius: 4px; height: 7px; margin: 0 10px; overflow: hidden; }
.distribuicao .barra-preenchida { background: #B8460E; height: 100%; border-radius: 4px; }

.review-card {
  background: #FFFFFF;
  border-radius: 18px;
  box-shadow: 0 1px 2px rgba(23,24,28,.03), 0 2px 10px rgba(23,24,28,.04);
  padding: 20px 22px;
  margin-bottom: 12px;
  transition: box-shadow .15s ease, transform .15s ease;
}
.review-card.clicavel:hover { box-shadow: 0 2px 4px rgba(23,24,28,.05), 0 8px 24px rgba(23,24,28,.08); transform: translateY(-1px); }

.review-header { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.avatar {
  width: 38px; height: 38px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: #FFFFFF; font-size: 13px; font-weight: 600; flex-shrink: 0;
}
.review-meta .nome { font-size: 14px; font-weight: 600; }
.review-meta .local-data { font-size: 12px; color: #9B9EA8; }

.review-rating { margin-bottom: 10px; display: flex; align-items: center; gap: 8px; }
.star { color: #E3E4E9; font-size: 15px; }
.star-filled { color: #B8460E; }
.nota-numero-chip {
  font-size: 11px; font-weight: 600; color: #7A4200; background: #FBEAD9;
  padding: 2px 8px; border-radius: 999px;
}

.review-comment { font-size: 14px; color: #26272C; }
.review-link {
  display: inline-flex; align-items: center; gap: 4px; margin-top: 12px;
  font-size: 13px; color: #B8460E; text-decoration: none; font-weight: 600;
}
.review-link:hover { gap: 8px; }

.paginacao { display: flex; justify-content: center; gap: 6px; margin-top: 28px; }
.paginacao a, .paginacao span {
  display: inline-flex; align-items: center; justify-content: center;
  min-width: 34px; height: 34px;
  border-radius: 10px; font-size: 13px; font-weight: 500;
  text-decoration: none; color: #17181C; background: #FFFFFF;
  box-shadow: 0 1px 2px rgba(23,24,28,.04);
}
.paginacao .atual { background: #B8460E; color: #FFFFFF; }
.paginacao a:hover { background: #F1F2F5; }

.voltar {
  display: inline-flex; align-items: center; gap: 4px; margin-bottom: 20px;
  font-size: 13px; color: #5B5F6B; text-decoration: none; font-weight: 500;
}
.voltar:hover { color: #17181C; }

.detalhe-card .review-comment { font-size: 15px; line-height: 1.8; margin-bottom: 20px; }

.badges { display: flex; flex-wrap: wrap; gap: 8px; margin: 18px 0; }
.badge {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 12px; font-weight: 600; padding: 6px 12px; border-radius: 999px;
}
.badge-sim { background: #E7F5EC; color: #1E7A42; }
.badge-nao { background: #FCEAEA; color: #B3261E; }

.divisor { border: none; border-top: 1px solid #EEEFF2; margin: 18px 0; }

.reacoes { display: flex; align-items: center; gap: 10px; }
.reacao-btn {
  display: inline-flex; align-items: center; gap: 6px;
  border: 1px solid #E7E8EC; background: #FFFFFF; border-radius: 999px;
  padding: 7px 14px; font-size: 13px; font-weight: 500; color: #5B5F6B;
  cursor: pointer; transition: background .15s ease, border-color .15s ease;
}
.reacao-btn:hover { background: #F1F2F5; border-color: #D8DAE0; }
.reacao-btn.ativo { background: #FBEAD9; border-color: #F0C69A; color: #7A4200; }
.reacao-btn .contagem { font-weight: 600; }

.respondido-tag {
  font-size: 12px; color: #9B9EA8; display: flex; align-items: center; gap: 6px; margin-top: 14px;
}
.respondido-tag .ponto { width: 6px; height: 6px; border-radius: 50%; background: #D8DAE0; }
.respondido-tag.sim .ponto { background: #1E7A42; }
"""

# Toggle simples: primeiro clique marca "ativo" e soma 1; clicar de novo
# desfaz. Corrige o bug da v1 (clique múltiplo somando infinito).
JS_REACOES = """function reagir(botao) {
  var span = botao.querySelector('.contagem');
  var ativo = botao.classList.toggle('ativo');
  var atual = parseInt(span.textContent, 10);
  span.textContent = ativo ? atual + 1 : atual - 1;
}
"""

TOPBAR = f"""  <div class="topbar">
    <div class="logo">{NOME_SITE}</div>
    <nav>
      <a href="#">Início</a>
      <a href="#">Empresas</a>
      <a href="#">Categorias</a>
      <a href="#">Entrar</a>
    </nav>
  </div>
"""


def _resumo_html(avaliacoes: list[dict]) -> str:
    total = len(avaliacoes)
    media = sum(a["nota"] for a in avaliacoes) / total
    contagem = {n: sum(1 for a in avaliacoes if a["nota"] == n) for n in range(1, 6)}

    linhas = []
    for n in [5, 4, 3, 2, 1]:
        pct = (contagem[n] / total) * 100
        linhas.append(f"""      <div class="linha">
        <span class="rotulo">{n}★</span>
        <span class="barra-fundo"><span class="barra-preenchida" style="width:{pct:.0f}%"></span></span>
        <span>{contagem[n]}</span>
      </div>""")

    return f"""  <div class="resumo">
    <div class="nota-media">
      <div class="numero">{media:.1f}</div>
      <div class="total">{total} avaliações</div>
    </div>
    <div class="distribuicao">
{chr(10).join(linhas)}
    </div>
  </div>
"""


def _card_listagem_html(a: dict) -> str:
    snippet = _truncar(a["comentario"], TAMANHO_SNIPPET)
    return f"""    <div class="review-card clicavel" data-review-id="{a['review_id']}">
      <div class="review-header">
        <div class="avatar" style="background:{a['cor_avatar']}">{a['iniciais']}</div>
        <div class="review-meta">
          <div class="nome">{a['nome_exibicao']}</div>
          <div class="local-data">{a['cidade']}/{a['estado']} · {a['data_avaliacao'].strftime('%d/%m/%Y')}</div>
        </div>
      </div>
      <div class="review-rating" data-nota="{a['nota']}">{_estrelas_html(a['nota'])}</div>
      <p class="review-comment">{snippet}</p>
      <a class="review-link" href="avaliacoes/avaliacao_{a['review_id']}.html">Leia a avaliação completa →</a>
    </div>
"""


def _paginacao_html(pagina_atual: int) -> str:
    itens = []
    for p in range(1, PAGINAS + 1):
        if p == pagina_atual:
            itens.append(f'<span class="atual">{p}</span>')
        else:
            itens.append(f'<a href="pagina_{p:02d}.html">{p}</a>')
    return f'  <div class="paginacao">{"".join(itens)}</div>\n'


def _gerar_pagina_listagem(numero: int, avaliacoes_da_pagina: list[dict], resumo_html: str) -> str:
    cards = "".join(_card_listagem_html(a) for a in avaliacoes_da_pagina)
    return f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="utf-8">
  <title>Avaliações sobre {NOME_EMPRESA} - Página {numero} - {NOME_SITE}</title>
  <link rel="stylesheet" href="estilos.css">
</head>
<body>
{TOPBAR}
  <div class="container">
    <div class="breadcrumb"><a href="#">Início</a> &gt; <a href="#">Empresas</a> &gt; {NOME_EMPRESA}</div>
    <h1>Avaliações de clientes — {NOME_EMPRESA}</h1>
    <div class="subtitulo">Página {numero} de {PAGINAS}</div>
{resumo_html}
    <div class="reviews-list">
{cards}    </div>
{_paginacao_html(numero)}  </div>
</body>
</html>
"""


def _badges_html(a: dict) -> str:
    if not a["respondido"]:
        return ""
    resolvido_classe = "badge-sim" if a["resolvido"] else "badge-nao"
    resolvido_texto = "✓ Problema resolvido" if a["resolvido"] else "✕ Problema não resolvido"
    voltaria_classe = "badge-sim" if a["voltaria"] else "badge-nao"
    voltaria_texto = "✓ Voltaria a fazer negócio" if a["voltaria"] else "✕ Não voltaria a fazer negócio"
    return f"""      <hr class="divisor">

      <div class="badges">
        <span class="badge {resolvido_classe}" data-campo="resolvido" data-valor="{'sim' if a['resolvido'] else 'nao'}">{resolvido_texto}</span>
        <span class="badge {voltaria_classe}" data-campo="voltaria" data-valor="{'sim' if a['voltaria'] else 'nao'}">{voltaria_texto}</span>
      </div>

"""


def _gerar_pagina_detalhe(a: dict) -> str:
    badges_html = _badges_html(a)
    respondido_classe = "sim" if a["respondido"] else ""
    respondido_texto = "Respondida pela empresa" if a["respondido"] else "Ainda não foi respondida pela empresa"

    return f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="utf-8">
  <title>Avaliação de {a['nome_exibicao']} sobre {NOME_EMPRESA} - {NOME_SITE}</title>
  <link rel="stylesheet" href="../estilos.css">
</head>
<body>
{TOPBAR}
  <div class="container">
    <div class="breadcrumb"><a href="#">Início</a> &gt; <a href="../pagina_{a['pagina']:02d}.html">{NOME_EMPRESA}</a> &gt; Avaliação #{a['review_id']}</div>
    <a class="voltar" href="../pagina_{a['pagina']:02d}.html">← Voltar para a lista de avaliações</a>

    <div class="review-card detalhe-card" data-review-id="{a['review_id']}">
      <div class="review-header">
        <div class="avatar" style="background:{a['cor_avatar']}">{a['iniciais']}</div>
        <div class="review-meta">
          <div class="nome">{a['nome_exibicao']}</div>
          <div class="local-data">{a['cidade']}/{a['estado']} · {a['data_avaliacao'].strftime('%d/%m/%Y')}</div>
        </div>
      </div>

      <div class="review-rating" data-nota="{a['nota']}">
        {_estrelas_html(a['nota'])}
        <span class="nota-numero-chip" data-nota-numero="{a['nota']}">{a['nota']} de 5</span>
      </div>

      <p class="review-comment">{a['comentario']}</p>

{badges_html}      <div class="reacoes">
        <button class="reacao-btn" onclick="reagir(this)">
          👍 <span class="contagem" data-reacao="util">{a['util']}</span>
        </button>
        <button class="reacao-btn" onclick="reagir(this)">
          👎 <span class="contagem" data-reacao="nao-util">{a['nao_util']}</span>
        </button>
      </div>

      <div class="respondido-tag {respondido_classe}" data-respondido="{'sim' if a['respondido'] else 'nao'}">
        <span class="ponto"></span> {respondido_texto}
      </div>
    </div>
  </div>
  <script src="../reacoes.js"></script>
</body>
</html>
"""


def gerar_fixtures(destino: Path) -> None:
    destino.mkdir(parents=True, exist_ok=True)
    pasta_detalhes = destino / "avaliacoes"
    pasta_detalhes.mkdir(exist_ok=True)

    total_avaliacoes = PAGINAS * AVALIACOES_POR_PAGINA
    avaliacoes = _gerar_avaliacoes(total_avaliacoes)
    resumo_html = _resumo_html(avaliacoes)

    (destino / "estilos.css").write_text(CSS, encoding="utf-8")
    (destino / "reacoes.js").write_text(JS_REACOES, encoding="utf-8")

    for numero_pagina in range(1, PAGINAS + 1):
        avaliacoes_da_pagina = [a for a in avaliacoes if a["pagina"] == numero_pagina]
        html = _gerar_pagina_listagem(numero_pagina, avaliacoes_da_pagina, resumo_html)
        (destino / f"pagina_{numero_pagina:02d}.html").write_text(html, encoding="utf-8")

    for a in avaliacoes:
        html = _gerar_pagina_detalhe(a)
        (pasta_detalhes / f"avaliacao_{a['review_id']}.html").write_text(html, encoding="utf-8")

    respondidas = sum(1 for a in avaliacoes if a["respondido"])
    com_erro = sum(1 for a in avaliacoes if any(a["comentario"] == t for tier in FRASES_ERRO_PALAVRAO.values() for t in tier))
    print(
        f"{PAGINAS} página(s) de listagem + {total_avaliacoes} página(s) de "
        f"detalhe geradas em '{destino}'.\n"
        f"Respondidas pela empresa: {respondidas}/{total_avaliacoes} "
        f"({respondidas/total_avaliacoes:.0%})."
    )


if __name__ == "__main__":
    gerar_fixtures(Path(__file__).parent / "paginas_html")

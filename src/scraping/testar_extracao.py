"""
Script de teste — coleta e trata os dados, mas NÃO grava no banco.

Uso (com o uvicorn já rodando e URL_SERVIDOR configurada no .env):
    python src/scraping/testar_extracao.py

Objetivo: validar a estrutura do dado extraído (nome, nota, comentário,
respondido, resolvido, voltaria) antes de conectar no Postgres. Quando a
estrutura estiver aprovada, o próximo passo é ligar `gravacao.py` a este
mesmo fluxo (ver status.md).
"""
from src.scraping.coletor import coletar_htmls_detalhe
from src.scraping.parser import extrair_avaliacoes
from src.scraping.tratamento import tratar_lote


def main() -> None:
    print("Coletando páginas via HTTP...")
    htmls_detalhe = coletar_htmls_detalhe()
    print(f"{len(htmls_detalhe)} avaliação(ões) coletada(s).")

    brutas = extrair_avaliacoes(htmls_detalhe)
    validas, descartadas = tratar_lote(brutas)

    print(f"\n{len(validas)} válidas, {len(descartadas)} descartadas.\n")

    if descartadas:
        print("Descartadas:")
        for item in descartadas:
            print(f"  - review_id={item.get('review_id')}: {item['motivo_descarte']}")

    print("\nAmostra (5 primeiras avaliações válidas):")
    for item in validas[:5]:
        print(f"""
  review_id : {item['review_id']}
  nome      : {item['nome']}
  data      : {item['data_avaliacao']}
  nota      : {item['nota']}
  respondido: {item['respondido']}
  resolvido : {item['resolvido']}
  voltaria  : {item['voltaria']}
  comentario: {item['comentario'][:80]}...""")

    respondidas = sum(1 for v in validas if v["respondido"])
    print(f"\nRespondidas pela empresa: {respondidas}/{len(validas)} ({respondidas/len(validas):.0%})")


if __name__ == "__main__":
    main()
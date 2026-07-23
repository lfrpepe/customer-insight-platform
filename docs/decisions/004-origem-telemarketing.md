# ADR 004 — Nova origem de avaliação: Telemarketing (Pesquisa Pós-Atendimento)

**Status:** Aceito
**Data:** 2026-07-23
**Fase:** 1/2 — Modelagem de Dados / Banco de Dados

## Contexto

O projeto já suportava 4 origens de avaliação (Formulário Web, Pinpad -
Atendente, Totem - Autoatendimento, Scraping), cada uma com um padrão
diferente de preenchimento (ver ADR-002 e a tabela "Preenchimento por
origem" em `data_model_relational.md`).

Uma 5ª origem realista e comum em centrais de atendimento é a **pesquisa de
satisfação pós-atendimento via telemarketing/IVR** — o cliente, ao final de
uma ligação (ativa ou receptiva), é convidado a "digitar uma nota de 1 a 5"
para avaliar o atendimento recebido.

## Decisão

Adicionar a origem `Telemarketing - Pesquisa Pós-Atendimento`, com o
seguinte padrão de preenchimento:

| Campo         | Conhecido? | Justificativa                                                        |
|---------------|:----------:|----------------------------------------------------------------------|
| `id_cliente`  | ✅ Sim     | A ligação (ativa ou receptiva) está vinculada a um telefone/cadastro já existente na base — diferente do Pinpad/Totem, que são anônimos |
| `id_categoria`| ✅ Sim     | O motivo/categoria da ligação já é conhecido pelo sistema de telemarketing antes da pesquisa ser aplicada |
| `comentario`  | ❌ Não     | O IVR captura apenas o dígito da nota (1–5); não há campo de texto livre |
| `nota`        | ✅ Sempre  | Obrigatória, como em todas as origens                                 |

Isso é estruturalmente idêntico ao Formulário Web em termos de FKs
conhecidas (`id_cliente` e `id_categoria` preenchidos), mas se diferencia
por **nunca** ter `comentario` — o que já era opcional no Formulário Web,
mas no Telemarketing é estruturalmente impossível (não existe campo de
texto no IVR).

Como essa origem tem `id_cliente` conhecido, ela também participa da
correlação persona↔cliente no seed de desenvolvimento (ver
`generate_seed_dev.py` e ADR anterior sobre perfis de satisfação),
igual ao Formulário Web.

## Alternativas consideradas

| Alternativa | Motivo de descarte |
|---|---|
| Tratar Telemarketing como uma variação do Formulário Web (mesma origem, campo extra indicando canal) | Descartada — origem já é o campo correto para diferenciar canal de captura (é para isso que `origens_avaliacao` existe); criar uma sub-flag dentro do Formulário Web duplicaria essa responsabilidade. |
| Permitir `comentario` opcional, igual ao Formulário Web | Descartada — não reflete a limitação real do canal (IVR não tem captura de texto livre; um comentário aqui seria dado inventado, não uma limitação real do canal sendo simulada). |

## Consequências

- **Schema:** nenhuma alteração de coluna necessária — `avaliacoes` já
  suporta esse padrão de preenchimento (FKs opcionais desde o ADR-002).
  Apenas nova linha em `origens_avaliacao`.
- **Seed de desenvolvimento:** distribuição de origens redistribuída para
  acomodar a 5ª origem; ver proporções atualizadas em
  `generate_seed_dev.py`.
- **Análise de negócio:** Telemarketing passa a contribuir para "nota média
  por cliente" e "clientes recorrentemente insatisfeitos" junto com o
  Formulário Web — são as duas únicas origens que sustentam esse tipo de
  análise (ver tabela atualizada em `data_model_relational.md`).

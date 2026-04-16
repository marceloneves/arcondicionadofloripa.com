# -*- coding: utf-8 -*-
"""Gera servicos.html: seções por região em ordem alfabética (nome), com cards de serviço."""

from __future__ import annotations

import unicodedata
from pathlib import Path

from _rebuild_servico_main import BAIRROS, CIDADES, SERV_META

ROOT = Path(__file__).resolve().parent

# Serviços com página local por bairro em Florianópolis (sem conserto/pmoc por bairro no disco).
SERVICOS_COM_LOCAL_FLN = (
    "instalacao-de-ar-condicionado",
    "manutencao-de-ar-condicionado",
    "limpeza-de-ar-condicionado",
    "higienizacao-de-ar-condicionado",
    "carga-de-gas-de-ar-condicionado",
    "remocao-e-reinstalacao-de-ar-condicionado",
)

SERVICOS_COM_LOCAL_CIDADE = SERVICOS_COM_LOCAL_FLN + (
    "conserto-de-ar-condicionado",
    "pmoc-de-ar-condicionado",
)

# Seis âncoras no topo: mesmos ids que /servicos.html#… no rodapé (exceto conserto/PMOC, id no final da página).
ANCHOR_HUBS_TOP: tuple[tuple[str, str, str], ...] = (
    ("instalacao-de-ar-condicionado", "servico/instalacao-de-ar-condicionado.html", "Instalação de Ar-Condicionado"),
    ("manutencao-de-ar-condicionado", "servico/manutencao-de-ar-condicionado.html", "Manutenção de Ar-Condicionado"),
    ("limpeza-de-ar-condicionado", "servico/limpeza-de-ar-condicionado.html", "Limpeza de Ar-Condicionado"),
    ("higienizacao-de-ar-condicionado", "servico/higienizacao-de-ar-condicionado.html", "Higienização de Ar-Condicionado"),
    ("carga-de-gas-de-ar-condicionado", "servico/carga-de-gas-de-ar-condicionado.html", "Carga de Gás de Ar-Condicionado"),
    ("remocao-e-reinstalacao-de-ar-condicionado", "servico/remocao-e-reinstalacao-de-ar-condicionado.html", "Remoção e Reinstalação de Ar-Condicionado"),
)


def _norm_sort(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s.casefold()


def _href_servico(sk: str, prep: str, slug: str, suf: str) -> str:
    tok = "florianopolis" if suf == "florianopolis" else "sc"
    return f"servico/{sk}-{prep}-{slug}-{tok}.html"


def _card(sk: str, prep: str, slug: str, suf: str, nome_regiao: str) -> str:
    meta = SERV_META[sk]
    href = _href_servico(sk, prep, slug, suf)
    label = f'{meta["titulo"]} em {nome_regiao}'
    return (
        f'<article class="card"><h3><a href="{href}">{label}</a></h3></article>'
    )


def _bloco_regiao(slug: str, nome: str, prep: str, suf: str) -> str:
    is_cidade = slug in CIDADES
    servicos = SERVICOS_COM_LOCAL_CIDADE if is_cidade else SERVICOS_COM_LOCAL_FLN
    if is_cidade:
        hub = f"regioes/{slug}-sc.html"
        meta_linha = f'SC · <a href="{hub}">Hub da cidade</a>'
    else:
        hub = f"regioes/{slug}-florianopolis.html"
        meta_linha = f'Florianópolis · <a href="{hub}">Hub da região</a>'
    cards = "".join(_card(sk, prep, slug, suf, nome) for sk in servicos)
    return f"""  <section class="section servicos-por-regiao" id="regiao-{slug}">
    <div class="container">
      <h2 class="servicos-regiao-titulo">{nome}</h2>
      <p class="servicos-regiao-meta">{meta_linha}</p>
      <div class="grid-3">{cards}</div>
    </div>
  </section>
"""


def build_main_html() -> str:
    entries = []
    for slug, meta in BAIRROS.items():
        nome = meta["nome"]
        prep = meta["prep"]
        suf = "sc" if slug in CIDADES else "florianopolis"
        entries.append((slug, nome, prep, suf))
    entries.sort(key=lambda t: _norm_sort(t[1]))
    return "\n".join(_bloco_regiao(slug, nome, prep, suf) for slug, nome, prep, suf in entries)


def build_anchor_strip() -> str:
    lis = "".join(
        f'<li><a id="{aid}" href="{href}">{label}</a></li>'
        for aid, href, label in ANCHOR_HUBS_TOP
    )
    lis_extra = (
        '<li><a href="servico/conserto-de-ar-condicionado.html">Conserto de Ar-Condicionado (hub)</a></li>'
        + '<li><a href="servico/pmoc-de-ar-condicionado.html">PMOC de Ar-Condicionado (hub)</a></li>'
    )
    return f"""  <section class="section servicos-indice-tipo">
    <div class="container">
      <p class="servicos-indice-tipo-lead">Atalhos para o <strong>hub geral</strong> de cada tipo (âncoras usadas no rodapé e em outras páginas):</p>
      <ul class="servicos-indice-tipo-list">{lis}{lis_extra}</ul>
    </div>
  </section>
"""


def build_page() -> str:
    main_sections = build_main_html()
    anchor_strip = build_anchor_strip()
    extra = """  <section class="section servicos-por-tipo">
    <div class="container">
      <h2 class="servicos-grupo-titulo" id="conserto-de-ar-condicionado">Conserto de Ar-Condicionado</h2>
      <p class="servicos-grupo-extra">Em bairros de Florianópolis não há páginas locais de conserto; use o hub ou o contato. Em São José, Palhoça e Biguaçu, o conserto local está nos blocos por região acima.</p>
      <h2 class="servicos-grupo-titulo" id="pmoc-de-ar-condicionado">PMOC de Ar-Condicionado</h2>
      <p class="servicos-grupo-extra">PMOC para empresas e condomínios segue o mesmo critério: hub geral na capital; páginas locais nas três cidades da Grande Florianópolis nos blocos acima.</p>
      <div class="grid-3">
        <article class="card"><h3><a href="servico/conserto-de-ar-condicionado.html">Conserto de Ar-Condicionado (hub)</a></h3></article>
        <article class="card"><h3><a href="servico/pmoc-de-ar-condicionado.html">PMOC de Ar-Condicionado (hub)</a></h3></article>
        <article class="card"><h3><a href="contato.html">Solicitar orçamento</a></h3></article>
      </div>
    </div>
  </section>
"""
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Serviços de Ar-Condicionado por Região | Florianópolis e Grande Florianópolis</title>
  <meta name="description" content="Serviços de ar-condicionado listados por região em ordem alfabética: Florianópolis (por bairro) e cidades da Grande Florianópolis, com links para instalação, manutenção, limpeza, higienização, carga de gás, reinstalação, conserto e PMOC quando disponível.">
  <link rel="stylesheet" href="css/style.css">

</head>
<body>
<header class="site-header">
  <div class="container nav-wrap">
    <a class="logo" href="index.html">Ar Condicionado em Florianópolis</a>
    <button class="menu-toggle" aria-label="Abrir menu" aria-expanded="false">☰</button>
    <nav class="main-nav" id="mainNav">
      <a href="index.html" class="">Início</a>
      <a href="servicos.html" class="active">Serviços</a>
      <a href="regioes.html" class="">Regiões</a>
      <a href="blog.html" class="">Blog</a>
      <a href="contato.html" class="">Contato</a>
    </nav>
    <a class="btn btn-whats" href="https://wa.me/5548988105199?text=Olá!%20Quero%20orçamento%20de%20ar-condicionado%20em%20Florianópolis." target="_blank" rel="noopener">WhatsApp</a>
  </div>
</header>
<main>
  <section class="inner-banner">
    <div class="container">
      <h1>Serviços por região</h1>
      <p>Regiões em <strong>ordem alfabética</strong>. Em cada bloco, os serviços com página local; em Florianópolis (bairros), conserto e PMOC ficam no <a href="#conserto-de-ar-condicionado">final da página</a> (hubs gerais).</p>
    </div>
  </section>

{anchor_strip}
{main_sections}
{extra}
</main>
<footer class="site-footer">
  <div class="container footer-grid">
    <div>
      <h3>Ar Condicionado em Florianópolis</h3>
      <p>Atendimento técnico para instalação, manutenção, limpeza, higienização, carga de gás e reinstalação em Florianópolis.</p>
    </div>
    <div><h4>Links rápidos</h4><ul><li><a href="/index.html">Início</a></li><li><a href="/servicos.html">Serviços</a></li><li><a href="/regioes.html">Regiões</a></li><li><a href="/contato.html">Contato</a></li></ul></div>
    <div><h4>Serviços</h4><ul><li><a href="/servicos.html#instalacao-de-ar-condicionado">Instalação de Ar-Condicionado</a></li><li><a href="/servicos.html#manutencao-de-ar-condicionado">Manutenção de Ar-Condicionado</a></li><li><a href="/servicos.html#limpeza-de-ar-condicionado">Limpeza de Ar-Condicionado</a></li><li><a href="/servicos.html#higienizacao-de-ar-condicionado">Higienização de Ar-Condicionado</a></li><li><a href="/servicos.html#carga-de-gas-de-ar-condicionado">Carga de Gás de Ar-Condicionado</a></li><li><a href="/servicos.html#remocao-e-reinstalacao-de-ar-condicionado">Remoção e Reinstalação de Ar-Condicionado</a></li><li><a href="/servicos.html#conserto-de-ar-condicionado">Conserto de Ar-Condicionado</a></li><li><a href="/servicos.html#pmoc-de-ar-condicionado">PMOC de Ar-Condicionado</a></li></ul></div>
    <div><h4>Regiões</h4><ul><li><a href="/regioes/abraao-florianopolis.html">Abraão</a></li><li><a href="/regioes/agronomica-florianopolis.html">Agronômica</a></li><li><a href="/regioes/armacao-florianopolis.html">Armação</a></li><li><a href="/regioes/balneario-florianopolis.html">Balneário</a></li><li><a href="/regioes/barra-da-lagoa-florianopolis.html">Barra da Lagoa</a></li><li><a href="/regioes/biguacu-sc.html">Biguaçu</a></li><li><a href="/regioes/bom-abrigo-florianopolis.html">Bom Abrigo</a></li><li><a href="/regioes/cachoeira-do-bom-jesus-florianopolis.html">Cachoeira do Bom Jesus</a></li><li><a href="/regioes/cacupe-florianopolis.html">Cacupé</a></li><li><a href="/regioes/campeche-florianopolis.html">Campeche</a></li><li><a href="/regioes/canasvieiras-florianopolis.html">Canasvieiras</a></li><li><a href="/regioes/canto-florianopolis.html">Canto</a></li><li><a href="/regioes/capoeiras-florianopolis.html">Capoeiras</a></li><li><a href="/regioes/carianos-florianopolis.html">Carianos</a></li><li><a href="/regioes/carvoeira-florianopolis.html">Carvoeira</a></li><li><a href="/regioes/centro-florianopolis.html">Centro</a></li><li><a href="/regioes/coloninha-florianopolis.html">Coloninha</a></li><li><a href="/regioes/coqueiros-florianopolis.html">Coqueiros</a></li><li><a href="/regioes/corrego-grande-florianopolis.html">Córrego Grande</a></li><li><a href="/regioes/costeira-do-pirajubae-florianopolis.html">Costeira do Pirajubaé</a></li><li><a href="/regioes/daniela-florianopolis.html">Daniela</a></li><li><a href="/regioes/estreito-florianopolis.html">Estreito</a></li><li><a href="/regioes/ingleses-florianopolis.html">Ingleses</a></li><li><a href="/regioes/itacorubi-florianopolis.html">Itacorubi</a></li><li><a href="/regioes/itaguacu-florianopolis.html">Itaguaçu</a></li><li><a href="/regioes/jardim-atlantico-florianopolis.html">Jardim Atlântico</a></li><li><a href="/regioes/jardim-capoeiras-florianopolis.html">Jardim Capoeiras</a></li><li><a href="/regioes/joao-paulo-florianopolis.html">João Paulo</a></li><li><a href="/regioes/jose-mendes-florianopolis.html">José Mendes</a></li><li><a href="/regioes/jurere-florianopolis.html">Jurerê</a></li><li><a href="/regioes/jurere-internacional-florianopolis.html">Jurerê Internacional</a></li><li><a href="/regioes/lagoa-da-conceicao-florianopolis.html">Lagoa da Conceição</a></li><li><a href="/regioes/mocambique-florianopolis.html">Moçambique</a></li><li><a href="/regioes/monte-cristo-florianopolis.html">Monte Cristo</a></li><li><a href="/regioes/monte-verde-florianopolis.html">Monte Verde</a></li><li><a href="/regioes/morro-das-pedras-florianopolis.html">Morro das Pedras</a></li><li><a href="/regioes/palhoca-sc.html">Palhoça</a></li><li><a href="/regioes/pantanal-florianopolis.html">Pantanal</a></li><li><a href="/regioes/pantano-do-sul-florianopolis.html">Pântano do Sul</a></li><li><a href="/regioes/ponta-das-canas-florianopolis.html">Ponta das Canas</a></li><li><a href="/regioes/praia-brava-florianopolis.html">Praia Brava</a></li><li><a href="/regioes/praia-do-forte-florianopolis.html">Praia do Forte</a></li><li><a href="/regioes/ratones-florianopolis.html">Ratones</a></li><li><a href="/regioes/ribeirao-da-ilha-florianopolis.html">Ribeirão da Ilha</a></li><li><a href="/regioes/rio-tavares-florianopolis.html">Rio Tavares</a></li><li><a href="/regioes/rio-vermelho-florianopolis.html">Rio Vermelho</a></li><li><a href="/regioes/saco-dos-limoes-florianopolis.html">Saco dos Limões</a></li><li><a href="/regioes/saco-grande-florianopolis.html">Saco Grande</a></li><li><a href="/regioes/sambaqui-florianopolis.html">Sambaqui</a></li><li><a href="/regioes/santa-monica-florianopolis.html">Santa Mônica</a></li><li><a href="/regioes/santinho-florianopolis.html">Santinho</a></li><li><a href="/regioes/santo-antonio-de-lisboa-florianopolis.html">Santo Antônio de Lisboa</a></li><li><a href="/regioes/sao-joao-do-rio-vermelho-florianopolis.html">São João do Rio Vermelho</a></li><li><a href="/regioes/sao-jose-sc.html">São José</a></li><li><a href="/regioes/tapera-florianopolis.html">Tapera</a></li><li><a href="/regioes/tapera-da-base-florianopolis.html">Tapera da Base</a></li><li><a href="/regioes/trindade-florianopolis.html">Trindade</a></li><li><a href="/regioes/vargem-do-bom-jesus-florianopolis.html">Vargem do Bom Jesus</a></li><li><a href="/regioes/vargem-grande-florianopolis.html">Vargem Grande</a></li><li><a href="/regioes/vargem-pequena-florianopolis.html">Vargem Pequena</a></li></ul></div>
  </div>
  <div class="container footer-bottom"><p>© 2026 Ar Condicionado em Florianópolis. Todos os direitos reservados.</p><p><a href="tel:+5548988105199">(48) 98810-5199</a></p></div>
</footer>
<a class="floating-whatsapp" href="https://wa.me/5548988105199?text=Olá!%20Quero%20orçamento%20de%20ar-condicionado%20em%20Florianópolis." target="_blank" rel="noopener" aria-label="Falar no WhatsApp">WhatsApp</a>
<script src="js/script.js"></script>
</body>
</html>
"""


def main() -> None:
    out = ROOT / "servicos.html"
    out.write_text(build_page(), encoding="utf-8")
    print("OK:", out.name)


if __name__ == "__main__":
    main()

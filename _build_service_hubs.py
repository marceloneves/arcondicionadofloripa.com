# -*- coding: utf-8 -*-
"""Gera hubs por serviço com descrição e links para todos os bairros."""

from pathlib import Path
import json

from _rebuild_servico_main import BAIRROS, SERV_META, SERVICE_KEYS

ROOT = Path(__file__).parent
OUT_DIR = ROOT / "servico-hub"
PHONE = "(48) 99999-0000"
TEL = "+5548999990000"
WA = "https://wa.me/5548999990000?text=Olá!%20Quero%20orçamento%20de%20ar-condicionado%20em%20Florianópolis."
BASE_URL = "https://arcondicionadofloripa.com"

INTRO = {
    "instalacao-de-ar-condicionado": (
        "A instalação de ar-condicionado em Florianópolis exige avaliação do ambiente, definição da rota de tubulação, "
        "dreno, alimentação elétrica e posicionamento correto da evaporadora e da condensadora."
    ),
    "manutencao-de-ar-condicionado": (
        "A manutenção de ar-condicionado em Florianópolis ajuda a revisar o funcionamento do sistema, reduzir falhas, "
        "melhorar desempenho e evitar retrabalho em períodos de uso intenso."
    ),
    "limpeza-de-ar-condicionado": (
        "A limpeza de ar-condicionado em Florianópolis remove sujeira acumulada em filtros, bandeja e áreas acessíveis, "
        "melhorando vazão de ar, conforto térmico e percepção de higiene no ambiente."
    ),
    "higienizacao-de-ar-condicionado": (
        "A higienização de ar-condicionado em Florianópolis é indicada quando há odor persistente, biofilme ou necessidade "
        "de reforçar a qualidade do ar em residências, consultórios, salas e comércios."
    ),
    "carga-de-gas-de-ar-condicionado": (
        "A carga de gás de ar-condicionado em Florianópolis deve sempre partir de diagnóstico técnico, com checagem de "
        "vazamento, circuito frigorífico, vácuo e condições gerais do equipamento."
    ),
    "remocao-e-reinstalacao-de-ar-condicionado": (
        "A remoção e reinstalação de ar-condicionado em Florianópolis atende mudanças, reformas e readequações, com "
        "desmontagem segura, transporte e reinstalação com testes no novo ponto."
    ),
}


def href_for(sk: str, prep: str, bairro_slug: str) -> str:
    return f"/servico/{sk}-{prep}-{bairro_slug}-florianopolis.html"


def hub_slug(sk: str) -> str:
    return f"/servico-hub/{sk}.html"


def schema_for(sk: str, title: str, description: str) -> str:
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "CollectionPage",
                "@id": f"{BASE_URL}/servico-hub/{sk}.html#webpage",
                "url": f"{BASE_URL}/servico-hub/{sk}.html",
                "name": title,
                "description": description,
                "isPartOf": {
                    "@type": "WebSite",
                    "@id": f"{BASE_URL}/#website",
                    "name": "Ar Condicionado em Florianópolis",
                    "url": BASE_URL,
                },
            },
            {
                "@type": "Service",
                "@id": f"{BASE_URL}/servico-hub/{sk}.html#service",
                "name": SERV_META[sk]["titulo"],
                "serviceType": SERV_META[sk]["titulo"],
                "description": SERV_META[sk]["oque"],
                "provider": {
                    "@type": "LocalBusiness",
                    "name": "Ar Condicionado em Florianópolis",
                    "url": BASE_URL,
                    "telephone": TEL,
                },
                "areaServed": {
                    "@type": "City",
                    "name": "Florianópolis",
                    "containedInPlace": {
                        "@type": "AdministrativeArea",
                        "name": "Santa Catarina",
                    },
                },
            },
        ],
    }
    return json.dumps(graph, ensure_ascii=False)


def build_page(sk: str) -> str:
    meta = SERV_META[sk]
    title = f"{meta['titulo']} em Florianópolis | Hub do Serviço"
    description = (
        f"Hub de {meta['curto']} em Florianópolis: descrição do serviço e links para todas as páginas por bairro."
    )
    items = []
    for bairro_slug, bairro in BAIRROS.items():
        href = href_for(sk, bairro["prep"], bairro_slug)
        items.append(
            f'<li><a href="{href}">{meta["titulo"]} {bairro["prep"]} {bairro["nome"]}</a></li>'
        )
    links_html = "".join(items)
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <link rel="canonical" href="{BASE_URL}/servico-hub/{sk}.html">
  <link rel="stylesheet" href="../css/style.css">
  <script type="application/ld+json">{schema_for(sk, title, description)}</script>
</head>
<body>
<header class="site-header">
  <div class="container nav-wrap">
    <a class="logo" href="../index.html">Ar Condicionado em Florianópolis</a>
    <button class="menu-toggle" aria-label="Abrir menu" aria-expanded="false">☰</button>
    <nav class="main-nav" id="mainNav">
      <a href="../index.html">Início</a>
      <a href="../servicos.html" class="active">Serviços</a>
      <a href="../bairros.html">Bairros</a>
      <a href="../contato.html">Contato</a>
    </nav>
    <a class="btn btn-whats" href="{WA}" target="_blank" rel="noopener">WhatsApp</a>
  </div>
</header>
<main>
<section class="inner-banner"><div class="container"><h1>{meta["titulo"]} em Florianópolis</h1><p>Hub do serviço com explicação objetiva e acesso às páginas locais por bairro.</p></div></section>
<section class="section"><div class="container">
  <p>{INTRO[sk]}</p>
  <p>Este hub reúne o contexto geral do serviço e os links locais para bairros atendidos em Florianópolis, o que facilita a navegação entre páginas com foco geográfico e intenção de busca mais específica.</p>
  <p>Se você quer comparar bairros, avaliar a cobertura ou acessar rapidamente a página certa do seu endereço, use a lista abaixo.</p>
</div></section>
<section class="section"><div class="container"><div class="card">
  <h2>Páginas de {meta["curto"]} por bairro</h2>
  <div class="local-links"><ul>{links_html}</ul></div>
</div></div></section>
<section class="section"><div class="container cta-box"><div><h2>Precisa de {meta["curto"]} em Florianópolis?</h2><p>Fale com a equipe e receba orientação técnica para o seu caso.</p></div><div><a class="btn btn-whats" href="{WA}" target="_blank" rel="noopener">WhatsApp</a> <a class="btn btn-primary" href="../contato.html">Solicitar orçamento</a> <a class="btn btn-outline" href="tel:{TEL}">Ligar</a></div></div></section>
<section class="section"><div class="container"><div class="card"><h2>Links úteis</h2><ul><li><a href="../index.html">Home</a></li><li><a href="../servicos.html">Página geral de serviços</a></li><li><a href="../bairros.html">Lista de bairros</a></li><li><a href="../contato.html">Contato</a></li></ul></div></div></section>
</main>
<footer class="site-footer">
  <div class="container footer-grid">
    <div><h3>Ar Condicionado em Florianópolis</h3><p>Atendimento técnico para instalação, manutenção, limpeza, higienização, carga de gás e reinstalação em Florianópolis.</p></div>
    <div><h4>Links rápidos</h4><ul><li><a href="../index.html">Início</a></li><li><a href="../servicos.html">Serviços</a></li><li><a href="../bairros.html">Bairros</a></li><li><a href="../contato.html">Contato</a></li></ul></div>
    <div><h4>Serviços</h4><ul><li><a href="{hub_slug('instalacao-de-ar-condicionado')}">Instalação</a></li><li><a href="{hub_slug('manutencao-de-ar-condicionado')}">Manutenção</a></li><li><a href="{hub_slug('limpeza-de-ar-condicionado')}">Limpeza</a></li><li><a href="{hub_slug('higienizacao-de-ar-condicionado')}">Higienização</a></li><li><a href="{hub_slug('carga-de-gas-de-ar-condicionado')}">Carga de gás</a></li><li><a href="{hub_slug('remocao-e-reinstalacao-de-ar-condicionado')}">Remoção e reinstalação</a></li></ul></div>
    <div><h4>Este hub</h4><p><a href="../servicos.html">Ver visão geral dos serviços</a></p></div>
  </div>
  <div class="container footer-bottom"><p>© 2026 Ar Condicionado em Florianópolis. Todos os direitos reservados.</p><p><a href="tel:{TEL}">{PHONE}</a></p></div>
</footer>
<a class="floating-whatsapp" href="{WA}" target="_blank" rel="noopener" aria-label="Falar no WhatsApp">WhatsApp</a>
<script src="../js/script.js"></script>
</body>
</html>
"""


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    for sk in SERVICE_KEYS:
        (OUT_DIR / f"{sk}.html").write_text(build_page(sk), encoding="utf-8")
    print("Hubs gerados:", len(SERVICE_KEYS))


if __name__ == "__main__":
    main()

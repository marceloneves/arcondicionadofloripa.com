# -*- coding: utf-8 -*-
"""Legado: hubs em servico/<serviço>/ (sem cidade). Desativado — páginas canónicas: *-em-florianopolis/ e *-em-*-sc/."""

from html import escape
from pathlib import Path
import json

from _fix_html_root_paths import apply_relative_paths_to_file
from _brand import FAVICON_PATH, LOGO_ALT, LOGO_URL as BUSINESS_LOGO_URL
from _social_meta import insert_social_meta_after_description
from _schema_speakable import speakable
from _rebuild_servico_main import (
    BAIRROS,
    CIDADES,
    SERV_META,
    SERVICE_KEYS,
    SERVICO_INTRO_FOTO_ALT,
    SERVICO_INTRO_FOTO_H,
    SERVICO_INTRO_FOTO_PATH,
    SERVICO_INTRO_FOTO_W,
)

ROOT = Path(__file__).parent
OUT_DIR = ROOT / "servico"
PHONE = "(48) 98810-5199"
TEL = "+5548988105199"
WA = "https://wa.me/5548988105199?text=Olá!%20Quero%20orçamento%20de%20ar-condicionado%20em%20Florianópolis."
BASE_URL = "https://arcondicionadofloripa.com"
FOUNDING_DATE = "2021-04-06"

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
    "conserto-de-ar-condicionado": (
        "O conserto de ar-condicionado em Florianópolis foca em diagnóstico estruturado, identificação da causa raiz e "
        "correção do defeito com testes finais, evitando trocas desnecessárias de peças."
    ),
    "pmoc-de-ar-condicionado": (
        "O PMOC de ar-condicionado (Plano de Manutenção, Operação e Controle) organiza rotinas de manutenção, registros e "
        "frequências para sistemas de climatização em empresas, condomínios e comércios em Florianópolis."
    ),
}


def href_for(sk: str, prep: str, bairro_slug: str) -> str:
    # Capital: arquivo canónico é sempre ...-em-florianopolis/ (não ...-em-florianopolis-florianopolis/).
    if bairro_slug == "florianopolis":
        return servico_florianopolis_url(sk)
    suf = "sc" if bairro_slug in CIDADES else "florianopolis"
    return f"/servico/{sk}-{prep}-{bairro_slug}-{suf}/"


def hub_slug(sk: str) -> str:
    return f"/servico/{sk}/"


def servico_florianopolis_url(sk: str) -> str:
    """Página do serviço na capital (mesmos destinos do rodapé global)."""
    return f"/servico/{sk}-em-florianopolis/"


def schema_for(sk: str, title: str, description: str) -> str:
    """Um único nó: Service + WebPage (breadcrumb). Hub não tem FAQ no HTML."""
    page_url = f"{BASE_URL}/servico/{sk}/"
    meta = SERV_META[sk]
    payload = {
        "@context": "https://schema.org",
        "@type": ["Service", "WebPage"],
        "@id": f"{page_url}#servico",
        "speakable": speakable(
            "main section.inner-banner h1",
            "main .section .container > p:first-of-type",
        ),
        "name": title,
        "description": description,
        "url": page_url,
        "serviceType": meta["titulo"],
        "provider": {
            "@type": "LocalBusiness",
            "name": "Ar Condicionado em Florianópolis",
            "url": BASE_URL,
            "telephone": TEL,
            "foundingDate": FOUNDING_DATE,
            "logo": {"@type": "ImageObject", "url": BUSINESS_LOGO_URL},
        },
        "areaServed": {
            "@type": "City",
            "name": "Florianópolis",
            "containedInPlace": {
                "@type": "AdministrativeArea",
                "name": "Santa Catarina",
            },
        },
        "breadcrumb": {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Início", "item": f"{BASE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": "Serviços", "item": f"{BASE_URL}/servicos/"},
                {"@type": "ListItem", "position": 3, "name": meta["titulo"], "item": page_url},
            ],
        },
    }
    return json.dumps(payload, ensure_ascii=False)


def build_page(sk: str) -> str:
    meta = SERV_META[sk]
    title = meta["titulo"]
    description = (
        f"Hub de {meta['curto']} em Florianópolis: descrição do serviço e links para todas as páginas por bairro."
    )
    cards = []
    for bairro_slug, bairro in BAIRROS.items():
        href = href_for(sk, bairro["prep"], bairro_slug)
        if bairro_slug == "florianopolis":
            desc = f'Página local de {meta["curto"]} {bairro["prep"]} {bairro["nome"]}.'
        elif bairro_slug in CIDADES:
            desc = (
                f'Página local de {meta["curto"]} {bairro["prep"]} {bairro["nome"]} '
                f"na Grande Florianópolis (SC)."
            )
        else:
            desc = (
                f'Página local de {meta["curto"]} {bairro["prep"]} {bairro["nome"]} em Florianópolis.'
            )
        cards.append(
            f'<article class="card hub-servico-item"><h3>{bairro["nome"]}</h3>'
            f"<p>{desc}</p>"
            f'<a class="btn btn-outline" href="{href}">Ver página local</a></article>'
        )
    cards_html = "".join(cards)
    page_url_hub = f"{BASE_URL}/servico/{sk}/"
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="icon" href="{FAVICON_PATH}" type="image/webp">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <link rel="canonical" href="{BASE_URL}/servico/{sk}/">
  <link rel="stylesheet" href="/css/style.css">
  <script type="application/ld+json">{schema_for(sk, title, description)}</script>
</head>
<body>
<header class="site-header">
  <div class="container nav-wrap">
    <a class="logo" href="/"><img class="logo-img" src="/images/ar-condicionado-floripa-logo.webp" alt="{LOGO_ALT}" width="1024" height="558" loading="eager" decoding="async"><span class="logo-tagline">Ar-Condicionado em Florianópolis</span></a>
    <button class="menu-toggle" aria-label="Abrir menu" aria-expanded="false">☰</button>
    <nav class="main-nav" id="mainNav">
      <a href="/">Início</a>
      <a href="/servicos/" class="active">Serviços</a>
      <a href="/regioes/">Regiões</a>
      <a href="/blog/">Blog</a>
      <a href="/contato/">Contato</a>
    </nav>
    <a class="btn btn-whats" href="{WA}" target="_blank" rel="noopener nofollow">WhatsApp</a>
  </div>
</header>
<main>
<section class="inner-banner"><div class="container"><h1>{meta["titulo"]} em Florianópolis</h1><p>Hub do serviço com explicação objetiva e acesso às páginas locais por bairro.</p></div></section>
<div class="section"><div class="container">
  <p>{INTRO[sk]}</p>
  <p>Este hub reúne o contexto geral do serviço e os links locais para bairros atendidos em Florianópolis, o que facilita a navegação entre páginas com foco geográfico e intenção de busca mais específica.</p>
  <p>Se você quer comparar bairros, avaliar a cobertura ou acessar rapidamente a página certa do seu endereço, use a lista abaixo.</p>
</div></div>
<section class="section"><div class="container">
  <img class="servico-intro-foto" src="{SERVICO_INTRO_FOTO_PATH}" alt="{escape(SERVICO_INTRO_FOTO_ALT, quote=True)}" width="{SERVICO_INTRO_FOTO_W}" height="{SERVICO_INTRO_FOTO_H}" loading="lazy" decoding="async">
  <h2>Páginas de {meta["curto"]} por bairro</h2>
  <div class="grid-3">{cards_html}</div>
</div></section>
<section class="section"><div class="container cta-box"><div><h2>Precisa de {meta["curto"]} em Florianópolis?</h2><p>Fale com a equipe e receba orientação técnica para o seu caso.</p></div><div><a class="btn btn-whats" href="{WA}" target="_blank" rel="noopener nofollow">WhatsApp</a> <a class="btn btn-primary" href="/contato/">Solicitar orçamento</a> <a class="btn btn-outline" href="tel:{TEL}">Ligar</a></div></div></section>
<section class="section"><div class="container"><div class="card"><h2>Links úteis</h2><ul><li><a href="/">Home</a></li><li><a href="/servicos/">Página geral de serviços</a></li><li><a href="/regioes/">Lista de regiões</a></li><li><a href="/contato/">Contato</a></li></ul></div></div></section>
</main>
<footer class="site-footer">
  <div class="container footer-grid">
    <div><h3>Ar Condicionado em Florianópolis</h3><p>Atendimento técnico para instalação, manutenção, limpeza, higienização, carga de gás e reinstalação em Florianópolis.</p></div>
    <div><h4>Links rápidos</h4><ul><li><a href="/">Início</a></li><li><a href="/servicos/">Serviços</a></li><li><a href="/regioes/">Regiões</a></li><li><a href="/blog/">Blog</a></li><li><a href="/contato/">Contato</a></li></ul></div>
    <div><h4>Serviços</h4><ul><li><a href="{servico_florianopolis_url('instalacao-de-ar-condicionado')}">Instalação de Ar-Condicionado</a></li><li><a href="{servico_florianopolis_url('manutencao-de-ar-condicionado')}">Manutenção de Ar-Condicionado</a></li><li><a href="{servico_florianopolis_url('limpeza-de-ar-condicionado')}">Limpeza de Ar-Condicionado</a></li><li><a href="{servico_florianopolis_url('higienizacao-de-ar-condicionado')}">Higienização de Ar-Condicionado</a></li><li><a href="{servico_florianopolis_url('carga-de-gas-de-ar-condicionado')}">Carga de Gás de Ar-Condicionado</a></li><li><a href="{servico_florianopolis_url('remocao-e-reinstalacao-de-ar-condicionado')}">Remoção e Reinstalação de Ar-Condicionado</a></li><li><a href="{servico_florianopolis_url('conserto-de-ar-condicionado')}">Conserto de Ar-Condicionado</a></li><li><a href="{servico_florianopolis_url('pmoc-de-ar-condicionado')}">PMOC de Ar-Condicionado</a></li></ul></div>
    <div><h4>Este hub</h4><p><a href="/servicos/">Ver visão geral dos serviços</a></p></div>
  </div>
  <div class="container footer-bottom"><p>© 2026 Ar Condicionado em Florianópolis. Todos os direitos reservados.</p><p><a href="tel:{TEL}">{PHONE}</a></p></div>
</footer>
<a class="floating-whatsapp" href="{WA}" target="_blank" rel="noopener nofollow" aria-label="Falar no WhatsApp">WhatsApp</a>
<script src="/js/script.js"></script>
</body>
</html>
"""
    return insert_social_meta_after_description(
        html,
        og_type="website",
        title=title,
        description=description,
        page_url=page_url_hub,
    )


def main() -> None:
    print("Geração de hubs desativada (nada gravado). Use /servicos/ e páginas *-em-florianopolis/ ou *-em-*-sc/.")


if __name__ == "__main__":
    main()

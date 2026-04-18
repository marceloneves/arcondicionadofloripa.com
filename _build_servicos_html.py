# -*- coding: utf-8 -*-
"""Gera servicos/index.html: quatro blocos (Florianópolis + cidades SC) com cards por tipo de serviço."""

from __future__ import annotations

import json
from pathlib import Path

from _fix_html_root_paths import apply_relative_paths_to_file
from _brand import LOGO_ALT, LOGO_URL
from _social_meta import insert_social_meta_after_description
from _rebuild_servico_main import CIDADES, SERVICE_KEYS, SERV_META

ROOT = Path(__file__).resolve().parent
BASE_URL = "https://arcondicionadofloripa.com"
FOUNDING_DATE = "2021-04-06"

IMG = "/images/ar-condicionado-florianopolis.webp"
IMG_W, IMG_H = 1408, 768


class _FirstLcpImg:
    """Primeira imagem da página: LCP; demais: lazy."""

    __slots__ = ("_done",)

    def __init__(self) -> None:
        self._done = False

    def img_extra_attrs(self) -> str:
        if self._done:
            return f' width="{IMG_W}" height="{IMG_H}" loading="lazy" decoding="async"'
        self._done = True
        return f' width="{IMG_W}" height="{IMG_H}" fetchpriority="high" loading="eager" decoding="async"'


def _href(sk: str, cidade_slug: str, suffix: str) -> str:
    if cidade_slug == "florianopolis":
        return f"/servico/{sk}-em-florianopolis/"
    return f"/servico/{sk}-em-{cidade_slug}-{suffix}/"


def build_collection_page_schema_jsonld() -> str:
    """Um único bloco: CollectionPage + ItemList (32 URLs, mesma ordem do HTML)."""
    urls: list[str] = []
    for sk in SERVICE_KEYS:
        urls.append(f"{BASE_URL}/servico/{sk}-em-florianopolis/")
    for slug in CIDADES:
        for sk in SERVICE_KEYS:
            urls.append(f"{BASE_URL}/servico/{sk}-em-{slug}-sc/")
    items = [{"@type": "ListItem", "position": i + 1, "url": u} for i, u in enumerate(urls)]
    payload = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Serviços de ar condicionado | Grande Florianópolis SC",
        "url": f"{BASE_URL}/servicos/",
        "description": (
            "Página com a listagem dos principais serviços de ar-condicionado em Florianópolis, "
            "São José, Palhoça e Biguaçu."
        ),
        "publisher": {
            "@type": "Organization",
            "@id": f"{BASE_URL}/#business",
            "name": "Ar Condicionado em Florianópolis",
            "url": f"{BASE_URL}/",
            "foundingDate": FOUNDING_DATE,
            "logo": {"@type": "ImageObject", "url": LOGO_URL},
        },
        "breadcrumb": {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Início", "item": f"{BASE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": "Serviços", "item": f"{BASE_URL}/servicos/"},
            ],
        },
        "mainEntity": {
            "@type": "ItemList",
            "name": "Lista de serviços de ar-condicionado por cidade",
            "itemListOrder": "https://schema.org/ItemListUnordered",
            "numberOfItems": len(items),
            "itemListElement": items,
        },
    }
    body = json.dumps(payload, ensure_ascii=False, indent=2)
    indented = "\n".join(f"  {line}" for line in body.splitlines())
    return f'  <script type="application/ld+json">\n{indented}\n  </script>'


def _card(sk: str, cidade_slug: str, suffix: str, nome_cidade: str, lcp: _FirstLcpImg) -> str:
    meta = SERV_META[sk]
    href = _href(sk, cidade_slug, suffix)
    label = f'{meta["titulo"]} em {nome_cidade}'
    extra = lcp.img_extra_attrs()
    return (
        f'<article class="card"><h3><a href="{href}">{label}</a></h3>'
        f'<a class="servico-card-img-link" href="{href}">'
        f'<img class="servico-card-img" src="{IMG}" alt="{label}"{extra}></a></article>'
    )


def _bloco_cidade(section_id: str, nome: str, cidade_slug: str, suffix: str, lcp: _FirstLcpImg) -> str:
    cards = "".join(_card(sk, cidade_slug, suffix, nome, lcp) for sk in SERVICE_KEYS)
    return f"""  <section class="section servicos-por-regiao" id="{section_id}">
    <div class="container">
      <h2 class="servicos-regiao-titulo">Serviços em {nome}</h2>
      <p class="servicos-regiao-meta">Páginas principais por tipo de serviço.</p>
      <div class="grid-3">{cards}</div>
    </div>
  </section>
"""


def build_page() -> str:
    lcp = _FirstLcpImg()
    blocos = [
        _bloco_cidade("servicos-florianopolis", "Florianópolis", "florianopolis", "florianopolis", lcp),
    ]
    for slug, meta in CIDADES.items():
        blocos.append(
            _bloco_cidade(f"servicos-{slug}", meta["nome"], slug, "sc", lcp),
        )
    main_sections = "\n\n".join(blocos)
    schema_ld = build_collection_page_schema_jsonld()
    page_title = "Serviços de ar condicionado | Grande Florianópolis SC"
    page_desc = (
        "Instalação a PMOC em Floripa, São José, Biguaçu e Palhoça. Abra sua cidade e peça orçamento no WhatsApp — técnico na Grande Florianópolis."
    )
    page_url_servicos = f"{BASE_URL}/servicos/"
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{page_title}</title>
  <meta name="description" content="{page_desc}">
  <link rel="preload" as="image" href="/images/ar-condicionado-florianopolis.webp">
  <link rel="stylesheet" href="/css/style.css">
{schema_ld}
</head>
<body>
<header class="site-header">
  <div class="container nav-wrap">
    <a class="logo" href="/"><img class="logo-img" src="/images/ar-condicionado-floripa-logo.webp" alt="{LOGO_ALT}" width="1024" height="558" loading="eager" decoding="async"><span class="logo-tagline">Ar-Condicionado em Florianópolis</span></a>
    <button class="menu-toggle" aria-label="Abrir menu" aria-expanded="false">☰</button>
    <nav class="main-nav" id="mainNav">
      <a href="/" class="">Início</a>
      <a href="/servicos/" class="active">Serviços</a>
      <a href="/regioes/" class="">Regiões Atendidas</a>
      <a href="/quem-somos/" class="">Quem Somos</a>
      <a href="/blog/" class="">Blog</a>
      <a href="/contato/" class="">Contato</a>
    </nav>
    <a class="btn btn-whats" href="https://wa.me/5548988105199?text=Olá!%20Quero%20orçamento%20de%20ar-condicionado%20em%20Florianópolis." target="_blank" rel="noopener nofollow">WhatsApp</a>
  </div>
</header>
<main>
  <section class="inner-banner">
    <div class="container">
      <h1>Serviços em Florianópolis</h1>
      <p>Escolha o tipo de serviço para ver a página principal em Florianópolis.</p>
    </div>
  </section>

{main_sections}

</main>
<footer class="site-footer">
  <div class="container footer-grid">
    <div>
      <h3>Ar Condicionado em Florianópolis</h3>
      <p>Atendimento técnico e rápido para instalação, manutenção, limpeza, higienização, carga de gás e reinstalação em Florianópolis desde 2021.</p>
    </div>
    <div><h4>Institucional</h4><ul><li><a href="https://arcondicionadofloripa.com/">Início</a></li><li><a href="https://arcondicionadofloripa.com/servicos/">Serviços</a></li><li><a href="/regioes/">Regiões Atendidas</a></li><li><a href="/quem-somos/">Quem Somos</a></li><li><a href="https://arcondicionadofloripa.com/blog/">Blog</a></li><li><a href="/contato/">Contato</a></li><li><a href="/politica-de-privacidade/">Política de Privacidade</a></li></ul></div>
    <div><h4>Serviços</h4><ul><li><a href="/servico/instalacao-de-ar-condicionado-em-florianopolis/">Instalação de Ar-Condicionado</a></li><li><a href="/servico/manutencao-de-ar-condicionado-em-florianopolis/">Manutenção de Ar-Condicionado</a></li><li><a href="/servico/limpeza-de-ar-condicionado-em-florianopolis/">Limpeza de Ar-Condicionado</a></li><li><a href="/servico/higienizacao-de-ar-condicionado-em-florianopolis/">Higienização de Ar-Condicionado</a></li><li><a href="/servico/carga-de-gas-de-ar-condicionado-em-florianopolis/">Carga de Gás de Ar-Condicionado</a></li><li><a href="/servico/remocao-e-reinstalacao-de-ar-condicionado-em-florianopolis/">Remoção e Reinstalação de Ar-Condicionado</a></li><li><a href="/servico/conserto-de-ar-condicionado-em-florianopolis/">Conserto de Ar-Condicionado</a></li><li><a href="/servico/pmoc-de-ar-condicionado-em-florianopolis/">PMOC de Ar-Condicionado</a></li></ul></div>
    <div><h4>Cidades</h4><ul><li><a href="/servicos/#servicos-florianopolis">Florianópolis</a></li><li><a href="/regioes/#sao-jose">São José</a></li><li><a href="/regioes/#biguacu">Biguaçu</a></li><li><a href="/regioes/#palhoca">Palhoça</a></li></ul></div>
  </div>
  <div class="container footer-bottom"><p class="footer-address">Rodovia Armando Calil Bullos, 630 — Vargem Grande, Florianópolis - SC, 88056-618</p><p>© 2026 Ar Condicionado em Florianópolis. Todos os direitos reservados.</p><p><a href="tel:+5548988105199">(48) 98810-5199</a></p><p>Fale conosco: <a href="mailto:marcelo@arcondicionadofloripa.com">marcelo@arcondicionadofloripa.com</a></p></div>
</footer>
<a class="floating-whatsapp" href="https://wa.me/5548988105199?text=Olá!%20Quero%20orçamento%20de%20ar-condicionado%20em%20Florianópolis." target="_blank" rel="noopener nofollow" aria-label="Falar no WhatsApp">WhatsApp</a>
<script src="/js/script.js"></script>
</body>
</html>
"""
    return insert_social_meta_after_description(
        html,
        og_type="website",
        title=page_title,
        description=page_desc,
        page_url=page_url_servicos,
    )


def main() -> None:
    out = ROOT / "servicos" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_page(), encoding="utf-8")
    apply_relative_paths_to_file(out, ROOT)
    print("OK:", out.relative_to(ROOT))


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""Gera servicos.html: quatro blocos (Florianópolis + cidades SC) com cards por tipo de serviço."""

from __future__ import annotations

from pathlib import Path

from _rebuild_servico_main import CIDADES, SERVICE_KEYS, SERV_META

ROOT = Path(__file__).resolve().parent

IMG = "images/ar-condicionado-florianopolis.webp"
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
        return f"servico/{sk}-em-florianopolis.html"
    return f"servico/{sk}-em-{cidade_slug}-{suffix}.html"


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
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Serviços de Ar-Condicionado | Florianópolis e Grande Florianópolis</title>
  <meta name="description" content="Serviços de ar-condicionado com páginas principais por cidade: Florianópolis, São José, Biguaçu e Palhoça.">
  <link rel="preload" as="image" href="/images/ar-condicionado-florianopolis.webp">
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
      <a href="regioes.html" class="">Regiões Atendidas</a>
      <a href="quem-somos.html" class="">Quem Somos</a>
      <a href="blog.html" class="">Blog</a>
      <a href="contato.html" class="">Contato</a>
    </nav>
    <a class="btn btn-whats" href="https://wa.me/5548988105199?text=Olá!%20Quero%20orçamento%20de%20ar-condicionado%20em%20Florianópolis." target="_blank" rel="noopener">WhatsApp</a>
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
    <div><h4>Institucional</h4><ul><li><a href="/index.html">Início</a></li><li><a href="/servicos.html">Serviços</a></li><li><a href="/regioes.html">Regiões Atendidas</a></li><li><a href="/quem-somos.html">Quem Somos</a></li><li><a href="/blog.html">Blog</a></li><li><a href="/contato.html">Contato</a></li><li><a href="/politica-de-privacidade.html">Política de Privacidade</a></li></ul></div>
    <div><h4>Serviços</h4><ul><li><a href="/servicos.html#instalacao-de-ar-condicionado">Instalação de Ar-Condicionado</a></li><li><a href="/servicos.html#manutencao-de-ar-condicionado">Manutenção de Ar-Condicionado</a></li><li><a href="/servicos.html#limpeza-de-ar-condicionado">Limpeza de Ar-Condicionado</a></li><li><a href="/servicos.html#higienizacao-de-ar-condicionado">Higienização de Ar-Condicionado</a></li><li><a href="/servicos.html#carga-de-gas-de-ar-condicionado">Carga de Gás de Ar-Condicionado</a></li><li><a href="/servicos.html#remocao-e-reinstalacao-de-ar-condicionado">Remoção e Reinstalação de Ar-Condicionado</a></li><li><a href="/servicos.html#conserto-de-ar-condicionado">Conserto de Ar-Condicionado</a></li><li><a href="/servicos.html#pmoc-de-ar-condicionado">PMOC de Ar-Condicionado</a></li></ul></div>
    <div><h4>Cidades</h4><ul><li><a href="/servicos.html#servicos-florianopolis">Florianópolis</a></li><li><a href="/regioes/sao-jose-sc.html">São José</a></li><li><a href="/regioes/biguacu-sc.html">Biguaçu</a></li><li><a href="/regioes/palhoca-sc.html">Palhoça</a></li></ul></div>
  </div>
  <div class="container footer-bottom"><p class="footer-address">Rodovia Armando Calil Bullos, 410 — Vargem Grande, Florianópolis - SC, 88056-618</p><p>© 2026 Ar Condicionado em Florianópolis. Todos os direitos reservados.</p><p><a href="tel:+5548988105199">(48) 98810-5199</a></p><p>Fale conosco: <a href="mailto:marcelo@arcondicionadofloripa.com">marcelo@arcondicionadofloripa.com</a></p></div>
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

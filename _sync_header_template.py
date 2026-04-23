#!/usr/bin/env python3
"""Padroniza o header principal em todos os HTMLs do projeto.

Objetivo:
- manter o menu principal sem item "Calculadora BTU"
- manter botão chamativo "Calculadora BTU" ao lado do WhatsApp
- preservar logo existente e link WhatsApp já configurado em cada página

Uso:
  python3 _sync_header_template.py
"""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent

HEADER_RE = re.compile(
    r"<header class=\"site-header\">.*?</header>",
    re.DOTALL,
)
LOGO_RE = re.compile(r"<a class=\"logo\"[^>]*>.*?</a>", re.DOTALL)
WPP_RE = re.compile(
    r"<a class=\"btn (btn-whats|btn-whatsapp)\"[^>]*href=\"([^\"]+)\"[^>]*>WhatsApp</a>",
    re.DOTALL,
)


def rel_prefix(html_path: Path) -> str:
    rel = html_path.relative_to(ROOT)
    depth = len(rel.parts) - 1
    return "./" if depth == 0 else "../" * depth


def page_active(rel_path: str) -> str:
    if rel_path == "index.html":
        return "home"
    if rel_path.startswith("servicos/") or rel_path.startswith("servico/"):
        return "servicos"
    if rel_path.startswith("regioes/"):
        return "regioes"
    if rel_path.startswith("quem-somos/"):
        return "quem"
    if rel_path.startswith("blog/"):
        return "blog"
    if rel_path.startswith("contato/"):
        return "contato"
    return ""


def nav_link(href: str, label: str, active: bool) -> str:
    cls = ' class="active"' if active else ""
    return f'      <a href="{href}"{cls}>{label}</a>'


def build_nav(prefix: str, active_key: str) -> str:
    items = [
        (f"{prefix}", "Início", active_key == "home"),
        (f"{prefix}servicos/", "Serviços", active_key == "servicos"),
        (f"{prefix}regioes/", "Regiões Atendidas", active_key == "regioes"),
        (f"{prefix}quem-somos/", "Quem Somos", active_key == "quem"),
        (f"{prefix}blog/", "Blog", active_key == "blog"),
        (f"{prefix}contato/", "Contato", active_key == "contato"),
    ]
    links = "\n".join(nav_link(href, label, active) for href, label, active in items)
    return f'<nav class="main-nav" id="mainNav">\n{links}\n    </nav>'


def sync_file(path: Path) -> bool:
    html = path.read_text(encoding="utf-8")
    header_match = HEADER_RE.search(html)
    if not header_match:
        return False

    current_header = header_match.group(0)

    logo_match = LOGO_RE.search(current_header)
    if not logo_match:
        return False
    logo_html = logo_match.group(0)

    wpp_match = WPP_RE.search(current_header)
    if not wpp_match:
        return False
    wpp_class = wpp_match.group(1)
    wpp_href = wpp_match.group(2)

    rel_path = path.relative_to(ROOT).as_posix()
    prefix = rel_prefix(path)
    active_key = page_active(rel_path)
    calc_href = f"{prefix}calculadora-btu/"

    new_header = (
        '<header class="site-header">\n'
        '  <div class="container nav-wrap">\n'
        f"    {logo_html}\n"
        '    <button class="menu-toggle" aria-label="Abrir menu" aria-expanded="false">☰</button>\n'
        f"    {build_nav(prefix, active_key)}\n"
        f'    <a class="btn btn-calc" href="{calc_href}">Calculadora BTU</a>\n'
        f'    <a class="btn {wpp_class}" href="{wpp_href}" target="_blank" rel="noopener nofollow">WhatsApp</a>\n'
        "  </div>\n"
        "</header>"
    )

    if new_header == current_header:
        return False

    updated = html[: header_match.start()] + new_header + html[header_match.end() :]
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> None:
    changed = 0
    for html_file in sorted(ROOT.rglob("*.html")):
        if sync_file(html_file):
            changed += 1
    print(f"Header sincronizado em {changed} arquivos.")


if __name__ == "__main__":
    main()


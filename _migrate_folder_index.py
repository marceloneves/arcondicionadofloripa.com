#!/usr/bin/env python3
"""
Migra páginas .html para pastas com index.html, normaliza links internos e, no fim, aplica caminhos relativos (CSS/JS).
Execute uma vez na raiz do projeto: python3 _migrate_folder_index.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from _fix_html_root_paths import apply_relative_paths_to_file

ROOT = Path(__file__).resolve().parent
BASE = "https://arcondicionadofloripa.com"


def transform_html(html: str) -> str:
    # --- Assets: sempre a partir da raiz ---
    html = re.sub(r'href="\.\./\.\./css/style\.css"', 'href="/css/style.css"', html)
    html = re.sub(r'href="\.\./css/style\.css"', 'href="/css/style.css"', html)
    html = re.sub(r'href="css/style\.css"', 'href="/css/style.css"', html)

    html = re.sub(r'src="\.\./\.\./images/', 'src="/images/', html)
    html = re.sub(r'src="\.\./images/', 'src="/images/', html)
    html = re.sub(r'src="images/', 'src="/images/', html)

    html = re.sub(r'href="\.\./\.\./js/script\.js"', 'href="/js/script.js"', html)
    html = re.sub(r'src="\.\./\.\./js/script\.js"', 'src="/js/script.js"', html)
    html = re.sub(r'src="\.\./js/script\.js"', 'src="/js/script.js"', html)
    html = re.sub(r'src="js/script\.js"', 'src="/js/script.js"', html)

    # --- Domínio: serviço e blog (com ou sem #fragmento) ---
    html = re.sub(
        rf"({re.escape(BASE)})(/servico/[a-z0-9-]+)\.html",
        r"\1\2/",
        html,
        flags=re.IGNORECASE,
    )
    html = re.sub(
        rf"({re.escape(BASE)})(/blog/[a-z0-9-]+)\.html",
        r"\1\2/",
        html,
        flags=re.IGNORECASE,
    )

    # Páginas “top” .html no domínio
    for slug in (
        "servicos",
        "contato",
        "blog",
        "quem-somos",
        "regioes",
        "politica-de-privacidade",
    ):
        html = html.replace(f"{BASE}/{slug}.html", f"{BASE}/{slug}/")
        html = html.replace(f"{BASE}/{slug}.html#", f"{BASE}/{slug}/#")

    # Caminhos absolutos /… .html (atributo href)
    html = re.sub(r'href="/blog/([a-z0-9-]+)\.html"', r'href="/blog/\1/"', html)
    html = re.sub(r'href="/servico/([a-z0-9-]+)\.html"', r'href="/servico/\1/"', html)
    html = re.sub(r'"/servicos\.html#', '"/servicos/#', html)
    html = html.replace('"/servicos.html"', '"/servicos/"')
    html = html.replace('"/contato.html"', '"/contato/"')
    html = html.replace('"/blog.html"', '"/blog/"')
    html = html.replace('"/regioes.html"', '"/regioes/"')
    html = html.replace('"/quem-somos.html"', '"/quem-somos/"')
    html = html.replace('"/politica-de-privacidade.html"', '"/politica-de-privacidade/"')
    html = re.sub(r'"/regioes/([a-z0-9-]+)\.html"', r'"/regioes/\1/"', html)

    # Relativos nav / rodapé (artigos e serviços com slug)
    html = re.sub(r'href="\.\./blog/([a-z0-9-]+)\.html"', r'href="/blog/\1/"', html)
    html = re.sub(r'href="\.\./servico/([a-z0-9-]+)\.html"', r'href="/servico/\1/"', html)
    for a, b in [
        ("../index.html", "/"),
        ("../servicos.html", "/servicos/"),
        ("../regioes.html", "/regioes/"),
        ("../quem-somos.html", "/quem-somos/"),
        ("../blog.html", "/blog/"),
        ("../contato.html", "/contato/"),
        ("../politica-de-privacidade.html", "/politica-de-privacidade/"),
    ]:
        html = html.replace(f'href="{a}"', f'href="{b}"')

    # Raiz: index e páginas irmãs
    html = html.replace('href="index.html"', 'href="/"')
    html = re.sub(r'href="servicos\.html"', 'href="/servicos/"', html)
    html = re.sub(r'href="regioes\.html"', 'href="/regioes/"', html)
    html = re.sub(r'href="quem-somos\.html"', 'href="/quem-somos/"', html)
    html = re.sub(r'href="blog\.html"', 'href="/blog/"', html)
    html = re.sub(r'href="contato\.html"', 'href="/contato/"', html)
    html = re.sub(r'href="politica-de-privacidade\.html"', 'href="/politica-de-privacidade/"', html)

    # blog/foo.html e blog/foo.html (relativo em listagens na raiz)
    html = re.sub(r'href="blog/([a-z0-9-]+)\.html"', r'href="/blog/\1/"', html)
    html = re.sub(r'href="blog/([a-z0-9-]+)\.html#', r'href="/blog/\1/#', html)

    # rel=prev/next
    html = re.sub(r'href="blog/pagina-([23])\.html"', r'href="/blog/pagina-\1/"', html)

    # servico/foo.html relativo (sem ../) — antes do catch-all de artigos do blog
    html = re.sub(r'href="servico/([a-z0-9-]+)\.html"', r'href="/servico/\1/"', html)

    # Artigos: links entre posts (slug.html)
    html = re.sub(r'href="([a-z][a-z0-9-]{3,120})\.html"', r'href="/blog/\1/"', html)

    # JSON-LD em linha única: URLs .html restantes no nosso domínio
    html = re.sub(rf'({re.escape(BASE)}/servico/[a-z0-9-]+)\.html', r"\1/", html)
    html = re.sub(rf'({re.escape(BASE)}/blog/[a-z0-9-]+)\.html', r"\1/", html)

    # preload / href já absolutos com /images — ok

    return html


def collect_moves() -> list[tuple[Path, Path]]:
    moves: list[tuple[Path, Path]] = []
    blog_dir = ROOT / "blog"
    if blog_dir.is_dir():
        for p in sorted(blog_dir.glob("*.html")):
            moves.append((p, blog_dir / p.stem / "index.html"))

    for name in (
        "servicos.html",
        "contato.html",
        "quem-somos.html",
        "regioes.html",
        "politica-de-privacidade.html",
        "blog.html",
    ):
        src = ROOT / name
        if src.is_file():
            moves.append((src, ROOT / name.replace(".html", "") / "index.html"))

    serv_dir = ROOT / "servico"
    if serv_dir.is_dir():
        for p in sorted(serv_dir.glob("*.html")):
            moves.append((p, serv_dir / p.stem / "index.html"))

    return moves


def write_vercel_json(redirects: list[tuple[str, str]]) -> None:
    data = {
        "$schema": "https://openapi.vercel.sh/vercel.json",
        "trailingSlash": True,
        "redirects": [
            {"source": src, "destination": dst, "permanent": True}
            for src, dst in redirects
        ],
    }
    (ROOT / "vercel.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    moves = collect_moves()
    if not moves:
        print("Nada para migrar.")
        return

    # Redirects: de .html para /
    redirs: list[tuple[str, str]] = []
    for src, dst in moves:
        rel = src.relative_to(ROOT).as_posix()
        if rel == "index.html":
            continue
        if rel.endswith(".html"):
            no_ext = "/" + rel[: -len(".html")]
            if not no_ext.endswith("/"):
                no_ext += "/"
            redirs.append(("/" + rel, no_ext))

    for src, dst in moves:
        dst.parent.mkdir(parents=True, exist_ok=True)
        raw = src.read_text(encoding="utf-8")
        out = transform_html(raw)
        dst.write_text(out, encoding="utf-8")
        print("OK", src.relative_to(ROOT), "->", dst.relative_to(ROOT))
        src.unlink()

    write_vercel_json(redirs)
    print("vercel.json atualizado com", len(redirs), "redirects e trailingSlash.")

    nfix = 0
    for p in sorted(ROOT.rglob("*.html")):
        if ".git" in p.parts:
            continue
        if apply_relative_paths_to_file(p, ROOT):
            nfix += 1
    print("Caminhos relativos (CSS/links):", nfix, "ficheiros.")


if __name__ == "__main__":
    main()

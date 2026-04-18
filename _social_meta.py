# -*- coding: utf-8 -*-
"""Open Graph e Twitter Cards — URLs e imagem alinhados a _brand.BASE_URL."""

from __future__ import annotations

import re
from html import escape, unescape
from pathlib import Path

from _brand import BASE_URL

OG_SITE_NAME = "Ar Condicionado Floripa"
OG_LOCALE = "pt_BR"
# Hero usado em serviços/home; dimensões reais do webp (evita distorção em previews)
OG_IMAGE_URL = f"{BASE_URL}/images/ar-condicionado-florianopolis.webp"
OG_IMAGE_WIDTH = 1408
OG_IMAGE_HEIGHT = 768

_SOCIAL_BLOCK_RE = re.compile(
    r"\s*<!--\s*soc-meta:start\s*-->.*?<!--\s*soc-meta:end\s*-->\s*",
    re.DOTALL | re.IGNORECASE,
)


def social_meta_lines(
    *,
    og_type: str,
    title: str,
    description: str,
    page_url: str,
    image_url: str | None = None,
    image_width: int | None = None,
    image_height: int | None = None,
) -> str:
    """Uma linha por tag; indentação de 2 espaços (dentro do <head>)."""
    img = image_url or OG_IMAGE_URL
    iw = OG_IMAGE_WIDTH if image_width is None else image_width
    ih = OG_IMAGE_HEIGHT if image_height is None else image_height
    eq = escape
    parts = [
        "  <!-- soc-meta:start -->",
        f'  <meta property="og:type" content="{eq(og_type, quote=True)}">',
        f'  <meta property="og:title" content="{eq(title, quote=True)}">',
        f'  <meta property="og:description" content="{eq(description, quote=True)}">',
        f'  <meta property="og:url" content="{eq(page_url, quote=True)}">',
        f'  <meta property="og:site_name" content="{eq(OG_SITE_NAME, quote=True)}">',
        f'  <meta property="og:locale" content="{eq(OG_LOCALE, quote=True)}">',
        f'  <meta property="og:image" content="{eq(img, quote=True)}">',
        f'  <meta property="og:image:width" content="{iw}">',
        f'  <meta property="og:image:height" content="{ih}">',
        '  <meta name="twitter:card" content="summary_large_image">',
        f'  <meta name="twitter:title" content="{eq(title, quote=True)}">',
        f'  <meta name="twitter:description" content="{eq(description, quote=True)}">',
        f'  <meta name="twitter:image" content="{eq(img, quote=True)}">',
        "  <!-- soc-meta:end -->",
    ]
    return "\n".join(parts)


def strip_social_meta_block(html: str) -> str:
    return _SOCIAL_BLOCK_RE.sub("\n", html, count=1)


def insert_social_meta_after_description(
    html: str,
    *,
    og_type: str,
    title: str,
    description: str,
    page_url: str,
    image_url: str | None = None,
    image_width: int | None = None,
    image_height: int | None = None,
) -> str:
    """Remove bloco anterior (se houver) e reinsere após <meta name="description" …>."""
    html = strip_social_meta_block(html)
    block = social_meta_lines(
        og_type=og_type,
        title=title,
        description=description,
        page_url=page_url,
        image_url=image_url,
        image_width=image_width,
        image_height=image_height,
    )
    new_html, n = re.subn(
        r"(<meta\s+name=\"description\"\s+content=\"[^\"]*\"\s*/?>)",
        r"\1\n" + block,
        html,
        count=1,
        flags=re.DOTALL,
    )
    if n == 1:
        return new_html
    # Fallback: antes de </head>
    block2 = "\n" + block + "\n"
    new_html, n2 = re.subn(r"(</head>)", block2 + r"\1", html, count=1, flags=re.IGNORECASE)
    if n2 == 1:
        return new_html
    return html


def absolute_url_for_page(path: Path, root: Path) -> str:
    """URL canónica (com / final) para um index.html ou .html na raiz do site."""
    rel = path.relative_to(root).as_posix()
    if rel == "index.html":
        return f"{BASE_URL}/"
    if rel.endswith("/index.html"):
        return f"{BASE_URL}/{rel[: -len('index.html')]}"
    if rel.endswith(".html"):
        return f"{BASE_URL}/{rel[:-5]}/"
    return f"{BASE_URL}/"


def infer_og_type(path: Path, root: Path) -> str:
    rel = path.relative_to(root)
    parts = rel.parts
    if len(parts) >= 3 and parts[0] == "blog" and parts[-1] == "index.html":
        slug = parts[1]
        if slug in ("pagina-2", "pagina-3"):
            return "website"
        return "article"
    if len(parts) == 2 and parts[0] == "blog" and parts[1] == "index.html":
        return "website"
    return "website"


def sync_file(path: Path, root: Path) -> bool:
    """Lê title/description/canonical e injeta metadados sociais. Retorna True se alterou."""
    html = path.read_text(encoding="utf-8")
    t_m = re.search(r"<title>([^<]*)</title>", html, re.DOTALL | re.IGNORECASE)
    d_m = re.search(
        r'<meta\s+name="description"\s+content="([^"]*)"\s*/?>',
        html,
        re.DOTALL | re.IGNORECASE,
    )
    if not t_m or not d_m:
        return False
    title = unescape(t_m.group(1).strip())
    description = unescape(d_m.group(1).strip())
    c_m = re.search(r'<link\s+rel="canonical"\s+href="([^"]+)"', html, re.IGNORECASE)
    page_url = c_m.group(1).strip() if c_m else absolute_url_for_page(path, root)
    og_type = infer_og_type(path, root)
    new_html = insert_social_meta_after_description(
        html,
        og_type=og_type,
        title=title,
        description=description,
        page_url=page_url,
    )
    if new_html != html:
        path.write_text(new_html, encoding="utf-8")
        return True
    return False


def sync_all_html(root: Path) -> int:
    """Atualiza todos os *.html sob root (exceto __pycache__ e ocultos)."""
    n = 0
    for p in sorted(root.rglob("*.html")):
        if any(part.startswith(".") for part in p.parts):
            continue
        if sync_file(p, root):
            n += 1
    return n

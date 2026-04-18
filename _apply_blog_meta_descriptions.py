#!/usr/bin/env python3
"""Atualiza <meta name="description"> nas páginas do blog a partir de _blog_meta_descriptions_data."""
from __future__ import annotations

import re
import sys
from html import escape
from pathlib import Path

from _blog_meta_descriptions_data import META_BY_SLUG

ROOT = Path(__file__).resolve().parent
BLOG = ROOT / "blog"

META_RE = re.compile(
    r'<meta\s+name="description"\s+content="[^"]*"\s*/?>',
    re.IGNORECASE,
)


def path_for_slug(slug: str) -> Path:
    if slug == "index":
        return BLOG / "index.html"
    return BLOG / slug / "index.html"


def main() -> int:
    n = 0
    for slug, desc in META_BY_SLUG.items():
        path = path_for_slug(slug)
        if not path.is_file():
            print("AVISO: não encontrado:", path.relative_to(ROOT), file=sys.stderr)
            continue
        html = path.read_text(encoding="utf-8")
        new_tag = f'<meta name="description" content="{escape(desc, quote=True)}">'
        new_html, c = META_RE.subn(new_tag, html, count=1)
        if c != 1:
            print("AVISO: meta description não substituída:", path.relative_to(ROOT), file=sys.stderr)
            continue
        if new_html != html:
            path.write_text(new_html, encoding="utf-8")
            n += 1
    print(f"OK: {n} ficheiros do blog com meta description atualizada.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

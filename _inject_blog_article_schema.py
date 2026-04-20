#!/usr/bin/env python3
"""Injeta JSON-LD (BlogPosting + BreadcrumbList + FAQPage) nos artigos do blog."""
from __future__ import annotations

import html as html_module
import json
import re
import sys
from pathlib import Path

from _fix_html_root_paths import apply_relative_paths_to_file
from _brand import LOGO_URL

ROOT = Path(__file__).resolve().parent
BLOG = ROOT / "blog"
BASE = "https://arcondicionadofloripa.com"
FOUNDING_DATE = "2021-04-06"

AUTHOR = {
    "@type": "Person",
    "@id": f"{BASE}/#author-marcelo-menezes",
    "name": "Marcelo Menezes",
    "description": (
        "Técnico em refrigeração em Florianópolis, com mais de 8 anos de experiência em "
        "instalação, manutenção e diagnóstico de sistemas de ar-condicionado e refrigeração."
    ),
}
PUBLISHER = {
    "@type": "Organization",
    "@id": f"{BASE}/#business",
    "name": "Ar Condicionado em Florianópolis",
    "url": f"{BASE}/",
    "foundingDate": FOUNDING_DATE,
    "logo": {"@type": "ImageObject", "url": LOGO_URL},
}
SPEAKABLE_SELECTORS = [
    "main .inner-banner h1",
    "main .inner-banner p:nth-of-type(2)",
]

MARKER_START = "<!-- blog-schema:start -->"
MARKER_END = "<!-- blog-schema:end -->"
# Linha do stylesheet (href relativo ou /css/…), antes do bloco JSON-LD injetado.
STYLESHEET_LINK = re.compile(
    r"^(\s*<link rel=\"stylesheet\" href=\"[^\"]*css/style\.css\">)\s*$",
    re.MULTILINE,
)


def is_faq_h2(title: str) -> bool:
    t = title.strip()
    sl = t.lower()
    if sl == "faq":
        return True
    if sl.startswith("faq"):
        return True
    if "perguntas frequentes" in sl:
        return True
    if "tudo sobre o preço da manutenção do seu ar" in sl:
        return True
    return False


def html_to_plain(fragment: str) -> str:
    t = re.sub(r"<[^>]+>", " ", fragment)
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"\s+([.,;:!?])", r"\1", t)
    return html_module.unescape(t)


def extract_faq_section(html: str) -> str | None:
    for m in re.finditer(r"<h2>([^<]+)</h2>", html):
        if is_faq_h2(m.group(1)):
            start = m.end()
            end = html.find("</section>", start)
            if end == -1:
                return None
            return html[start:end]
    return None


def parse_faq_pairs(section_html: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for m in re.finditer(r"<h3>([^<]+)</h3>", section_html):
        q = m.group(1).strip()
        pos = m.end()
        nxt = section_html.find("<h3>", pos)
        block = section_html[pos : nxt if nxt != -1 else len(section_html)]
        texts: list[str] = []
        for pm in re.finditer(r"<p[^>]*>([\s\S]*?)</p>", block):
            texts.append(html_to_plain(pm.group(1)))
        answer = " ".join(texts).strip()
        if q and answer:
            pairs.append((q, answer))
    return pairs


def strip_old_schema(html: str) -> str:
    block = re.compile(
        rf"\n\s*{re.escape(MARKER_START)}[\s\S]*?{re.escape(MARKER_END)}\s*",
        re.MULTILINE,
    )
    return block.sub("\n", html, count=1)


def build_graph(
    *,
    slug: str,
    headline: str,
    description: str,
    date_iso: str,
    faq_pairs: list[tuple[str, str]],
) -> dict:
    base_path = f"{BASE}/blog/{slug}/"
    article_id = f"{base_path}#article"
    breadcrumb_id = f"{base_path}#breadcrumb"
    faq_id = f"{base_path}#faq"

    blog_posting = {
        "@type": "BlogPosting",
        "@id": article_id,
        "mainEntityOfPage": {"@type": "WebPage", "@id": base_path},
        "speakable": {
            "@type": "SpeakableSpecification",
            "cssSelector": SPEAKABLE_SELECTORS,
        },
        "headline": headline,
        "description": description,
        "datePublished": date_iso,
        "dateModified": date_iso,
        "inLanguage": "pt-BR",
        "articleSection": "Blog",
        "author": AUTHOR,
        "publisher": PUBLISHER,
    }

    breadcrumb = {
        "@type": "BreadcrumbList",
        "@id": breadcrumb_id,
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Início",
                "item": f"{BASE}/",
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": "Blog",
                "item": f"{BASE}/blog/",
            },
            {
                "@type": "ListItem",
                "position": 3,
                "name": headline,
                "item": base_path,
            },
        ],
    }

    main_entity = [
        {
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a},
        }
        for q, a in faq_pairs
    ]

    faq_page = {
        "@type": "FAQPage",
        "@id": faq_id,
        "breadcrumb": {"@id": breadcrumb_id},
        "mainEntity": main_entity,
    }

    return {"@context": "https://schema.org", "@graph": [blog_posting, breadcrumb, faq_page]}


def process_file(path: Path) -> tuple[bool, str]:
    raw = path.read_text(encoding="utf-8")
    html = strip_old_schema(raw)

    slug = path.parent.name if path.name == "index.html" else path.stem
    tm = re.search(r'<time datetime="(\d{4}-\d{2}-\d{2})"', html)
    if not tm:
        return False, "sem <time datetime>"
    date_iso = tm.group(1)

    h1m = re.search(r"<h1>([^<]+)</h1>", html)
    if not h1m:
        return False, "sem <h1>"
    headline = h1m.group(1).strip()

    descm = re.search(r'<meta name="description" content="([^"]*)"', html)
    if not descm:
        return False, "sem meta description"
    description = html_module.unescape(descm.group(1).strip())

    sec = extract_faq_section(html)
    if not sec:
        return False, "bloco FAQ não encontrado"
    pairs = parse_faq_pairs(sec)
    if not pairs:
        return False, "FAQ sem pares h3+p"

    graph = build_graph(
        slug=slug,
        headline=headline,
        description=description,
        date_iso=date_iso,
        faq_pairs=pairs,
    )
    json_str = json.dumps(graph, ensure_ascii=False, indent=2)
    injection = (
        f"\n  {MARKER_START}\n"
        f'  <script type="application/ld+json">\n{json_str}\n  </script>\n'
        f"  {MARKER_END}\n"
    )

    sm = STYLESHEET_LINK.search(html)
    if not sm:
        return False, "linha do stylesheet não encontrada"
    insert_at = sm.end()
    new_html = html[:insert_at] + injection + html[insert_at:]
    path.write_text(new_html, encoding="utf-8")
    apply_relative_paths_to_file(path, ROOT)
    return True, f"{len(pairs)} FAQs"


def main() -> int:
    skip = {"pagina-2", "pagina-3"}
    files = sorted(
        p for p in BLOG.glob("*/index.html") if p.parent.name not in skip
    )
    errors: list[str] = []
    for p in files:
        ok, msg = process_file(p)
        if not ok:
            errors.append(f"{p.name}: {msg}")
            print(f"ERRO {p.name}: {msg}", file=sys.stderr)
        else:
            print(f"OK {p.name} ({msg})")

    if errors:
        print(f"\nFalhas: {len(errors)}", file=sys.stderr)
        return 1
    print(f"Total: {len(files)} artigos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

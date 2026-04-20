from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent
BASE_URL = "https://arcondicionadofloripa.com"

# Publicação dos artigos do blog no sitemap: intervalo de 2 dias entre posts, a partir desta data (ordem = nomes de arquivo A–Z).
BLOG_PUBLICATION_START = date(2026, 3, 1)

_MESES_PT = (
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
)


def _blog_article_files_sorted() -> list[Path]:
    """HTML de post: blog/<slug>/index.html (exclui paginação)."""
    blog = ROOT / "blog"
    return sorted(
        p
        for p in blog.glob("*/index.html")
        if p.is_file() and p.parent.name not in ("pagina-2", "pagina-3")
    )


def _publication_date_for_blog_article(path: Path) -> date:
    files = _blog_article_files_sorted()
    try:
        idx = files.index(path.resolve())
    except ValueError as e:
        raise ValueError(f"Arquivo de blog fora da lista de artigos: {path}") from e
    return BLOG_PUBLICATION_START + timedelta(days=idx * 2)


def _format_date_pt_br(d: date) -> str:
    return f"{d.day} de {_MESES_PT[d.month - 1]} de {d.year}"


def _blog_sitemap_lastmod(path: Path) -> str:
    """lastmod no sitemap: data editorial do post; páginas 2/3 = após o último artigo (mesmo passo de 2 dias)."""
    if path.parent.name == "pagina-2":
        n = len(_blog_article_files_sorted())
        return (BLOG_PUBLICATION_START + timedelta(days=n * 2)).isoformat()
    if path.parent.name == "pagina-3":
        n = len(_blog_article_files_sorted())
        return (BLOG_PUBLICATION_START + timedelta(days=n * 2 + 2)).isoformat()
    if path.parent.parent.resolve() == (ROOT / "blog").resolve() and path.name == "index.html":
        return _publication_date_for_blog_article(path).isoformat()
    return _lastmod_iso(path)


def _sync_blog_post_meta_in_html(path: Path) -> None:
    """Insere ou atualiza data abaixo do <h1> do banner (somente artigos)."""
    if path.parent.name in ("pagina-2", "pagina-3"):
        return
    d = _publication_date_for_blog_article(path)
    iso = d.isoformat()
    display = _format_date_pt_br(d)
    text = path.read_text(encoding="utf-8")
    banner_start = text.find('<section class="inner-banner">')
    if banner_start == -1:
        return
    banner_end = text.find("</section>", banner_start)
    if banner_end == -1:
        return
    before = text[:banner_start]
    banner = text[banner_start:banner_end]
    after = text[banner_end:]
    banner = re.sub(
        r"<p class=\"blog-post-meta\">\s*<time[^>]*>.*?</time>\s*</p>\s*",
        "",
        banner,
        count=1,
        flags=re.DOTALL,
    )
    h1_close = banner.find("</h1>")
    if h1_close == -1:
        return
    insert_at = h1_close + len("</h1>")
    block = (
        f'\n    <p class="blog-post-meta">'
        f'<time datetime="{iso}">{display}</time></p>'
    )
    new_banner = banner[:insert_at] + block + banner[insert_at:]
    path.write_text(before + new_banner + after, encoding="utf-8")


@dataclass(frozen=True)
class UrlItem:
    loc: str
    lastmod: str


def _lastmod_iso(path: Path) -> str:
    dt = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return dt.date().isoformat()


def _loc_for(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return f"{BASE_URL}/"
    if rel.endswith("/index.html"):
        prefix = rel[: -len("/index.html")]
        return f"{BASE_URL}/{prefix}/"
    return f"{BASE_URL}/{rel}"


def _write_urlset(out_path: Path, items: Iterable[UrlItem]) -> None:
    urls = []
    for it in items:
        urls.append(
            "  <url>\n"
            f"    <loc>{it.loc}</loc>\n"
            f"    <lastmod>{it.lastmod}</lastmod>\n"
            "  </url>"
        )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )
    out_path.write_text(xml, encoding="utf-8")


def _write_sitemapindex(out_path: Path, sitemap_files: list[Path]) -> None:
    sitems = []
    now = datetime.now(tz=timezone.utc).date().isoformat()
    for p in sitemap_files:
        loc = f"{BASE_URL}/{p.name}"
        sitems.append(
            "  <sitemap>\n"
            f"    <loc>{loc}</loc>\n"
            f"    <lastmod>{now}</lastmod>\n"
            "  </sitemap>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(sitems)
        + "\n</sitemapindex>\n"
    )
    out_path.write_text(xml, encoding="utf-8")


def _collect_nested_index(dirpath: Path) -> list[Path]:
    if not dirpath.exists():
        return []
    return sorted(p for p in dirpath.glob("*/index.html") if p.is_file())


def _make_items(files: list[Path]) -> list[UrlItem]:
    return [UrlItem(loc=_loc_for(p), lastmod=_lastmod_iso(p)) for p in files]


def _make_blog_items(files: list[Path]) -> list[UrlItem]:
    return [UrlItem(loc=_loc_for(p), lastmod=_blog_sitemap_lastmod(p)) for p in files]


def main() -> None:
    # Páginas principais: home + índices por secção
    root_pages: list[Path] = []
    home = ROOT / "index.html"
    if home.is_file():
        root_pages.append(home)
    for sub in ("servicos", "contato", "blog", "quem-somos", "regioes", "politica-de-privacidade"):
        p = ROOT / sub / "index.html"
        if p.is_file():
            root_pages.append(p)
    for p in ROOT.glob("*.html"):
        if not p.is_file() or p.name.lower() in {"404.html"}:
            continue
        if p not in root_pages:
            root_pages.append(p)

    # Seções
    servico_pages = _collect_nested_index(ROOT / "servico")
    regioes_hubs = _collect_nested_index(ROOT / "regioes")
    reg_index = ROOT / "regioes" / "index.html"
    if reg_index.is_file() and reg_index not in regioes_hubs:
        regioes_hubs = sorted([reg_index, *regioes_hubs])
    blog_pages = sorted(
        p for p in (ROOT / "blog").glob("*/index.html") if p.is_file()
    )

    for p in blog_pages:
        _sync_blog_post_meta_in_html(p)

    # Arquivos de saída
    out_pages = ROOT / "sitemap_pages.xml"
    out_servicos = ROOT / "sitemap_servicos.xml"
    out_regioes = ROOT / "sitemap_regioes.xml"
    out_local = ROOT / "sitemap_local.xml"
    out_blog = ROOT / "sitemap_posts.xml"

    _write_urlset(out_pages, _make_items(root_pages))
    _write_urlset(out_servicos, _make_items(servico_pages))
    _write_urlset(out_regioes, _make_items(regioes_hubs))
    # Sitemap local = somente arquivo KML do negócio.
    local_pages: list[Path] = []
    local_kml = ROOT / "localizacao.kml"
    if local_kml.is_file():
        local_pages.append(local_kml)
    _write_urlset(out_local, _make_items(local_pages))
    _write_urlset(out_blog, _make_blog_items(blog_pages))

    index = ROOT / "sitemap_index.xml"
    _write_sitemapindex(index, [out_pages, out_servicos, out_regioes, out_local, out_blog])

    print("OK: sitemaps gerados")
    print("-", index.name)
    for p in [out_pages, out_servicos, out_regioes, out_local, out_blog]:
        print("-", p.name)


if __name__ == "__main__":
    main()


from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent
BASE_URL = "https://arcondicionadofloripa.com"


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


def _collect_html_files(dirpath: Path) -> list[Path]:
    if not dirpath.exists():
        return []
    return sorted([p for p in dirpath.glob("*.html") if p.is_file()])


def _make_items(files: list[Path]) -> list[UrlItem]:
    return [UrlItem(loc=_loc_for(p), lastmod=_lastmod_iso(p)) for p in files]


def main() -> None:
    # Páginas principais na raiz (exclui 404 se existir, e arquivos técnicos)
    root_pages = []
    for p in ROOT.glob("*.html"):
        if not p.is_file():
            continue
        if p.name.lower() in {"404.html"}:
            continue
        root_pages.append(p)

    # Seções
    servico_pages = _collect_html_files(ROOT / "servico")
    bairro_hubs = _collect_html_files(ROOT / "bairro")
    blog_pages = _collect_html_files(ROOT / "blog")

    # Arquivos de saída
    out_pages = ROOT / "sitemap_pages.xml"
    out_servicos = ROOT / "sitemap_servicos.xml"
    out_bairros = ROOT / "sitemap_bairros.xml"
    out_blog = ROOT / "sitemap_blog.xml"

    _write_urlset(out_pages, _make_items(root_pages))
    _write_urlset(out_servicos, _make_items(servico_pages))
    _write_urlset(out_bairros, _make_items(bairro_hubs))
    _write_urlset(out_blog, _make_items(blog_pages))

    index = ROOT / "sitemap_index.xml"
    _write_sitemapindex(index, [out_pages, out_servicos, out_bairros, out_blog])

    print("OK: sitemaps gerados")
    print("-", index.name)
    for p in [out_pages, out_servicos, out_bairros, out_blog]:
        print("-", p.name)


if __name__ == "__main__":
    main()


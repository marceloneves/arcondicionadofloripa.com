from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SERVICO_DIR = ROOT / "servico"


NAV_RE = re.compile(r'(<nav class="main-nav" id="mainNav">)(.*?)(</nav>)', re.DOTALL)


def patch_html(html: str) -> str:
    m = NAV_RE.search(html)
    if not m:
        return html

    nav_open, nav_inner, nav_close = m.group(1), m.group(2), m.group(3)

    # já tem blog?
    if re.search(r'href="(?:\.\./)*blog/"', nav_inner) or "../blog.html" in nav_inner:
        return html

    # insere antes do contato (mesmo prefixo relativo que contato: ../../ ou ../)
    contato_re = re.compile(
        r'(\s*)(<a href="((?:\.\./)*)contato/"[^>]*>Contato</a>\s*)',
    )
    if not contato_re.search(nav_inner):
        return html

    nav_inner2 = contato_re.sub(
        lambda m: f'{m.group(1)}<a href="{m.group(3)}blog/" class="">Blog</a>\n{m.group(1)}{m.group(2)}',
        nav_inner,
        count=1,
    )

    new_nav = f"{nav_open}{nav_inner2}{nav_close}"
    return html[: m.start()] + new_nav + html[m.end() :]


def main() -> None:
    if not SERVICO_DIR.exists():
        raise SystemExit("Diretório servico/ não existe")

    changed = 0
    total = 0
    for path in sorted(SERVICO_DIR.glob("*/index.html")):
        total += 1
        old = path.read_text(encoding="utf-8")
        new = patch_html(old)
        if new != old:
            path.write_text(new, encoding="utf-8")
            changed += 1

    print(f"OK: {changed}/{total} páginas de servico atualizadas com link Blog")


if __name__ == "__main__":
    main()


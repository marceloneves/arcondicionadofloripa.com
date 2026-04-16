from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BAIRRO_DIR = ROOT / "regioes"


@dataclass(frozen=True)
class BairroItem:
    name: str
    filename: str  # ex: "centro-florianopolis.html"

    @property
    def href(self) -> str:
        return f"/regioes/{self.filename}"


def _norm_sort_key(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s.casefold()


def load_bairros() -> list[BairroItem]:
    if not BAIRRO_DIR.exists():
        raise SystemExit(f"Diretório não encontrado: {BAIRRO_DIR}")

    items: list[BairroItem] = []
    for path in sorted(BAIRRO_DIR.glob("*.html")):
        html = path.read_text(encoding="utf-8")
        m = re.search(r"<h1>\s*Ar-Condicionado em (.*?),\s*(Florianópolis|SC)\s*</h1>", html)
        if not m:
            raise SystemExit(f"Não consegui extrair o nome da região em: {path}")
        name = m.group(1).strip()
        items.append(BairroItem(name=name, filename=path.name))

    items.sort(key=lambda x: _norm_sort_key(x.name))
    return items


def build_bairros_ul(items: list[BairroItem]) -> str:
    # Mantém HTML compacto como o restante do projeto
    lis = "".join(f'<li><a href="{i.href}">{i.name}</a></li>' for i in items)
    return f"<ul>{lis}</ul>"


def patch_file_footer(html: str, bairros_ul: str) -> tuple[str, int]:
    # Substitui APENAS o bloco do footer da coluna de regiões (título legado "Bairros" ou "Regiões").
    pattern = re.compile(r"(<div><h4>(?:Bairros|Regiões)</h4>)\s*<ul>[\s\S]*?</ul>(</div>)")

    def repl(m: re.Match[str]) -> str:
        return f"{m.group(1)}{bairros_ul}{m.group(2)}"

    new_html, n = pattern.subn(repl, html)
    return new_html, n


def iter_target_html_files() -> list[Path]:
    # Patches em todas as páginas HTML do site.
    # (Os hubs de bairro têm um footer diferente, sem coluna "Bairros"; serão ignorados naturalmente.)
    files = [p for p in ROOT.rglob("*.html") if ".git" not in p.parts]
    return sorted(files)


def main() -> None:
    bairros = load_bairros()
    bairros_ul = build_bairros_ul(bairros)

    total_files = 0
    changed_files = 0
    total_replacements = 0

    for path in iter_target_html_files():
        html = path.read_text(encoding="utf-8")
        new_html, n = patch_file_footer(html, bairros_ul)
        total_files += 1
        total_replacements += n
        if n and new_html != html:
            path.write_text(new_html, encoding="utf-8")
            changed_files += 1

    print(
        f"OK: {len(bairros)} bairros | arquivos analisados: {total_files} | "
        f"arquivos alterados: {changed_files} | substituições: {total_replacements}"
    )


if __name__ == "__main__":
    main()


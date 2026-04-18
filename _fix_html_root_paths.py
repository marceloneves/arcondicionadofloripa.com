#!/usr/bin/env python3
"""
Reescreve href/src que começam com '/' para caminhos relativos à raiz do site,
consoante a profundidade do ficheiro (ex.: blog/foo/index.html -> ../../css/...).

Assim o CSS/JS/imagens e links internos funcionam com `python -m http.server`
e ao abrir páginas em pastas sem depender da raiz do sistema de ficheiros.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent

# href / src / poster com caminho absoluto no host (começa com uma /)
ATTR_RE = re.compile(
    r"(?P<attr>\b(?:href|src|poster))\s*=\s*"
    r'(?P<q>["\'])(?P<val>/[^"\']*?)(?P=q)',
    re.IGNORECASE,
)


def root_prefix_for_relpath(relpath: str | Path) -> str:
    """Dado um caminho relativo à raiz do site (ex.: servicos/index.html), devolve '../' * profundidade."""
    p = Path(relpath)
    return "../" * len(p.parent.parts)


def _prefix_for(path: Path) -> str:
    rel = path.relative_to(ROOT)
    return root_prefix_for_relpath(rel)


def _repl_val(prefix: str, m: re.Match[str]) -> str:
    val = m.group("val")
    if val.startswith("//"):
        return m.group(0)
    inner = val[1:]  # sem '/' inicial
    if not inner:
        inner = "./" if not prefix else prefix.rstrip("/") + "/"
    else:
        inner = f"{prefix}{inner}"
    return f'{m.group("attr")}={m.group("q")}{inner}{m.group("q")}'


def transform_html(html: str, prefix: str) -> str:
    return ATTR_RE.sub(lambda m: _repl_val(prefix, m), html)


def iter_html_files() -> list[Path]:
    out: list[Path] = []
    for p in ROOT.rglob("*.html"):
        if ".git" in p.parts:
            continue
        out.append(p)
    return sorted(out)


def apply_relative_paths_to_file(path: Path, root: Path | None = None) -> bool:
    """Lê um HTML, aplica prefixos relativos e grava se alterado. Devolve True se gravou."""
    base = root or ROOT
    path = path.resolve()
    base = base.resolve()
    prefix = root_prefix_for_relpath(path.relative_to(base))
    text = path.read_text(encoding="utf-8")
    new = transform_html(text, prefix)
    if new != text:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def main() -> int:
    changed = 0
    for path in iter_html_files():
        if apply_relative_paths_to_file(path):
            changed += 1
    print(f"OK: {changed} ficheiros HTML atualizados (prefixo relativo à profundidade).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

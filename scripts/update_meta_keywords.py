#!/usr/bin/env python3
"""
Regenera <meta name="keywords"> em todo index.html a partir do <title> da página.

Uso (a partir de qualquer pasta):
  python3 scripts/update_meta_keywords.py
  python3 scripts/update_meta_keywords.py --dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
from html import escape
from pathlib import Path

DROP_ALONE = frozenset(
    {
        "blog",
        "sc",
        "de",
        "da",
        "do",
        "dos",
        "das",
        "em",
        "no",
        "na",
        "nos",
        "nas",
        "e",
        "ou",
        "para",
        "com",
        "por",
        "o",
        "a",
        "os",
        "as",
        "um",
        "uma",
        "uns",
        "se",
        "que",
        "como",
        "qual",
        "quais",
        "ao",
        "aos",
        "à",
        "às",
    }
)

META_RE = re.compile(r'  <meta name="keywords" content="[^"]*">\r?\n', re.MULTILINE)


def normalize_ac(s: str) -> str:
    s = re.sub(r"\b[Aa]r-[Cc]ondicionado\b", "Ar Condicionado", s)
    return re.sub(r"\s+", " ", s).strip()


def split_recursive(s: str) -> list[str]:
    s = normalize_ac(s)
    s = s.strip().rstrip("?").strip()
    if not s:
        return []

    m = re.match(r"^(Ar Condicionado)\s+([A-ZÁÂÃÉÍÓÚÇ][a-záâãéíóúç]+)$", s)
    if m and " " not in m.group(2):
        return [m.group(1), m.group(2)]

    if re.search(r"\s+em\s+", s, re.I):
        out: list[str] = []
        for p in re.split(r"\s+em\s+", s, flags=re.I):
            out.extend(split_recursive(p))
        return out

    if re.search(r"\s+ou\s+", s, re.I):
        out = []
        for p in re.split(r"\s+ou\s+", s, flags=re.I):
            out.extend(split_recursive(p))
        return out

    if re.search(r"\s+e\s+", s, re.I):
        out = []
        for p in re.split(r"\s+e\s+", s, flags=re.I):
            out.extend(split_recursive(p))
        return out

    m = re.match(r"^(.+?)\s+de\s+(.+)$", s, re.I)
    if m:
        left, right = m.group(1).strip(), m.group(2).strip()
        if 1 <= len(left.split()) <= 3 and right:
            return split_recursive(left) + split_recursive(right)

    return [s]


def title_to_keywords(title: str) -> str:
    t = normalize_ac(title)
    t = re.sub(r"\s*[|—–]\s*", ", ", t)
    t = re.sub(r"\?\s+(?=\S)", ", ", t)
    while ":" in t:
        nt = re.sub(r"\s*:\s*", ", ", t, count=1)
        if nt == t:
            break
        t = nt

    chunks = [c.strip() for c in re.split(r"\s*,\s*", t) if c.strip()]

    terms: list[str] = []
    seen: set[str] = set()

    for ch in chunks:
        if ch.lower() in ("blog", "sc"):
            continue
        for term in split_recursive(ch):
            term = normalize_ac(term).strip().rstrip("?").strip()
            if not term:
                continue
            low = term.lower()
            if low in DROP_ALONE:
                continue
            if low not in seen:
                seen.add(low)
                terms.append(term)

    return ", ".join(terms)


def main() -> int:
    parser = argparse.ArgumentParser(description="Atualiza meta keywords a partir dos títulos.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostra arquivos que mudariam, sem gravar.",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    changed = 0
    missing_meta = 0
    missing_title = 0

    for path in sorted(root.rglob("index.html")):
        text = path.read_text(encoding="utf-8")
        m = re.search(r"<title>([^<]*)</title>", text, re.I)
        if not m:
            missing_title += 1
            print(f"Sem <title>: {path.relative_to(root)}", file=sys.stderr)
            continue

        kw = title_to_keywords(m.group(1))
        new_line = f'  <meta name="keywords" content="{escape(kw, quote=True)}">\n'
        new_text, n = META_RE.subn(new_line, text, count=1)
        if n == 0:
            missing_meta += 1
            print(f"Sem meta keywords: {path.relative_to(root)}", file=sys.stderr)
            continue

        if new_text == text:
            continue

        changed += 1
        rel = path.relative_to(root)
        if args.dry_run:
            print(f"[dry-run] {rel}")
        else:
            path.write_text(new_text, encoding="utf-8")

    if args.dry_run:
        print(f"Arquivos que mudariam: {changed}")
    else:
        print(f"Arquivos alterados: {changed}")
    if missing_title or missing_meta:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

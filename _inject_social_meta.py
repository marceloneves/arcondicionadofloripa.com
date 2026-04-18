#!/usr/bin/env python3
"""Injeta/atualiza bloco OG + Twitter em todas as páginas HTML (páginas estáticas e geradas)."""
from __future__ import annotations

from pathlib import Path

from _social_meta import sync_all_html

ROOT = Path(__file__).resolve().parent

if __name__ == "__main__":
    n = sync_all_html(ROOT)
    print("HTML atualizados com meta social:", n)

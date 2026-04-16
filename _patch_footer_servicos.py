# -*- coding: utf-8 -*-
"""Atualiza o bloco de serviços no rodapé para incluir todos os 8 serviços."""

from pathlib import Path
import re

ROOT = Path(__file__).parent


def build_services_block(prefix: str) -> str:
    base = f"{prefix}servicos.html"
    return (
        f'<div><h4>Serviços</h4><ul>'
        f'<li><a href="{base}#instalacao-de-ar-condicionado">Instalação de Ar-Condicionado</a></li>'
        f'<li><a href="{base}#manutencao-de-ar-condicionado">Manutenção de Ar-Condicionado</a></li>'
        f'<li><a href="{base}#limpeza-de-ar-condicionado">Limpeza de Ar-Condicionado</a></li>'
        f'<li><a href="{base}#higienizacao-de-ar-condicionado">Higienização de Ar-Condicionado</a></li>'
        f'<li><a href="{base}#carga-de-gas-de-ar-condicionado">Carga de Gás de Ar-Condicionado</a></li>'
        f'<li><a href="{base}#remocao-e-reinstalacao-de-ar-condicionado">Remoção e Reinstalação de Ar-Condicionado</a></li>'
        f'<li><a href="{base}#conserto-de-ar-condicionado">Conserto de Ar-Condicionado</a></li>'
        f'<li><a href="{base}#pmoc-de-ar-condicionado">PMOC de Ar-Condicionado</a></li>'
        f'</ul></div>'
    )


PAT = re.compile(
    r'<div><h4>Serviços</h4><ul>.*?</ul></div>',
    re.DOTALL,
)


def patch_file(path: Path) -> bool:
    html = path.read_text(encoding="utf-8")
    if '<h4>Serviços</h4>' not in html:
        return False
    # Define prefix for servicos.html based on directory depth
    if path.parent == ROOT:
        prefix = ""
    else:
        prefix = "../"
    new_block = build_services_block(prefix)
    new_html, n = PAT.subn(new_block, html, count=1)
    if n:
        path.write_text(new_html, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = 0
    for p in ROOT.rglob("*.html"):
        if p.name.startswith("_"):
            continue
        if patch_file(p):
            changed += 1
    print("Rodapés atualizados em", changed, "arquivos.")


if __name__ == "__main__":
    main()


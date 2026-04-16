from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PATH = ROOT / "regioes.html"


def main() -> None:
    html = PATH.read_text(encoding="utf-8")

    # 1) Ajusta o texto do banner para não mencionar hub
    html = html.replace(
        "Escolha seu bairro: use o hub para ver todos os serviços na região ou acesse diretamente a página do serviço desejado.",
        "Escolha seu bairro e acesse diretamente a página do serviço desejado.",
    )

    # 2) Remove o botão do hub (um por card)
    html = re.sub(
        r'<p class="bairro-hub-cta">.*?</p>',
        "",
        html,
        flags=re.DOTALL,
    )

    # 3) Troca lista por grid de links em caixinhas
    html = html.replace("<ul>", '<div class="bairro-links">')
    html = html.replace("</ul>", "</div>")

    html = re.sub(
        r'<li><a href="([^"]+)">([^<]+)</a></li>',
        r'<a class="bairro-link" href="\1">\2</a>',
        html,
    )

    # 4) Remove tags <li> restantes (segurança)
    html = html.replace("<li>", "").replace("</li>", "")

    PATH.write_text(html, encoding="utf-8")
    print("OK: regioes.html atualizado")


if __name__ == "__main__":
    main()


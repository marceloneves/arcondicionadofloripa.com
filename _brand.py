# -*- coding: utf-8 -*-
"""Marca e URLs de ativos públicos (logo, etc.)."""
from __future__ import annotations

BASE_URL = "https://arcondicionadofloripa.com"
LOGO_FILENAME = "ar-condicionado-floripa-logo.webp"
LOGO_PATH = f"/images/{LOGO_FILENAME}"
LOGO_URL = f"{BASE_URL}{LOGO_PATH}"
FAVICON_FILENAME = "ar-condicionado-floripa-fav-icon.webp"
FAVICON_PATH = f"/images/{FAVICON_FILENAME}"
FAVICON_URL = f"{BASE_URL}{FAVICON_PATH}"
# Acessibilidade: descreve o símbolo (não só o nome da marca).
LOGO_ALT = (
    "Logotipo da Ar Condicionado Floripa: monograma preto com as letras AF entrelaçadas "
    "dentro de um círculo em traço fino, fundo branco"
)
# Autor nos posts do blog (marcelo-ar-condicionado.webp).
AUTHOR_PHOTO_ALT = (
    "Marcelo Menezes, técnico em refrigeração, de moletom cinza com listras amarelas nos ombros, "
    "sentado em cadeira de madeira, olhando para a câmera"
)

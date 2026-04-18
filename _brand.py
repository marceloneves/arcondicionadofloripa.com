# -*- coding: utf-8 -*-
"""Marca e URLs de ativos públicos (logo, etc.)."""
from __future__ import annotations

BASE_URL = "https://arcondicionadofloripa.com"
LOGO_FILENAME = "ar-condicionado-floripa-logo.webp"
LOGO_PATH = f"/images/{LOGO_FILENAME}"
LOGO_URL = f"{BASE_URL}{LOGO_PATH}"
# Acessibilidade: descreve o símbolo (não só o nome da marca).
LOGO_ALT = (
    "Logotipo da Ar Condicionado Floripa: monograma preto com as letras AF entrelaçadas "
    "dentro de um círculo em traço fino, fundo branco"
)
# Mesma imagem em todos os cards da listagem de serviços: descreve o conteúdo visual.
SERVICO_CARD_IMG_ALT = (
    "Ilustração de unidade interna de ar-condicionado split branca com painel digital "
    "mostrando 22°C e fluxo de ar representado; parede clara e tubulação ao lado"
)
# Foto do autor nos posts do blog (marcelo-ar-condicionado.webp).
AUTHOR_PHOTO_ALT = (
    "Retrato de Marcelo Menezes, técnico em refrigeração, com moletom cinza com listras "
    "amarelas nos ombros, sentado em cadeira de madeira, olhando para a câmera"
)

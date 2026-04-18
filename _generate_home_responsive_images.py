# -*- coding: utf-8 -*-
"""Gera variantes WebP 480w/960w para galeria e diferenciais da home + logo 256w."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
IMG = ROOT / "images"
QUALITY = 82


def _resize_save(src: Path, max_w: int, out: Path) -> None:
    im = Image.open(src)
    im = im.convert("RGBA") if im.mode in ("RGBA", "P") else im.convert("RGB")
    w, h = im.size
    if w > max_w:
        nh = max(1, int(h * (max_w / w)))
        im = im.resize((max_w, nh), Image.Resampling.LANCZOS)
    if im.mode == "RGBA":
        im.save(out, "WEBP", quality=QUALITY, method=6)
    else:
        im.save(out, "WEBP", quality=QUALITY, method=6)


def main() -> None:
    for pattern in ("instalacao-ar-condicionado-*.webp", "ar-condicionado-diferencial-*.webp"):
        for src in sorted(IMG.glob(pattern)):
            if "-480w" in src.name or "-960w" in src.name:
                continue
            stem = src.stem
            for max_w, tag in ((480, "480w"), (960, "960w")):
                _resize_save(src, max_w, IMG / f"{stem}-{tag}.webp")
    logo = IMG / "ar-condicionado-floripa-logo.webp"
    _resize_save(logo, 256, IMG / "ar-condicionado-floripa-logo-256w.webp")
    print("OK:", IMG)


if __name__ == "__main__":
    main()

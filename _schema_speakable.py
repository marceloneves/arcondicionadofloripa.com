"""SpeakableSpecification (schema.org) — seletores CSS alinhados ao DOM do site."""


def speakable(*css_selectors: str) -> dict:
    return {
        "@type": "SpeakableSpecification",
        "cssSelector": list(css_selectors),
    }

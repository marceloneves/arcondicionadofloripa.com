"""Extração heurística de entidades semânticas (schema.org) para artigos do blog e páginas de serviço."""
from __future__ import annotations

import html as html_module
import re
from collections import Counter


def parse_meta_keywords(html: str) -> list[str]:
    m = re.search(r'<meta name="keywords" content="([^"]*)"', html, re.I)
    if not m:
        return []
    return [k.strip() for k in m.group(1).split(",") if k.strip()]

# (regex, nome canônico, @type schema.org)
_ENTITY_RAW: list[tuple[str, str, str]] = [
    # Marcas e linhas (frases compostas primeiro)
    (r"springer\s+midea", "Springer Midea", "Brand"),
    (r"carrier\s+infinity", "Carrier Infinity", "Brand"),
    (r"daikin\s+sky\s+air", "Daikin Sky Air", "Brand"),
    (r"lg\s+dual\s+inverter", "LG Dual Inverter", "Brand"),
    (r"samsung\s+wind\s+free", "Samsung WindFree", "Brand"),
    (r"electrolux\s+color\s+adapt", "Electrolux Color Adapt", "Brand"),
    # Gases e normas
    (r"r[-\s]?410a", "R-410A", "Thing"),
    (r"r[-\s]?32\b", "R-32", "Thing"),
    (r"r[-\s]?22\b", "R-22", "Thing"),
    (r"r[-\s]?134a", "R-134a", "Thing"),
    (r"r[-\s]?290\b", "R-290", "Thing"),
    (r"r[-\s]?600a", "R-600a", "Thing"),
    (r"\bnbr\s*5410\b", "NBR 5410", "Thing"),
    (r"\bnbr\s*16690\b", "NBR 16690", "Thing"),
    (r"\bprocel\b", "Procel", "Thing"),
    (r"\binmetro\b", "Inmetro", "Thing"),
    # Equipamentos e conceitos longos
    (r"ar[-\s]condicionado\s+inverter", "Ar-condicionado inverter", "Thing"),
    (r"ar[-\s]condicionado\s+convencional", "Ar-condicionado convencional", "Thing"),
    (r"ar[-\s]condicionado\s+de\s+janela", "Ar-condicionado de janela", "Thing"),
    (r"ar[-\s]condicionado\s+split", "Ar-condicionado split", "Thing"),
    (r"split\s+inverter", "Split inverter", "Thing"),
    (r"multi\s+split", "Multi split", "Thing"),
    (r"unidade\s+externa", "Unidade externa", "Thing"),
    (r"unidade\s+interna", "Unidade interna", "Thing"),
    (r"placa\s+eletr[oô]nica", "Placa eletrônica", "Thing"),
    (r"placa\s+inverter", "Placa inverter", "Thing"),
    (r"controle\s+remoto", "Controle remoto", "Thing"),
    (r"controle\s+universal", "Controle universal", "Thing"),
    (r"c[oó]digo\s+do\s+controle", "Código do controle", "Thing"),
    (r"sensor\s+de\s+temperatura", "Sensor de temperatura", "Thing"),
    (r"sensor\s+de\s+ambiente", "Sensor de ambiente", "Thing"),
    (r"g[aá]s\s+refrigerante", "Gás refrigerante", "Thing"),
    (r"recarga\s+de\s+g[aá]s", "Recarga de gás", "Thing"),
    (r"carga\s+de\s+g[aá]s", "Carga de gás", "Thing"),
    (r"linha\s+de\s+suc[cç][aã]o", "Linha de sucção", "Thing"),
    (r"linha\s+de\s+l[ií]quido", "Linha de líquido", "Thing"),
    (r"manuten[cç][aã]o\s+preventiva", "Manutenção preventiva", "Thing"),
    (r"manuten[cç][aã]o\s+corretiva", "Manutenção corretiva", "Thing"),
    (r"instala[cç][aã]o\s+de\s+ar[-\s]condicionado", "Instalação de ar-condicionado", "Thing"),
    (r"higieniza[cç][aã]o\s+de\s+ar[-\s]condicionado", "Higienização de ar-condicionado", "Thing"),
    (r"limpeza\s+de\s+ar[-\s]condicionado", "Limpeza de ar-condicionado", "Thing"),
    (r"motor\s+do\s+ventilador", "Motor do ventilador", "Thing"),
    (r"ventilador\s+condensadora", "Ventilador da condensadora", "Thing"),
    (r"ventilador\s+evaporadora", "Ventilador da evaporadora", "Thing"),
    (r"bandeja\s+de\s+dreno", "Bandeja de dreno", "Thing"),
    (r"filtro\s+de\s+ar", "Filtro de ar", "Thing"),
    (r"circuito\s+exclusivo", "Circuito exclusivo", "Thing"),
    (r"tomada\s+dedicada", "Tomada dedicada", "Thing"),
    (r"disjuntor\s+curva\s+c", "Disjuntor curva C", "Thing"),
    (r"disjuntor\s+curva\s+b", "Disjuntor curva B", "Thing"),
    (r"dimensionamento\s+de\s+btu", "Dimensionamento de BTUs", "Thing"),
    (r"dimensionamento\s+de\s+btus", "Dimensionamento de BTUs", "Thing"),
    (r"grande\s+florian[oó]polis", "Grande Florianópolis", "Place"),
    (r"santa\s+catarina", "Santa Catarina", "Place"),
    # Cidades
    (r"florian[oó]polis", "Florianópolis", "Place"),
    (r"\bfloripa\b", "Florianópolis", "Place"),
    (r"s[aã]o\s+jos[eé]", "São José", "Place"),
    (r"palho[cç]a", "Palhoça", "Place"),
    (r"bigua[cç]u", "Biguaçu", "Place"),
    # Peças e elétrica
    (r"compressor", "Compressor", "Thing"),
    (r"evaporadora", "Evaporadora", "Thing"),
    (r"condensadora", "Condensadora", "Thing"),
    (r"capacitor", "Capacitor", "Thing"),
    (r"pressostato", "Pressostato", "Thing"),
    (r"\brel[eé]\b", "Relé", "Thing"),
    (r"inversor\s+de\s+frequ[eê]ncia", "Inversor de frequência", "Thing"),
    (r"rolamento", "Rolamento", "Thing"),
    (r"serpentina", "Serpentina", "Thing"),
    (r"refrigera[cç][aã]o", "Refrigeração", "Thing"),
    (r"climatiza[cç][aã]o", "Climatização", "Thing"),
    (r"pmoc\b", "PMOC", "Thing"),
    (r"inverter\b", "Inverter", "Thing"),
    (r"convencional", "Convencional", "Thing"),
    (r"on[/\s]off", "On/Off", "Thing"),
    (r"disjuntor", "Disjuntor", "Thing"),
    (r"bitola", "Bitola", "Thing"),
    (r"monof[aá]sico", "Monofásico", "Thing"),
    (r"bif[aá]sico", "Bifásico", "Thing"),
    (r"trif[aá]sico", "Trifásico", "Thing"),
    # Marcas curtas (por último na ordem por comprimento)
    (r"\bsamsung\b", "Samsung", "Brand"),
    (r"\blg\b", "LG", "Brand"),
    (r"\bmidea\b", "Midea", "Brand"),
    (r"\bgree\b", "Gree", "Brand"),
    (r"\belectrolux\b", "Electrolux", "Brand"),
    (r"\bconsul\b", "Consul", "Brand"),
    (r"\bbrastemp\b", "Brastemp", "Brand"),
    (r"\bspringer\b", "Springer", "Brand"),
    (r"\bcarrier\b", "Carrier", "Brand"),
    (r"\bdaikin\b", "Daikin", "Brand"),
    (r"\bfujitsu\b", "Fujitsu", "Brand"),
    (r"\bhitachi\b", "Hitachi", "Brand"),
    (r"\bphilco\b", "Philco", "Brand"),
    (r"\bbrit[aâ]nia\b", "Britânia", "Brand"),
    (r"\belgin\b", "Elgin", "Brand"),
    (r"\bariston\b", "Ariston", "Brand"),
    (r"\bbosch\b", "Bosch", "Brand"),
    (r"\bkomeco\b", "Komeco", "Brand"),
    (r"\baginet\b", "Aginet", "Brand"),
    (r"\besmaltec\b", "Esmaltec", "Brand"),
    (r"\bcomfee\b", "Comfee", "Brand"),
    (r"\btcl\b", "TCL", "Brand"),
    (r"\bhisense\b", "Hisense", "Brand"),
]

_ENTITY_PATTERNS: list[tuple[re.Pattern[str], str, str]] = sorted(
    (
        (re.compile(pat, re.IGNORECASE), name, stype)
        for pat, name, stype in _ENTITY_RAW
    ),
    key=lambda x: len(x[0].pattern),
    reverse=True,
)


def is_faq_h2(title: str) -> bool:
    t = title.strip()
    sl = t.lower()
    if sl == "faq":
        return True
    if sl.startswith("faq"):
        return True
    if "perguntas frequentes" in sl:
        return True
    if "tudo sobre o preço da manutenção do seu ar" in sl:
        return True
    return False


def html_to_plain(fragment: str) -> str:
    t = re.sub(r"<[^>]+>", " ", fragment)
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"\s+([.,;:!?])", r"\1", t)
    return html_module.unescape(t)


def _strip_noise_html(html_chunk: str) -> str:
    return re.sub(r"<script[\s\S]*?</script>", " ", html_chunk, flags=re.I)


def extract_main_html(document: str) -> str:
    mm = re.search(r"<main>([\s\S]*?)</main>", document, re.I)
    return mm.group(1) if mm else document


def extract_article_body_html(main_inner: str) -> str:
    """Conteúdo do <main> até o primeiro bloco FAQ (exclui FAQ do foco de `about`)."""
    for m in re.finditer(r"<h2>([^<]+)</h2>", main_inner, re.I):
        if is_faq_h2(m.group(1)):
            return main_inner[: m.start()]
    return main_inner


def _norm_key(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"\s+", " ", s)
    return s


def _entity_node(name: str, stype: str) -> dict[str, str]:
    t = stype if stype in ("Thing", "Brand", "Place", "Product") else "Thing"
    return {"@type": t, "name": name}


def _scan_glossary(text: str) -> list[tuple[str, str, int]]:
    """Lista (nome canônico, tipo, posição primeira ocorrência)."""
    if not text:
        return []
    found: list[tuple[str, str, int]] = []
    seen_span: list[tuple[int, int]] = []

    def overlaps(a: int, b: int) -> bool:
        for x, y in seen_span:
            if a < y and b > x:
                return True
        return False

    for rx, name, stype in _ENTITY_PATTERNS:
        for m in rx.finditer(text):
            if overlaps(m.start(), m.end()):
                continue
            seen_span.append((m.start(), m.end()))
            found.append((name, stype, m.start()))
            break  # uma ocorrência por padrão evita explosão
    return found


def _btu_mentions(text: str) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    patterns = [
        r"\b\d{1,2}(?:\.\d{3})+\s*btus?\b",
        r"\b\d{4,5}\s*btus?\b",
        r"\b\d{1,2}\s*mil\s*btus?\b",
    ]
    for pat in patterns:
        for m in re.finditer(pat, text, re.I):
            label = m.group(0)
            label = re.sub(r"\s+", " ", label).strip()
            label = label[0].upper() + label[1:] if label else label
            label = re.sub(r"(?i)btus", "BTUs", label)
            nk = _norm_key(label)
            if nk not in seen:
                seen.add(nk)
                out.append(label)
    return out


def _voltage_mentions(text: str) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for m in re.finditer(r"\b(?:110|127|220|380)\s*v\b", text, re.I):
        label = m.group(0).upper().replace(" ", "")
        if label not in seen:
            seen.add(label)
            out.append(label)
    return out


def _ampere_mentions(text: str) -> list[str]:
    """Ex.: 16A, 20 A (só com A maiúsculo ou token claro)."""
    out: list[str] = []
    seen: set[str] = set()
    for m in re.finditer(r"\b(\d{1,2})\s*A\b", text):
        label = f"{m.group(1)}A"
        if label not in seen:
            seen.add(label)
            out.append(label)
    return out


def _headings_from_html(chunk: str) -> list[str]:
    """Só h2: h3 costuma ser subtítulo curto ou item de lista (mitos/FAQ interno), poluindo `about`."""
    titles: list[str] = []
    for m in re.finditer(r"<h2>([^<]+)</h2>", chunk, re.I):
        t = html_module.unescape(m.group(1)).strip()
        t = re.sub(r"^\d+\.\s*", "", t).strip()
        if 10 <= len(t) <= 100 and not is_faq_h2(t):
            titles.append(t)
    return titles


def infer_semantic_about_mentions(
    *,
    html: str,
    headline: str,
    description: str,
    keywords: list[str],
    faq_pairs: list[tuple[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """
    Retorna (about, mentions) como listas de nós schema.org (Thing / Brand / Place).
    `about`: tema principal (keywords + títulos de seção + entidades do corpo sem FAQ).
    `mentions`: tudo que aparece no texto útil (corpo + FAQ + meta).
    """
    main_raw = extract_main_html(html)
    main_clean = _strip_noise_html(main_raw)
    body_html = extract_article_body_html(main_clean)
    body_plain = html_to_plain(body_html)
    main_plain = html_to_plain(main_clean)
    faq_blob = " ".join(f"{q} {a}" for q, a in faq_pairs)

    corpus_mentions = " ".join(
        [
            headline,
            description,
            main_plain,
            faq_blob,
            ", ".join(keywords),
        ]
    )
    corpus_about = " ".join([headline, description, body_plain, ", ".join(keywords)])

    # --- mentions: glossário + regex técnicas
    mention_keys: dict[str, dict[str, str]] = {}
    order: list[str] = []

    def add_mention(name: str, stype: str = "Thing") -> None:
        nk = _norm_key(name)
        if nk in mention_keys or len(name) < 2:
            return
        mention_keys[nk] = _entity_node(name, stype)
        order.append(nk)

    for name, stype, _ in sorted(_scan_glossary(corpus_mentions), key=lambda x: x[2]):
        add_mention(name, stype)

    for lab in _btu_mentions(corpus_mentions):
        add_mention(lab, "Thing")
    for lab in _voltage_mentions(corpus_mentions):
        add_mention(lab, "Thing")
    for lab in _ampere_mentions(corpus_mentions):
        add_mention(lab, "Thing")

    mentions_list = [mention_keys[k] for k in order][:50]

    # --- about: keywords + headings + entidades mais frequentes no corpo
    about_keys: dict[str, dict[str, str]] = {}
    about_order: list[str] = []

    def add_about(name: str, stype: str = "Thing") -> None:
        nk = _norm_key(name)
        if nk in about_keys or len(name) < 3:
            return
        about_keys[nk] = _entity_node(name, stype)
        about_order.append(nk)

    for kw in keywords:
        add_about(kw.strip(), "Thing")

    for title in _headings_from_html(body_html)[:10]:
        add_about(title, "Thing")

    # Contagem de entidades do glossário no corpo (sem FAQ) para priorizar temas
    body_counts: Counter[str] = Counter()
    body_types: dict[str, str] = {}
    for rx, name, stype in _ENTITY_PATTERNS:
        n = len(rx.findall(body_plain))
        if n:
            body_counts[name] += n
            body_types[name] = stype

    for name, _cnt in body_counts.most_common(20):
        if _norm_key(name) not in about_keys:
            add_about(name, body_types.get(name, "Thing"))

    # Se ainda vazio, usa headline
    if not about_order:
        add_about(headline, "Thing")

    about_list = [about_keys[k] for k in about_order][:18]

    return about_list, mentions_list

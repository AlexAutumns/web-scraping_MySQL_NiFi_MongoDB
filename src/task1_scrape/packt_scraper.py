import json
import re
from typing import Any

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-GB,en;q=0.9",
}

PUBDATE_RE = re.compile(r"Publication date\s*:?\s*([A-Za-z]{3,9}\s+\d{1,2},\s+\d{4})", re.IGNORECASE)
PRICE_RE = re.compile(r"\$([0-9]+(?:\.[0-9]{2})?)")
YEAR_RE = re.compile(r"(19|20)\d{2}")

BAD_AUTHOR_PHRASES = [
    "free trial", "unsubscribe", "emails", "redeeming", "service",
    "privacy", "terms", "cookie", "newsletter", "consent"
]


def fetch_html(url: str, timeout: int = 30) -> str:
    r = requests.get(url, headers=HEADERS, timeout=timeout)
    print(f"[FETCH] {r.status_code} {url}")
    r.raise_for_status()
    return r.text


def extract_jsonld(soup: BeautifulSoup) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    for tag in soup.select('script[type="application/ld+json"]'):
        if not tag.string:
            continue
        try:
            data = json.loads(tag.string)
            if isinstance(data, list):
                blocks.extend([d for d in data if isinstance(d, dict)])
            elif isinstance(data, dict):
                blocks.append(data)
        except json.JSONDecodeError:
            continue
    return blocks


def pick_product_ld(jsonlds: list[dict[str, Any]]) -> dict[str, Any] | None:
    for d in jsonlds:
        t = d.get("@type")
        if t == "Product" or (isinstance(t, list) and "Product" in t):
            return d

    for d in jsonlds:
        graph = d.get("@graph")
        if isinstance(graph, list):
            for node in graph:
                t = node.get("@type")
                if t == "Product" or (isinstance(t, list) and "Product" in t):
                    return node
    return None


def extract_person_names_from_jsonld(jsonlds: list[dict[str, Any]]) -> list[str]:
    names: list[str] = []

    def walk(obj: Any):
        if isinstance(obj, dict):
            yield obj
            for v in obj.values():
                yield from walk(v)
        elif isinstance(obj, list):
            for item in obj:
                yield from walk(item)

    for block in jsonlds:
        for node in walk(block):
            t = node.get("@type")
            if t == "Person" or (isinstance(t, list) and "Person" in t):
                n = node.get("name")
                if isinstance(n, str) and n.strip():
                    names.append(n.strip())

    out: list[str] = []
    seen = set()
    for n in names:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


def is_probably_author_string(s: str) -> bool:
    if not s:
        return False

    s_clean = " ".join(s.split()).strip()
    if len(s_clean) > 80:
        return False

    low = s_clean.lower()
    if any(p in low for p in BAD_AUTHOR_PHRASES):
        return False

    if not re.search(r"[A-Za-z]", s_clean):
        return False

    if s_clean.count(".") >= 1 or s_clean.count(",") > 6:
        return False

    name_like = re.fullmatch(
        r"[A-Za-z][A-Za-z .'-]*(?:, [A-Za-z][A-Za-z .'-]*)*(?: and [A-Za-z][A-Za-z .'-]*)?",
        s_clean
    )
    if name_like:
        return True

    caps_words = re.findall(r"\b[A-Z][a-z]+(?:'[A-Za-z]+)?\b", s_clean)
    return len(caps_words) >= 2


def extract_authors_fallback(soup: BeautifulSoup) -> str | None:
    text_lines = soup.get_text("\n", strip=True).split("\n")

    for line in text_lines[:250]:
        line = " ".join(line.split()).strip()
        m = re.match(r"^By\s+(.+)$", line, flags=re.IGNORECASE)
        if m:
            cand = m.group(1).strip(" -|")
            if is_probably_author_string(cand):
                return cand

    selectors = [
        '[data-testid*="author"]',
        ".authors", ".author", ".product-authors", ".book-authors", ".contributors"
    ]
    for sel in selectors:
        try:
            for el in soup.select(sel):
                txt = el.get_text(" ", strip=True)
                txt = re.sub(r"^\s*By\s+", "", txt, flags=re.IGNORECASE).strip()
                if is_probably_author_string(txt):
                    return txt
        except Exception:
            pass

    return None


def extract_rating_fallback(soup: BeautifulSoup) -> float | None:
    text = soup.get_text(" ", strip=True)

    hotspots = ["rating", "ratings", "review", "reviews", "stars", "star"]
    for h in hotspots:
        idx = text.lower().find(h)
        if idx != -1:
            window = text[max(0, idx - 80): idx + 80]
            m = re.search(r"\b([0-5]\.[0-9])\b", window)
            if m:
                try:
                    val = float(m.group(1))
                    if 0.0 <= val <= 5.0:
                        return val
                except ValueError:
                    pass

    for m in re.finditer(r"\b([0-5]\.[0-9])\b", text):
        try:
            val = float(m.group(1))
            if 0.0 <= val <= 5.0:
                return val
        except ValueError:
            continue

    return None


def normalize_authors(authors: str | None) -> str | None:
    if not authors:
        return None

    s = " ".join(authors.split()).strip()

    if "," in s:
        parts = [p.strip() for p in s.split(",") if p.strip()]
        return ", ".join(parts) if parts else None

    s = re.sub(r"\s+\band\b\s+", ", ", s, flags=re.IGNORECASE)

    tokens = s.split()
    if len(tokens) <= 2:
        return s

    chunks: list[str] = []
    current: list[str] = [tokens[0]]

    def is_new_name_start(word: str) -> bool:
        connectors = {"de", "da", "del", "van", "von", "bin", "binti", "al", "el", "la", "le", "di", "du"}
        if word.lower() in connectors:
            return False
        if not word[:1].isupper():
            return False
        return len(current) >= 2

    for w in tokens[1:]:
        if is_new_name_start(w):
            chunks.append(" ".join(current))
            current = [w]
        else:
            current.append(w)

    if current:
        chunks.append(" ".join(current))

    if len(chunks) <= 1:
        return s

    return ", ".join(chunks)


def parse_packt_product(url: str) -> dict[str, Any]:
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n", strip=True)

    h1 = soup.select_one("h1")
    title = h1.get_text(strip=True) if h1 else None

    jsonlds = extract_jsonld(soup)
    product = pick_product_ld(jsonlds)

    authors = None
    year = None
    star_rating = None
    price = None

    if product:
        title = product.get("name") or title

        a = product.get("author")
        if isinstance(a, dict):
            authors = a.get("name")
        elif isinstance(a, list):
            names = []
            for item in a:
                if isinstance(item, dict) and item.get("name"):
                    names.append(item["name"])
                elif isinstance(item, str):
                    names.append(item)
            authors = ", ".join(names) if names else None
        elif isinstance(a, str):
            authors = a

        date_published = product.get("datePublished")
        if isinstance(date_published, str):
            ym = YEAR_RE.search(date_published)
            if ym:
                year = int(ym.group(0))

        agg = product.get("aggregateRating")
        if isinstance(agg, dict):
            rv = agg.get("ratingValue")
            try:
                star_rating = float(rv) if rv is not None else None
            except ValueError:
                star_rating = None

        offers = product.get("offers")
        if isinstance(offers, dict):
            pv = offers.get("price")
            try:
                price = float(pv) if pv is not None else None
            except ValueError:
                price = None
        elif isinstance(offers, list):
            for off in offers:
                if isinstance(off, dict) and off.get("price"):
                    try:
                        price = float(off["price"])
                        break
                    except ValueError:
                        pass

    if year is None:
        m = PUBDATE_RE.search(text)
        if m:
            ym = YEAR_RE.search(m.group(1))
            if ym:
                year = int(ym.group(0))
        else:
            ym = YEAR_RE.search(text)
            if ym:
                year = int(ym.group(0))

    if price is None:
        pm = PRICE_RE.search(text)
        if pm:
            price = float(pm.group(1))

    if authors is None:
        authors = extract_authors_fallback(soup)

    if authors is None:
        person_names = extract_person_names_from_jsonld(jsonlds)
        if person_names:
            authors = ", ".join(person_names[:5])

    if star_rating is None:
        star_rating = extract_rating_fallback(soup)

    authors = normalize_authors(authors)

    return {
        "title": title,
        "authors": authors,
        "year": year,
        "star_rating": star_rating,
        "price": price,
        "source_url": url,
    }

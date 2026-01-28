import re
from typing import Any, Optional

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.manning.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.manning.com/catalog",
}

# Patterns
YEAR_RE = re.compile(r"^(19|20)\d{2}$")                 # year is a standalone line like "2025"
PRICE_LINE_RE = re.compile(r"^([$£€])\s*([0-9]+(?:\.[0-9]{2})?)$")  # price on its own line like "$47.99"
RATINGCOUNT_RE = re.compile(r"^\((\d+)\)$")             # "(4)"

# Lines to ignore as "not titles"
NOISE = {
    "manning.com", "/", "catalog", "browse", "home", "cart", "log in",
    "sort:", "newest", "popularity",
    "Software Development", "Cloud", "Data Engineering",
    "Databases", "Database Platforms",
}
NOISE_LOWER = {s.lower() for s in NOISE}


def fetch_html(url: str, timeout: int = 30) -> str:
    r = requests.get(url, headers=HEADERS, timeout=timeout)
    print(f"[FETCH] {r.status_code} {url}")
    r.raise_for_status()
    return r.text


def _clean_lines(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    lines = [ln.strip() for ln in soup.get_text("\n", strip=True).split("\n")]
    return [ln for ln in lines if ln]


def _is_noise(line: str) -> bool:
    low = line.strip().lower()
    if low in NOISE_LOWER:
        return True
    # also ignore very short separators
    if line.strip() in {",", "|"}:
        return True
    return False


def _is_price_line(line: str) -> bool:
    return PRICE_LINE_RE.match(line.strip()) is not None


def _price_value(line: str) -> Optional[float]:
    m = PRICE_LINE_RE.match(line.strip())
    if not m:
        return None
    try:
        return float(m.group(2))
    except ValueError:
        return None


def _is_year_line(line: str) -> bool:
    return YEAR_RE.match(line.strip()) is not None


def _is_ratingcount_line(line: str) -> bool:
    return RATINGCOUNT_RE.match(line.strip()) is not None


def _looks_like_title(line: str) -> bool:
    """
    Heuristic for a title line:
    - not noise
    - not a year
    - not a price
    - not a rating count
    - reasonable length
    """
    s = line.strip()
    if not s or len(s) < 6:
        return False
    if _is_noise(s):
        return False
    if _is_year_line(s) or _is_price_line(s) or _is_ratingcount_line(s):
        return False
    # Many nav items are single words; titles usually have spaces
    if len(s.split()) == 1 and s.isalpha():
        return False
    return True


def parse_manning_catalog(html: str, catalog_url: str) -> list[dict[str, Any]]:
    """
    Parse Manning catalog pages where listing info is split across lines:
      Title
      Author Name(s)
      ,
      2025
      $47.99
      $23.99
      (4)
    """
    lines = _clean_lines(html)

    rows: list[dict[str, Any]] = []
    seen_titles = set()

    i = 0
    n = len(lines)

    while i < n:
        line = lines[i].strip()

        if not _looks_like_title(line):
            i += 1
            continue

        title = line

        # Look ahead for a year within the next few lines
        # We expect: author lines + optional comma line + year
        year_idx = None
        for j in range(i + 1, min(i + 8, n)):  # look ahead up to 7 lines
            if _is_year_line(lines[j]):
                year_idx = j
                break

        if year_idx is None:
            i += 1
            continue

        # Authors are the lines between title and year, excluding commas/noise
        author_parts = []
        for k in range(i + 1, year_idx):
            part = lines[k].strip()
            if part in {",", "|"}:
                continue
            if _is_noise(part) or _is_price_line(part) or _is_ratingcount_line(part) or _is_year_line(part):
                continue
            author_parts.append(part)

        authors = " ".join(author_parts).strip() if author_parts else None
        year = int(lines[year_idx].strip())

        # After year, gather next 1–4 price lines (often 1 or 2 lines: full + discounted)
        prices: list[float] = []
        p_scan_end = min(year_idx + 6, n)
        idx = year_idx + 1
        while idx < p_scan_end:
            p = _price_value(lines[idx])
            if p is not None:
                prices.append(p)
                idx += 1
                continue
            # stop price scan if we hit next title-ish thing
            if _looks_like_title(lines[idx]) and idx > year_idx + 1:
                break
            idx += 1

        if not prices:
            i += 1
            continue

        price = prices[-1]  # pick latest/discounted if multiple

        # Rating count can appear right after prices
        star_rating = None
        if idx < n and _is_ratingcount_line(lines[idx]):
            m = RATINGCOUNT_RE.match(lines[idx].strip())
            if m:
                star_rating = float(m.group(1))

        # Final validation
        if not authors:
            i += 1
            continue

        if title in seen_titles:
            i = max(i + 1, idx)
            continue
        seen_titles.add(title)

        rows.append({
            "title": title,
            "authors": authors,
            "year": year,
            "star_rating": star_rating,  # this is a count in Manning listings, but OK for CW1 field
            "price": price,
            "source_url": catalog_url,   # provenance; good enough for CW1
        })

        # Jump forward to continue scanning after this block
        i = max(i + 1, idx)

    return rows


def scrape_catalog(url: str) -> list[dict[str, Any]]:
    html = fetch_html(url)
    rows = parse_manning_catalog(html, catalog_url=url)
    print(f"[PARSE] {len(rows)} rows from catalog")

    # Helpful debug if still 0
    if not rows:
        lines = _clean_lines(html)
        print("[DEBUG] sample lines (first 60):")
        for ln in lines[:60]:
            print("  ", ln)

    return rows

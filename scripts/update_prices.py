#!/usr/bin/env python3
"""
Price update script for MOZA Competitor Price Monitor.
Uses BrowserAct stealth-extract to fetch live USD prices from official brand websites.

Features:
- Parallel stealth extraction across 8 brand websites via BrowserAct
- Anti-bot bypass with stealth browser engine
- Site-specific price parsers (Shopify, Logitech, Fanatec, Thrustmaster)
- Retry with exponential backoff on 429 rate limits
- Sale price detection (prefers current sale price over original)
- Intelligent product matching against existing data/prices.js
- Dry-run mode to preview changes before applying
- Scraper run log for audit trail

Usage:
    python scripts/update_prices.py                # Full update (all brands)
    python scripts/update_prices.py --dry-run      # Preview only
    python scripts/update_prices.py --brand MOZA   # Single brand
    python scripts/update_prices.py --sequential   # One at a time (avoids 429)
"""

import json
import os
import re
import subprocess
import sys
import time
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any

# ── Paths ──────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRICES_JS_PATH = os.path.join(PROJECT_ROOT, "data", "prices.js")
SCRAPER_LOG_PATH = os.path.join(PROJECT_ROOT, "data", "scraper_log.json")
STEALTH_TIMEOUT = 60     # seconds per stealth-extract call
RETRY_DELAY_BASE = 8     # base seconds for 429 backoff
MAX_RETRIES = 3          # max retry attempts per URL

# ── Brand scraping config ──────────────────────────────────────────────
# Each brand: list of URLs to scrape (can have multiple category pages)
# parser: strategy name
BRAND_CONFIGS: dict[str, dict] = {
    "MOZA": {
        "urls": [
            "https://us.mozaracing.com/collections/all",
        ],
        "parser": "shopify",
    },
    "Fanatec": {
        "urls": [
            "https://www.fanatec.com/us/en/c/sim-racing-bundles",
            "https://www.fanatec.com/us/en/c/wheel-bases",
            "https://www.fanatec.com/us/en/c/steering-wheels",
            "https://www.fanatec.com/us/en/c/pedals",
            "https://www.fanatec.com/us/en/c/add-ons",
        ],
        "parser": "fanatec",
    },
    "Simagic": {
        "urls": [
            "https://simagic-usa.myshopify.com/collections/all",
        ],
        "parser": "shopify",
    },
    "Logitech": {
        "urls": [
            "https://www.logitechg.com/en-us/products/driving.html",
        ],
        "parser": "logitech",
    },
    "Thrustmaster": {
        # NOTE: eshop.thrustmaster.com is blocked by reCAPTCHA.
        # Prices must be updated manually or via a different scraping approach.
        "urls": [],
        "parser": "generic",
    },
    "PXN": {
        "urls": [
            "https://us.e-pxn.com/collections/all",
        ],
        "parser": "shopify",
    },
    "Thermaltake": {
        "urls": [
            "https://thermaltakeusa.com/collections/racing-simulator",
        ],
        "parser": "shopify",
    },
    "Honeycomb": {
        "urls": [
            "https://flyhoneycomb.com/collections/all",
        ],
        "parser": "shopify",
    },
    "Asetek": {
        "urls": [
            "https://www.asetek.com/simsports/products/",
        ],
        "parser": "generic",
    },
    "VKB": {
        "urls": [
            "https://www.vkbcontrollers.com/collections/all",
        ],
        "parser": "shopify",
    },
    "Virpil": {
        "urls": [
            "https://virpil-controls.eu/shop",
        ],
        "parser": "generic",
    },
    "Winwing": {
        "urls": [
            "https://winwingsim.com/collections/all",
        ],
        "parser": "shopify",
    },
}

# Navigation/section keywords to skip during heading-based parsing
SKIP_HEADING_KEYWORDS = [
    "menu", "footer", "cart", "search", "account", "sign in", "create account",
    "policy", "shipping", "contact", "about", "blog", "collection", "featured",
    "new arrivals", "categories", "newsletter", "follow", "social", "currency",
    "language", "price", "filter", "sort by", "subscribe", "information",
    "customer", "support", "quick links", "shop by", "trending", "home",
    "company", "returns", "terms", "privacy", "cookies", "settings",
    "gaming mice", "keyboard", "headset", "webcam", "speaker", "accessories",
    "software", "discover", "build your", "shop", "region", "compare",
    "learn more", "buy now", "add to cart", "out of stock", "notify me",
    "free shipping", "easy returns", "buy now pay later", "all filters",
    "showing", "products", "gift with", "sale", "best seller",
    "features & availability", "driving style",
    "steering wheel & pedal", "cockpit bundles", "racing wheels",
    "shop now", "configurator", "forum", "skip to content",
    "play now pay later", "trueforce technology", "legal trademark",
    "subscribe to", "build your ultimate", "sim racing wheels,",
]


def _skip_heading(name: str) -> bool:
    """Check if a heading looks like navigation, not a product."""
    nl = name.strip().lower()
    if len(nl) < 4:
        return True
    return any(kw in nl for kw in SKIP_HEADING_KEYWORDS)


# ── Helpers ────────────────────────────────────────────────────────────

def read_prices_js() -> str:
    with open(PRICES_JS_PATH, "r", encoding="utf-8") as f:
        return f.read()


def write_prices_js(content: str) -> None:
    with open(PRICES_JS_PATH, "w", encoding="utf-8") as f:
        f.write(content)


def parse_js_products(content: str) -> list[dict]:
    """Parse RACING_PRODUCTS + FLIGHT_PRODUCTS arrays from prices.js."""
    products = []
    for array_name in ["RACING_PRODUCTS", "FLIGHT_PRODUCTS"]:
        m = re.search(rf"const {array_name} = \[(.*?)\];", content, re.DOTALL)
        if not m:
            continue
        for pm in re.finditer(
            r"\{\s*brand:\s*'([^']+)'\s*,\s*cat:\s*'([^']+)'\s*,\s*"
            r"name:\s*'([^']+)'\s*,\s*price:\s*([\d.]+)\s*,\s*"
            r"note:\s*'([^']*)'",
            m.group(1),
        ):
            products.append({
                "brand": pm.group(1),
                "cat": pm.group(2),
                "name": pm.group(3),
                "price": float(pm.group(4)),
                "note": pm.group(5),
            })
    return products


def call_stealth_extract(url: str, timeout: int = STEALTH_TIMEOUT) -> dict[str, Any]:
    """Call browser-act stealth-extract with retry on 429."""
    last_error = ""
    for attempt in range(1, MAX_RETRIES + 1):
        start = time.time()
        try:
            result = subprocess.run(
                [
                    "browser-act", "stealth-extract", url,
                    "--content-type", "markdown",
                    "--timeout", str(timeout * 1000),
                ],
                capture_output=True, text=True,
                timeout=timeout + 20,
            )
            elapsed = round(time.time() - start, 1)
            output = result.stdout
            err = result.stderr.strip()

            # Check for 429 in error output
            if "429" in err or "429" in output:
                if attempt < MAX_RETRIES:
                    delay = RETRY_DELAY_BASE * (2 ** (attempt - 1))
                    print(f"     ⏳ 429 rate-limited, retry {attempt}/{MAX_RETRIES} "
                          f"in {delay}s...")
                    time.sleep(delay)
                    continue
                return {"url": url, "success": False,
                        "error": "429 Too Many Requests (max retries)",
                        "elapsed": elapsed, "content": ""}

            # Check for other HTTP errors
            if "230404" in err or "404" in err:
                return {"url": url, "success": False,
                        "error": f"Page not found: {url}",
                        "elapsed": elapsed, "content": ""}

            if result.returncode != 0:
                return {"url": url, "success": False,
                        "error": err[:400], "elapsed": elapsed, "content": ""}

            # Clean output — skip warning lines at the top
            lines = output.split("\n")
            clean_start = 0
            for i, line in enumerate(lines):
                s = line.strip()
                if s and not any(s.startswith(p) for p in [
                    "C:", "warnings", "Error",
                ]) and "RequestsDependencyWarning" not in s:
                    clean_start = i
                    break
            content = "\n".join(lines[clean_start:])

            return {"url": url, "success": True, "content": content,
                    "elapsed": elapsed, "error": ""}

        except subprocess.TimeoutExpired:
            return {"url": url, "success": False,
                    "error": f"Timeout ({timeout + 20}s)",
                    "elapsed": timeout + 20, "content": ""}
        except Exception as e:
            last_error = str(e)[:400]
            if attempt < MAX_RETRIES:
                delay = RETRY_DELAY_BASE * (2 ** (attempt - 1))
                time.sleep(delay)
                continue

    return {"url": url, "success": False,
            "error": last_error, "elapsed": 0, "content": ""}


def _extract_price_from_lines(lines: list[str], start_idx: int,
                               max_lookahead: int = 12) -> float | None:
    """Look for a USD price in lines following start_idx.
    Returns the first (sale) price found, or None.

    Handles formats:
      $XX.XX USD
      Sale price$XX.XX USD
      **$XX.XX**              ← bold markdown (PXN)
      ~~$YY.YY~~              ← strikethrough regular price (PXN)
      Sale Price / Regular Price labels (PXN)
      $XX.XX USD $YY.YY USD   ← price range / sale+original
    """
    saw_sale_label = False
    for j in range(max_lookahead):
        idx = start_idx + j
        if idx >= len(lines):
            break
        nl = lines[idx].strip()
        if not nl:
            continue

        # Check for sale price label — the NEXT line with a dollar sign
        # is the sale price (PXN format: Sale Price \n **$XX.XX**)
        nl_lower = nl.lower()
        if "sale price" in nl_lower or "sale" in nl_lower:
            saw_sale_label = True

        # Match all USD prices on this line
        # Also handles **$XX.XX** (bold) and ~~$YY.YY~~ (strikethrough)
        prices = re.findall(r'\$([\d,]+(?:\.\d{2})?)', nl)
        if prices:
            # If we saw a "Sale Price" label, take the first price (the sale price)
            try:
                price = float(prices[0].replace(",", ""))
                if 5 < price < 10000:
                    return price
            except ValueError:
                continue
    return None


# ── Site-specific parsers ──────────────────────────────────────────────

def _clean_markdown_link(name: str) -> str:
    """Remove markdown link wrapper: [Text](url) → Text."""
    m = re.match(r'^\[(.+?)\]\(.*?\)$', name)
    return m.group(1).strip() if m else name


def _extract_product_name_from_line(line: str) -> str | None:
    """Extract product name from a heading line.

    Handles:
      ## Product Name
      ## [Product Name](url)       ← Fanatec-style link heading
      [## Product Name             ← link-embedded heading (Logitech)
      ### Product Name
    """
    s = line.strip()

    # Case 1: [## ... or [### ... — heading inside markdown link (Logitech)
    if s.startswith("[## ") or s.startswith("[### "):
        m = re.match(r'\[#+\s+(.+?)$', s)
        if m:
            return m.group(1).strip()

    # Case 2: ## [Product Name](url) — link heading (Fanatec)
    if s.startswith("## [") and "](http" in s:
        m = re.search(r'^##\s+\[(.+?)\]\(', s)
        if m:
            return m.group(1).strip()

    # Case 3: ## Product Name — standard heading
    if s.startswith("## ") and not s.startswith("### "):
        return _clean_markdown_link(s[3:].strip())

    # Case 4: ### Product Name — sub-heading
    if s.startswith("### "):
        return _clean_markdown_link(s[4:].strip())

    return None


def _parse_shopify_links(content: str, brand: str) -> list[dict]:
    """Parse Shopify storefront markdown in link-based format.

    Used by most Shopify sites (MOZA, PXN, Simagic, etc.) where
    products appear as markdown links followed by price lines:

      [Product Name](URL)
      $XX.XX USD

    Or with sale:
      [Product Name](URL)
      Sale price$XX.XX USDRegular price
      $YY.YY USD

    Or PXN-style:
      * [Add to Cart](URL)
        [Product Name](URL)
        Sale Price
        **$XX.XX**
        Regular Price
        ~~$YY.YY~~
    """
    products = []
    lines = content.split("\n")

    # Link skip patterns (navigation, action links — NOT products)
    # Only applied to short names (< 20 chars); longer names are products
    SKIP_LINK_PATTERNS = re.compile(
        r'^(add to cart|choose options|view|search|login|cart|'
        r'collections?|products?|filters?|sort|'
        r'facebook|twitter|instagram|youtube|tiktok|reddit|discord|'
        r'configurator|racing|flight|explore|support|about|'
        r'home|bundles?|wheel bases?|steering wheels?|pedals?|'
        r'accessor|shop now|sign in|create account|footer|'
        r'menu|subscribe|legal|privacy|terms|cookies)$',
        re.I
    )

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Match markdown link: [Product Name](URL)
        m = re.match(r'^\[(.+?)\]\(https?://[^)]+\)$', line)
        if m:
            name = m.group(1).strip()

            # Skip links that are very short or are navigation buttons
            if (len(name) < 6
                    or (len(name) < 20 and SKIP_LINK_PATTERNS.search(name))
                    or re.match(r'^(Only \d+ left|\d+\.\d+\'|\d+|\$[\d,]+|\*+)$', name)):
                i += 1
                continue

            # Seller rating / review stars
            if re.match(r'^\d+\.\d+\'?$', name):
                i += 1
                continue

            price = _extract_price_from_lines(lines, i + 1, max_lookahead=6)
            if price:
                # Clean name: remove trailing sale/badge annotations
                clean = re.sub(r'\s*[-–—]\s*(Sale|New|Best Seller).*$', '',
                               name, flags=re.I).strip()
                products.append({
                    "name": clean, "price": price, "brand": brand,
                })
        i += 1

    return products


def _parse_shopify(content: str, brand: str) -> list[dict]:
    """Parse Shopify storefront markdown.

    Two-phase: first try link-based format (most common), then
    fall back to heading-based format.

    Heading-based format:
      ## Product Title
      $XX.XX
      Add to cart

    Link-based format:
      [Product Name](URL)
      $XX.XX USD
    """
    # Phase 1: link-based (main format for modern Shopify themes)
    products = _parse_shopify_links(content, brand)
    if products:
        return products

    # Phase 2: heading-based (older Shopify themes)
    lines = content.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        name = _extract_product_name_from_line(line)

        if name and not _skip_heading(name):
            price = _extract_price_from_lines(lines, i + 1)
            if price:
                # Clean name: remove trailing sale/badge annotations
                clean = re.sub(r'\s*[-–—]\s*(Sale|New|Best Seller).*$', '',
                               name, flags=re.I).strip()
                products.append({
                    "name": clean, "price": price, "brand": brand,
                })
        i += 1

    return products


def _parse_logitech(content: str, brand: str) -> list[dict]:
    """Parse Logitech G driving products page.

    Logitech structure (observed from stealth-extract):
      ## RS50 Base
      8 Nm Direct Drive with TRUEFORCE Wheel Base
      Gift with Purchase
      $349.99 - $449.99           ← price range (take min)

      ## RS50 System
      ...
      $599.99 $699.99             ← sale price, original price (take first)
      $100.00 off

      ## RS Pedals
      ...
      $149.99 $159.99
      $10.00 off
    """
    products = []
    lines = content.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        name = _extract_product_name_from_line(line)

        if name and not _skip_heading(name):
            # Skip known non-product entries specific to Logitech
            nl = name.lower()
            if any(kw in nl for kw in [
                "build your", "play now pay", "trueforce technology",
                "subscribe to", "legal trademark", "faqs",
                "sim racing wheels, pedals",
            ]):
                i += 1
                continue

            price = _extract_price_from_lines(lines, i + 1, max_lookahead=8)
            if price:
                clean = re.sub(r'\s*[-–—]\s*(Shop|Buy|Learn More|Buy now).*$',
                               '', name, flags=re.I).strip()
                products.append({
                    "name": clean, "price": price, "brand": brand,
                })
        i += 1

    return products


def _parse_fanatec(content: str, brand: str) -> list[dict]:
    """Parse Fanatec category page markdown."""
    products = []
    lines = content.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        name = _extract_product_name_from_line(line)

        if name and not _skip_heading(name):
            price = _extract_price_from_lines(lines, i + 1)
            if price:
                products.append({
                    "name": name.strip(), "price": price, "brand": brand,
                })
        i += 1

    return products


def _parse_generic(content: str, brand: str) -> list[dict]:
    """Generic parser for any e-commerce site."""
    return _parse_shopify(content, brand)  # same heading+price pattern


EXTRACTORS = {
    "shopify": _parse_shopify,
    "logitech": _parse_logitech,
    "fanatec": _parse_fanatec,
    "generic": _parse_generic,
}


def extract_prices(content: str, brand: str, parser_name: str,
                    source_url: str = "") -> list[dict]:
    extractor = EXTRACTORS.get(parser_name, _parse_generic)
    products = extractor(content, brand)
    # Attach source URL to each product for category-constrained matching
    for p in products:
        p["source_url"] = source_url
    return products


# ── Category hints from URL ────────────────────────────────────────────
# Maps URL path patterns to category keywords for match constraint
URL_CATEGORY_HINTS: dict[str, list[str]] = {
    "sim-racing-bundles": ["bundle", "set", "ready2race", "ready 2 race"],
    "wheel-bases": ["wheel base", "base"],
    "steering-wheels": ["steering wheel", "wheel rim"],
    "wheel-rims": ["wheel rim"],
    "pedals": ["pedal"],
    "add-ons": ["shifter", "handbrake", "hub", "adapter", "mount",
                "clamp", "table", "accessory"],
    "cockpits": ["cockpit"],
    "collection": [],  # generic, no constraint
    "collections": [],  # generic, no constraint
}


def _url_category_hint(url: str) -> str | None:
    """Return a category hint from URL path, or None."""
    url_lower = url.lower()
    for pattern, _ in URL_CATEGORY_HINTS.items():
        if f"/c/{pattern}" in url_lower or f"/{pattern}" in url_lower:
            return pattern
    return None


# ── Product matching ────────────────────────────────────────────────────

# Accessory keywords — products containing these should only
# match other accessory products (not main wheel/bundle entries)
ACCESSORY_KEYWORDS_ = {
    "shifter", "handbrake", "clutch", "mount", "clamp",
    "adapter", "cable", "hub", "module", "table",
    "trophy", "playseat",
}

def _is_accessory(name: str) -> bool:
    """Check if a product name describes an accessory, not a main product."""
    nl = name.lower()
    return any(kw in nl for kw in ACCESSORY_KEYWORDS_)


def _cat_match_score(existing_cat: str, url_hint: str | None) -> int:
    """Score how well the existing product category matches the source URL.

    Returns 0 (no preference) to 3 (strong match).
    """
    if not url_hint or url_hint not in URL_CATEGORY_HINTS:
        return 0  # no URL hint → no preference
    cat_keywords = URL_CATEGORY_HINTS[url_hint]
    if not cat_keywords:
        return 0
    cat_lower = existing_cat.lower()
    for kw in cat_keywords:
        if kw in cat_lower:
            return 3  # strong match
    return 0


def match_product(extracted_name: str, existing: list[dict],
                  brand: str, source_url: str = "") -> dict | None:
    """Fuzzy-match extracted product name to existing prices.js entry.

    For Fanatec multi-page scraping, source_url provides category hints
    to avoid cross-category false matches (e.g. bundle price → single item).
    Candidates are scored and the best match is returned.
    """
    ex = extracted_name.lower().strip()
    ex_accessory = _is_accessory(ex)
    url_hint = _url_category_hint(source_url)

    # Collect model tokens from extracted name
    ex_model_tokens = set(re.findall(
        r'\b(R\d+|G\d+|T\d+|V\d+|P\d+|CSL|DD\d*|GT\s*(?:Neo|One|Pro)?|'
        r'FX\d*|EVO|Alpha|Initium|mBooster|TSW|ESX|HGP|HBP|SRP|CRP|'
        r'VD\d+|MHG|MH16|MA3X|MFY|MTP|MTQ|MTLP|MRP|TQB|TQA|AY210|'
        r'AB[69]|Alpha\s*Prime|WarBRD|STECS|Orion|RS\d*|H-Shifter)\b',
        ex, re.I))

    # Candidates: list of (product, score), higher score = better match
    candidates: list[tuple[dict, int]] = []
    GENERIC_MODEL_TOKENS = {
        "csl", "dd", "gt", "rs", "fx", "srp", "crp", "hgp",
        "hbp", "esx", "tsw", "evo", "alpha", "pro",
    }
    COMMON_WORDS = {
        "the", "a", "an", "and", "or", "of", "in", "for", "with",
        "wheel", "racing", "steering", "base", "drive", "direct",
        "pedal", "pedals", "simulator", "simulation", "sim",
        "pro", "set", "logitech", "force", "shifter", "handbrake",
    }

    for p in existing:
        if p["brand"] != brand:
            continue
        pl = p["name"].lower()
        p_accessory = _is_accessory(pl)
        cat_score = _cat_match_score(p.get("cat", ""), url_hint)
        base_score = 0

        # Accessory vs main product mismatch — skip
        if p_accessory != ex_accessory:
            continue

        # 1) Exact match
        if pl == ex:
            candidates.append((p, 100 + cat_score))
            continue

        # 2) Substring / contains match — but reject if scraped name
        #    has too many extra words (likely a different product variant)
        if pl in ex or ex in pl:
            # Check variant drift: existing significant words should be
            # at least 35% of scraped significant words
            ex_significant = set(ex.split()) - COMMON_WORDS
            pl_significant = set(pl.split()) - COMMON_WORDS
            overlap_ratio = len(pl_significant) / max(len(ex_significant), 1)
            if overlap_ratio >= 0.35:
                candidates.append((p, 80 + cat_score))
            # else: scraped name is too different, fall through to token match
            continue

        # 3) Token-based match
        p_model_tokens = set()
        if ex_model_tokens:
            p_model_tokens = set(re.findall(
                r'\b(R\d+|G\d+|T\d+|V\d+|P\d+|CSL|DD\d*|DD\+|GT\s*(?:Neo|One|Pro)?|'
                r'FX\d*|EVO|Alpha|Initium|mBooster|TSW|ESX|HGP|HBP|SRP|CRP|'
                r'VD\d+|MHG|MH16|MA3X|MFY|MTP|MTQ|MTLP|MRP|TQB|TQA|AY210|'
                r'AB[69]|Alpha\s*Prime|WarBRD|STECS|Orion|RS\d*|H-Shifter)\b',
                pl, re.I))

        if p_model_tokens:
            common_tokens = ex_model_tokens & p_model_tokens
            if common_tokens and p_model_tokens.issubset(ex_model_tokens):
                if len(common_tokens) >= 2:
                    candidates.append((p, 60 + cat_score))
                    continue
                # Single-token match
                token = next(iter(common_tokens)).lower()
                if re.search(r'\d+', token) and token not in GENERIC_MODEL_TOKENS:
                    candidates.append((p, 55 + cat_score))
                    continue
                # Generic single-token → check word overlap
                ex_words = set(ex.split()) - COMMON_WORDS
                p_words = set(pl.split()) - COMMON_WORDS
                if ex_words and p_words:
                    overlap = ex_words & p_words
                    if len(overlap) >= 2:
                        candidates.append((p, 40 + cat_score))
                        continue

        # 4) Significant word overlap fallback
        ex_words = set(ex.split()) - COMMON_WORDS
        p_words = set(pl.split()) - COMMON_WORDS
        if len(ex_words) >= 3 and p_words:
            overlap = ex_words & p_words
            if len(overlap) >= min(3, len(ex_words) // 2 + 1):
                candidates.append((p, 20 + cat_score))

    if not candidates:
        return None

    # Pick candidate with highest score (category-matched preferred)
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[0][0]


# Keep old function signature for backward compat (unused but safe)
def _match_product_legacy(extracted_name: str, existing: list[dict],
                          brand: str, source_url: str = "") -> dict | None:
    return match_product(extracted_name, existing, brand, source_url)


def update_price_in_js(content: str, product: dict,
                        new_price: float) -> tuple[str, bool]:
    """Replace a product's price in prices.js text. Returns (new_content, changed)."""
    name_escaped = re.escape(product["name"])
    brand_escaped = re.escape(product["brand"])
    cat_escaped = re.escape(product["cat"])
    pattern = (
        rf"(brand:\s*'{brand_escaped}'\s*,\s*"
        rf"cat:\s*'{cat_escaped}'\s*,\s*"
        rf"name:\s*'{name_escaped}'\s*,\s*"
        rf"price:\s*)([\d.]+)"
    )

    if abs(new_price - product["price"]) < 0.01:
        return content, False

    new_content = re.sub(pattern, rf"\g<1>{new_price}", content)
    return new_content, True


def update_timestamp(content: str) -> str:
    now = datetime.now().strftime("%Y-%m")
    return re.sub(
        r"Last (?:manual|auto) update: \d{4}-\d{2}",
        f"Last auto update: {now}", content,
    )


def load_scraper_log() -> dict:
    if os.path.exists(SCRAPER_LOG_PATH):
        try:
            with open(SCRAPER_LOG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"runs": []}


def save_scraper_log(log: dict) -> None:
    os.makedirs(os.path.dirname(SCRAPER_LOG_PATH), exist_ok=True)
    with open(SCRAPER_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


# ── Main ───────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description="MOZA Price Monitor — Update via BrowserAct stealth-extract"
    )
    ap.add_argument("--dry-run", action="store_true",
                    help="Preview only, no files written")
    ap.add_argument("--brand", type=str,
                    help="Single brand, e.g. MOZA or Fanatec")
    ap.add_argument("--timeout", type=int, default=STEALTH_TIMEOUT,
                    help=f"Seconds per stealth-extract (default {STEALTH_TIMEOUT})")
    ap.add_argument("--sequential", action="store_true",
                    help="Scrape URLs one-at-a-time (avoids rate limits)")
    ap.add_argument("--save-raw", type=str,
                    help="Save raw markdown output to directory for debugging")
    args = ap.parse_args()

    print("=" * 62)
    print("  MOZA Competitor Price Monitor — Price Update Tool")
    print(f"  Engine: BrowserAct stealth-extract v1.2.1")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 62)

    # Select brands
    if args.brand:
        if args.brand not in BRAND_CONFIGS:
            print(f"\n  ❌ Unknown brand: {args.brand}")
            print(f"  Available: {', '.join(BRAND_CONFIGS.keys())}")
            return 1
        brands = {args.brand: BRAND_CONFIGS[args.brand]}
        print(f"\n  🎯 Single brand: {args.brand}")
    else:
        brands = BRAND_CONFIGS
        print(f"\n  🌐 All brands: {len(brands)}")

    # Read existing data
    print("\n  📖 Reading prices.js...")
    current = read_prices_js()
    existing = parse_js_products(current)
    print(f"  Loaded {len(existing)} products across "
          f"{len(set(p['brand'] for p in existing))} brands")

    # Collect all URLs to scrape
    all_urls: list[tuple[str, str]] = []  # (brand, url)
    for brand, cfg in brands.items():
        for u in cfg["urls"]:
            all_urls.append((brand, u))

    # ── Scrape ──
    mode = "sequential" if args.sequential else "parallel"
    print(f"\n  🔍 Scraping {len(all_urls)} URLs ({mode}, "
          f"timeout={args.timeout}s)...\n")

    scrape_results: dict[str, list[dict]] = {}  # brand → list of per-URL results

    if args.sequential:
        for brand, url in all_urls:
            r = call_stealth_extract(url, args.timeout)
            scrape_results.setdefault(brand, []).append(r)
            status = "✅" if r["success"] else "❌"
            clen = len(r["content"]) if r["success"] else 0
            print(f"  {status} {brand:14s} | {r['elapsed']:5.1f}s  "
                  f"({clen:,} chars)"
                  + (f"  ERR: {r['error'][:70]}" if not r["success"] else ""))
    else:
        with ThreadPoolExecutor(max_workers=4) as ex:
            futures = {}
            for brand, url in all_urls:
                f = ex.submit(call_stealth_extract, url, args.timeout)
                futures[f] = (brand, url)

            for f in as_completed(futures):
                brand, url = futures[f]
                r = f.result()
                scrape_results.setdefault(brand, []).append(r)
                status = "✅" if r["success"] else "❌"
                clen = len(r["content"]) if r["success"] else 0
                print(f"  {status} {brand:14s} | {r['elapsed']:5.1f}s  "
                      f"({clen:,} chars)"
                      + (f"  ERR: {r['error'][:70]}" if not r["success"] else ""))

    # Save raw for debugging
    if args.save_raw:
        os.makedirs(args.save_raw, exist_ok=True)
        for brand, results in scrape_results.items():
            for i, r in enumerate(results):
                if r["success"]:
                    fname = f"{brand}_{i}.md"
                    path = os.path.join(args.save_raw, fname)
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(r["content"])
        print(f"\n  💾 Raw output saved to {args.save_raw}/")

    # ── Parse ──
    print(f"\n  📊 Parsing extracted prices...")
    all_updates: list[dict] = []

    for brand, cfg in brands.items():
        results = scrape_results.get(brand, [])
        extracted: list[dict] = []
        for r in results:
            if r["success"]:
                extracted += extract_prices(
                    r["content"], brand, cfg["parser"], source_url=r["url"]
                )

        if not extracted:
            print(f"\n  ⚠️  {brand}: no products extracted ("
                  f"{sum(1 for r in results if r['success'])} pages ok, "
                  f"{sum(1 for r in results if not r['success'])} failed)")
            continue

        print(f"\n  🏷️  {brand}: {len(extracted)} products found in page"
              + ("s" if len(results) > 1 else ""))

        matched = 0
        unmatched: list[dict] = []
        for ep in extracted[:80]:
            # For multi-page brands, filter candidates by URL category
            src_url = ep.get("source_url", "")
            candidates = existing
            url_hint = _url_category_hint(src_url)
            if url_hint and len(brands.get(brand, {}).get("urls", [])) > 1:
                # Multi-page brand: only match against same-category products
                hint_kws = URL_CATEGORY_HINTS.get(url_hint, [])
                if hint_kws:
                    candidates = [
                        p for p in existing
                        if p["brand"] == brand
                        and any(kw in p.get("cat", "").lower() for kw in hint_kws)
                    ]
            match = match_product(ep["name"], candidates, brand,
                                  source_url=src_url)
            if match:
                matched += 1
                if abs(ep["price"] - match["price"]) > 0.01:
                    all_updates.append({
                        "brand": brand,
                        "product": match["name"],
                        "old_price": match["price"],
                        "new_price": ep["price"],
                        "scraped_name": ep["name"],
                    })
                    print(f"     🔄 {match['name'][:50]:50s}  "
                          f"${match['price']:>8.2f} → ${ep['price']:>8.2f}")
            else:
                unmatched.append(ep)

        if matched == 0:
            print(f"     ⚠️  0 of {len(extracted)} matched to known products")
        elif unmatched:
            print(f"     ℹ️  {matched} matched, {len(unmatched)} unmatched: "
                  + ", ".join(p["name"][:40] for p in unmatched[:5])
                  + (f" (+{len(unmatched)-5} more)" if len(unmatched) > 5 else ""))

    # ── Summary ──
    print(f"\n  {'─' * 60}")
    print(f"  📝 {len(all_updates)} price changes detected\n")

    if not all_updates:
        print("  ✅ All prices up to date.")
    else:
        for u in all_updates:
            diff = u["new_price"] - u["old_price"]
            arrow = "📈" if diff > 0 else "📉"
            print(f"  {arrow} {u['brand']:12s} | {u['product'][:45]:45s} | "
                  f"${u['old_price']:>8.2f} → ${u['new_price']:>8.2f} "
                  f"({diff:+.2f})")

    # ── Write ──
    if args.dry_run:
        print(f"\n  🧪 DRY RUN — no files written.")
        print(f"  Would update {len(all_updates)} prices.")
    elif all_updates:
        print(f"\n  💾 Applying {len(all_updates)} updates...")
        new_content = current
        for u in all_updates:
            for p in existing:
                if p["brand"] == u["brand"] and p["name"] == u["product"]:
                    nc, changed = update_price_in_js(new_content, p, u["new_price"])
                    if changed:
                        new_content = nc
                        p["price"] = u["new_price"]
                    break

        new_content = update_timestamp(new_content)
        write_prices_js(new_content)
        print(f"  ✅ Written to data/prices.js")

        log = load_scraper_log()
        log["runs"].append({
            "timestamp": datetime.now().isoformat(),
            "brands": len(brands),
            "updates": all_updates,
        })
        log["runs"] = log["runs"][-30:]
        save_scraper_log(log)
        print(f"  ✅ Logged to data/scraper_log.json")
    else:
        print(f"\n  ✅ No changes — prices.js is current.")

    print(f"\n  {'=' * 62}")
    print(f"  Done: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  {'=' * 62}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

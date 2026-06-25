"""
sites/books_toscrape.py
------------------------
Adapter for https://books.toscrape.com/

This site is purpose-built for scraping practice, so it's a safe, stable
target with no ToS restrictions. Each adapter module exposes two things:

    SITE_NAME      -> short identifier used in the database
    parse(html)    -> takes raw HTML text, returns a dict:
                        {"title": str, "price": float, "currency": str, "in_stock": bool}

Keeping every site's parsing logic in its own small file means adding a
new site later is just: write a new adapter, register it in config.py.
"""

from bs4 import BeautifulSoup

SITE_NAME = "books_toscrape"


def parse(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")

    # Title lives in the product main page under <h1>
    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else "Unknown title"

    # Price lives inside <p class="price_color">£51.77</p>
    price_tag = soup.find("p", class_="price_color")
    raw_price = price_tag.get_text(strip=True) if price_tag else ""

    # Strip currency symbol, keep the numeric value
    currency = "GBP" if "£" in raw_price else "USD"
    price_value = _extract_number(raw_price)

    # Stock status: <p class="instock availability"> ... In stock (22 available) ... </p>
    stock_tag = soup.find("p", class_="instock availability")
    in_stock = stock_tag is not None and "in stock" in stock_tag.get_text(strip=True).lower()

    return {
        "title": title,
        "price": price_value,
        "currency": currency,
        "in_stock": in_stock,
    }


def _extract_number(text: str) -> float:
    """Pulls the first valid float out of a price string like '£51.77'."""
    digits = "".join(ch for ch in text if ch.isdigit() or ch == ".")
    try:
        return float(digits)
    except ValueError:
        return 0.0

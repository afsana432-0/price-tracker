"""
sites/webscraper_sandbox.py
-----------------------------
Adapter for https://webscraper.io/test-sites/e-commerce/allinone
This is webscraper.io's official public test sandbox, built specifically
so people can practice scraping real e-commerce-style HTML without hitting
a live retailer (which would risk ToS violations).

Same contract as every other adapter: parse(html) -> dict.
"""

from bs4 import BeautifulSoup

SITE_NAME = "webscraper_sandbox"


def parse(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")

    # Product title: <h4 class="title">...</h4>
    title_tag = soup.find("h4", class_="title")
    title = title_tag.get_text(strip=True) if title_tag else "Unknown title"

    # Price: <h4 class="price float-end card-title">$295.99</h4>
    price_tag = soup.find("h4", class_="price")
    raw_price = price_tag.get_text(strip=True) if price_tag else ""
    price_value = _extract_number(raw_price)

    # This sandbox doesn't expose live stock status, so we assume in stock
    # whenever we successfully find a price. Documented here so it's clear
    # this is a deliberate simplification, not a bug.
    in_stock = price_value > 0

    return {
        "title": title,
        "price": price_value,
        "currency": "USD",
        "in_stock": in_stock,
    }


def _extract_number(text: str) -> float:
    digits = "".join(ch for ch in text if ch.isdigit() or ch == ".")
    try:
        return float(digits)
    except ValueError:
        return 0.0

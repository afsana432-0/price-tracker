"""
scraper.py
----------
The core engine. For every product in config.TRACKED_PRODUCTS, this:
  1. Sends an HTTP GET request (checking status code)
  2. Hands the HTML to the right site adapter to parse
  3. Stores the result in SQLite via db.py
  4. Compares against the previous price reading to detect a drop
  5. Logs everything to logs/scraper.log

Run directly for a one-off scrape:
    python scraper.py

Run on a schedule via scheduler.py instead for continuous tracking.
"""

import logging
import time
from pathlib import Path

import requests

import db
import config

LOG_PATH = Path(__file__).parent / "logs" / "scraper.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler(),  # also print to console
    ],
)
logger = logging.getLogger(__name__)


def fetch_html(url: str) -> str | None:
    """
    Sends a GET request and returns the page HTML.
    Returns None (and logs a warning) if the request fails or the
    status code indicates an error, instead of crashing the whole run.
    """
    headers = {"User-Agent": config.USER_AGENT}
    try:
        response = requests.get(url, headers=headers, timeout=10)
    except requests.exceptions.RequestException as exc:
        logger.warning(f"Request failed for {url}: {exc}")
        return None

    # Treat anything outside 200-299 as a failure worth logging.
    if not response.ok:
        logger.warning(f"Bad status code {response.status_code} for {url}")
        return None

    return response.text


def check_price_drop(product_id: int, new_price: float, title: str):
    """
    Compares the new price against the previous reading (if one exists)
    and logs a clear alert when the price has dropped.
    """
    history = db.get_last_two_prices(product_id)

    # history[0] is the row we just inserted (newest), history[1] is the
    # one before that. We need at least 2 readings to compare.
    if len(history) < 2:
        return

    previous_price = history[1]["price"]

    if new_price < previous_price:
        drop = previous_price - new_price
        pct = (drop / previous_price) * 100 if previous_price else 0
        logger.info(
            f"PRICE DROP: '{title}' fell from {previous_price:.2f} to "
            f"{new_price:.2f} (-{pct:.1f}%)"
        )
    elif new_price > previous_price:
        logger.info(f"Price increased for '{title}': {previous_price:.2f} -> {new_price:.2f}")
    else:
        logger.info(f"No price change for '{title}' ({new_price:.2f})")


def run_once():
    """Scrapes every tracked product exactly one time."""
    db.init_db()
    logger.info(f"Starting scrape run for {len(config.TRACKED_PRODUCTS)} product(s)")

    for entry in config.TRACKED_PRODUCTS:
        site = entry["site"]
        url = entry["url"]
        adapter = entry["adapter"]

        html = fetch_html(url)
        if html is None:
            continue  # already logged inside fetch_html

        try:
            parsed = adapter(html)
        except Exception as exc:
            logger.error(f"Failed to parse {url}: {exc}")
            continue

        product_id = db.upsert_product(site=site, url=url, title=parsed["title"])
        db.record_price(
            product_id=product_id,
            price=parsed["price"],
            currency=parsed["currency"],
            in_stock=parsed["in_stock"],
        )

        logger.info(
            f"[{site}] '{parsed['title']}' -> {parsed['price']} {parsed['currency']} "
            f"({'in stock' if parsed['in_stock'] else 'out of stock'})"
        )

        check_price_drop(product_id, parsed["price"], parsed["title"])

        time.sleep(config.REQUEST_DELAY_SECONDS)

    logger.info("Scrape run complete.\n")


if __name__ == "__main__":
    run_once()

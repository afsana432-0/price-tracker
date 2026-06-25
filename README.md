# Automated Price Tracker

A scheduled web scraper that tracks product prices across multiple
e-commerce sites, stores time-series price data in SQLite, and detects
price drops automatically. Built as a portfolio project demonstrating
a production-style data acquisition pipeline.

## What it does

1. **Scrapes** product pages from multiple sites using `requests` + `BeautifulSoup`
2. **Validates** every HTTP response (status codes, error handling) before parsing
3. **Parses** HTML using site-specific adapters (easy to extend to new sites)
4. **Stores** every price reading as a time-series row in SQLite — never overwrites history
5. **Detects** price drops by comparing each new reading against the previous one
6. **Schedules** itself to run automatically every N minutes, indefinitely
7. **Logs** every run to both the console and a persistent log file

## Why this design

- **Site adapters are isolated** (`sites/` folder) — adding a new site means writing
  one small `parse()` function, not touching the core engine.
- **Time-series, not snapshot** — `price_history` keeps every reading, so you can
  later plot trends or find the all-time low, not just "what's the price right now."
- **Defensive networking** — bad status codes, timeouts, and connection errors are
  caught and logged instead of crashing the whole run. One broken URL doesn't take
  down the rest of the batch.
- **Polite scraping** — a small delay between requests and a transparent custom
  User-Agent string, so this behaves like a respectful, identifiable bot.

## Project structure

```
price-tracker/
├── config.py           # list of tracked products + scrape interval
├── db.py                # SQLite schema + read/write helpers
├── scraper.py           # core engine: fetch -> parse -> store -> detect drops
├── scheduler.py         # runs scraper.py on a recurring timer
├── sites/
│   ├── books_toscrape.py        # adapter for books.toscrape.com
│   └── webscraper_sandbox.py    # adapter for webscraper.io test sandbox
├── data/
│   └── price_tracker.db         # SQLite database (created on first run)
└── logs/
    └── scraper.log               # run history and price-drop alerts
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

**Run once** (single scrape of all tracked products):
```bash
python scraper.py
```

**Run continuously** (scrapes every `SCRAPE_INTERVAL_MINUTES`, set in `config.py`):
```bash
python scheduler.py
```
Leave it running in a terminal, or set it up as a background service / cron job
for true "set and forget" tracking.

## Adding a new product to track

Open `config.py` and add an entry to `TRACKED_PRODUCTS`:
```python
{
    "site": books_toscrape.SITE_NAME,
    "url": "https://books.toscrape.com/catalogue/some-other-book/index.html",
    "adapter": books_toscrape.parse,
},
```

## Adding a new site

1. Create `sites/your_site.py`
2. Define `SITE_NAME = "your_site"`
3. Define `parse(html: str) -> dict` returning `{"title", "price", "currency", "in_stock"}`
4. Import it in `config.py` and add product entries using that adapter

## Sites used in this demo

- [books.toscrape.com](https://books.toscrape.com) — a public sandbox site built
  specifically for scraping practice, so it's safe to use with no ToS concerns.
- [webscraper.io test sandbox](https://webscraper.io/test-sites/e-commerce/allinone) —
  webscraper.io's own official testing playground for e-commerce-style scraping.

Both are designed to be scraped, which is why they were chosen over a real retailer.

## Possible extensions

- Add email/SMS alerts when a price drop exceeds a threshold
- Plot price history with matplotlib for a visual trend chart
- Add more site adapters to track a wider product catalog
- Swap SQLite for PostgreSQL for a more production-like setup

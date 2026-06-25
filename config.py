"""
config.py
---------
Central list of products to track. To add a new product, add a dict here.
To add a new site, write an adapter in sites/ and import it below.

Each entry needs:
    "site"    -> matches the adapter's SITE_NAME, used as a DB key
    "url"     -> the exact product page to scrape
    "adapter" -> the parse() function to use for this URL
"""

from sites import books_toscrape, webscraper_sandbox

TRACKED_PRODUCTS = [
    {
        "site": books_toscrape.SITE_NAME,
        "url": "https://books.toscrape.com/catalogue/the-grand-design_405/index.html",
        "adapter": books_toscrape.parse,
    },
    {
        "site": books_toscrape.SITE_NAME,
        "url": "https://books.toscrape.com/catalogue/sapiens-a-brief-history-of-humankind_996/index.html",
        "adapter": books_toscrape.parse,
    },
    {
        "site": webscraper_sandbox.SITE_NAME,
        "url": "https://webscraper.io/test-sites/e-commerce/allinone/product/123",
        "adapter": webscraper_sandbox.parse,
    },
]

# How often to run the scrape, in minutes. Used by scheduler.py.
SCRAPE_INTERVAL_MINUTES = 60

# Be polite: pause this many seconds between hitting different URLs,
# so we don't hammer any one site with rapid-fire requests.
REQUEST_DELAY_SECONDS = 2

# Custom User-Agent so site owners can see this traffic is a transparent,
# identifiable bot rather than something pretending to be a browser.
USER_AGENT = "Mozilla/5.0 (compatible; AfsanaPriceTracker/1.0; educational project)"

"""
simulate_price_drop.py
------------------------
A demo script — NOT part of the core pipeline — that lets you watch the
price-drop detection logic fire without waiting for a real price to change.

What it does:
  1. Picks the first product in your database
  2. Inserts a fake "previous" price reading that's higher than the current one
  3. Re-runs the same check_price_drop() function the real scraper uses
  4. You'll see a PRICE DROP alert in the console/log, using real code paths

This is safe to run any time — it only adds an extra row to price_history,
it doesn't delete or modify anything.
"""

import sqlite3
from datetime import datetime, timedelta, timezone

import db
import scraper

conn = db.get_connection()
cur = conn.cursor()

# Grab the first tracked product
cur.execute("SELECT id, title FROM products LIMIT 1")
row = cur.fetchone()

if row is None:
    print("No products found yet. Run 'python scraper.py' at least once first.")
else:
    product_id = row["id"]
    title = row["title"]

    # Get the most recent real price for this product
    cur.execute(
        "SELECT price, currency FROM price_history WHERE product_id = ? ORDER BY scraped_at DESC LIMIT 1",
        (product_id,),
    )
    latest = cur.fetchone()
    current_price = latest["price"]
    currency = latest["currency"]

    # Insert a fake reading from "1 hour ago" that's 20% higher, so the
    # real current price will look like a drop when we compare against it.
    fake_old_price = round(current_price * 1.20, 2)
    fake_timestamp = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()

    cur.execute(
        """INSERT INTO price_history (product_id, price, currency, in_stock, scraped_at)
           VALUES (?, ?, ?, 1, ?)""",
        (product_id, fake_old_price, currency, fake_timestamp),
    )
    conn.commit()

    print(f"Simulated: '{title}' was {fake_old_price} {currency} one hour ago.")
    print(f"Current real price in your database: {current_price} {currency}")
    print()
    print("Running the real check_price_drop() function now...")
    print("-" * 60)

    scraper.check_price_drop(product_id, current_price, title)

conn.close()

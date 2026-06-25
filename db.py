"""
db.py
-----
Handles all SQLite storage for the price tracker.

Schema:
    products        -> one row per tracked product (site + url is unique)
    price_history    -> one row per price reading (time-series data)

Design choice: we never overwrite a product's price. Instead we INSERT a
new row into price_history every time we scrape, so we keep a full
time-series and can later plot trends or compute "lowest price ever".
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "data" / "price_tracker.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_connection():
    """Returns a sqlite3 connection with foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Creates tables if they don't already exist. Safe to call every run."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site TEXT NOT NULL,
            url TEXT NOT NULL,
            title TEXT,
            first_seen TEXT NOT NULL,
            UNIQUE(site, url)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            price REAL,
            currency TEXT,
            in_stock INTEGER,
            scraped_at TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    conn.commit()
    conn.close()


def upsert_product(site: str, url: str, title: str) -> int:
    """
    Inserts the product if it's new, otherwise leaves it untouched.
    Returns the product's internal id either way.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM products WHERE site = ? AND url = ?", (site, url))
    row = cur.fetchone()

    if row:
        product_id = row["id"]
    else:
        cur.execute(
            "INSERT INTO products (site, url, title, first_seen) VALUES (?, ?, ?, ?)",
            (site, url, title, datetime.utcnow().isoformat()),
        )
        conn.commit()
        product_id = cur.lastrowid

    conn.close()
    return product_id


def record_price(product_id: int, price: float, currency: str, in_stock: bool):
    """Inserts a new time-series price reading for a product."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO price_history (product_id, price, currency, in_stock, scraped_at)
           VALUES (?, ?, ?, ?, ?)""",
        (product_id, price, currency, int(in_stock), datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def get_last_two_prices(product_id: int):
    """
    Returns the two most recent price readings for a product, newest first.
    Used to detect price drops between consecutive scrapes.
    Returns a list of 0, 1, or 2 sqlite3.Row objects.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT price, scraped_at FROM price_history
           WHERE product_id = ?
           ORDER BY scraped_at DESC LIMIT 2""",
        (product_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_price_history(product_id: int):
    """Returns the full price history for a product, oldest first."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT price, currency, in_stock, scraped_at FROM price_history
           WHERE product_id = ? ORDER BY scraped_at ASC""",
        (product_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows

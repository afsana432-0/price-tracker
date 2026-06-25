"""
scheduler.py
------------
Runs scraper.run_once() on a recurring interval, using the `schedule`
library. This is what makes the tracker "automated" rather than a
one-shot script you have to remember to run manually.

Usage:
    python scheduler.py

Leave this running in a terminal (or as a background service) and it
will scrape every config.SCRAPE_INTERVAL_MINUTES minutes, forever,
until you stop it with Ctrl+C.
"""

import time
import schedule

import config
from scraper import run_once, logger


def job():
    logger.info("Scheduled job triggered.")
    run_once()


def main():
    logger.info(
        f"Scheduler starting. Will scrape every "
        f"{config.SCRAPE_INTERVAL_MINUTES} minute(s). Press Ctrl+C to stop."
    )

    # Run once immediately on startup, so you don't have to wait a full
    # interval to see the first result.
    job()

    schedule.every(config.SCRAPE_INTERVAL_MINUTES).minutes.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user.")

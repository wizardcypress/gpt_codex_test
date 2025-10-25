from __future__ import annotations

import logging

from app.fetcher import refresh_market_data
from app.database import init_db

logging.basicConfig(level=logging.INFO)


def main() -> None:
    init_db()
    refresh_market_data()


if __name__ == "__main__":
    main()

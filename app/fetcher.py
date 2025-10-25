from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import requests

from .database import session_scope
from .models import IndexSnapshot, StockSnapshot

logger = logging.getLogger(__name__)

INDEX_QUOTES_URL = "https://query1.finance.yahoo.com/v7/finance/quote"
DAY_GAINERS_URL = (
    "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved"
)
INDEX_SYMBOLS = {
    "^IXIC": "NASDAQ Composite",
    "^GSPC": "S&P 500",
}


class MarketDataError(RuntimeError):
    """Raised when we fail to retrieve or persist market data."""


def _get_json(url: str, params: dict[str, Any] | None = None) -> Any:
    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    return response.json()


def fetch_index_snapshots() -> list[IndexSnapshot]:
    params = {"symbols": ",".join(INDEX_SYMBOLS.keys())}
    payload = _get_json(INDEX_QUOTES_URL, params=params)

    results = payload.get("quoteResponse", {}).get("result", [])
    snapshots: list[IndexSnapshot] = []
    as_of = datetime.now(timezone.utc)

    for item in results:
        symbol = item.get("symbol")
        if symbol not in INDEX_SYMBOLS:
            continue
        snapshots.append(
            IndexSnapshot(
                symbol=symbol,
                name=INDEX_SYMBOLS[symbol],
                price=float(item.get("regularMarketPrice", 0.0)),
                change=float(item.get("regularMarketChange", 0.0)),
                percent_change=float(item.get("regularMarketChangePercent", 0.0)),
                fetched_at=as_of,
            )
        )
    return snapshots


def fetch_top_gainers(limit: int = 100) -> list[StockSnapshot]:
    params = {"scrIds": "day_gainers", "count": str(limit)}
    payload = _get_json(DAY_GAINERS_URL, params=params)
    results = (
        payload.get("finance", {})
        .get("result", [{}])[0]
        .get("quotes", [])
    )
    as_of = datetime.now(timezone.utc)
    snapshots: list[StockSnapshot] = []
    for idx, quote in enumerate(results[:limit], start=1):
        price = quote.get("regularMarketPrice")
        change = quote.get("regularMarketChange")
        percent_change = quote.get("regularMarketChangePercent")
        snapshots.append(
            StockSnapshot(
                symbol=str(quote.get("symbol", "")),
                short_name=str(quote.get("shortName") or quote.get("longName") or ""),
                price=float(price or 0.0),
                change=float(change or 0.0),
                percent_change=float(percent_change or 0.0),
                volume=float(quote.get("regularMarketVolume"))
                if quote.get("regularMarketVolume") is not None
                else None,
                rank=idx,
                fetched_at=as_of,
            )
        )
    return snapshots


def refresh_market_data() -> None:
    try:
        index_snapshots = fetch_index_snapshots()
        stock_snapshots = fetch_top_gainers()
    except Exception as exc:  # pragma: no cover - network errors
        logger.exception("Failed to fetch market data: %s", exc)
        raise MarketDataError("Unable to fetch market data") from exc

    with session_scope() as session:
        for snapshot in index_snapshots:
            session.add(snapshot)

        for snapshot in stock_snapshots:
            session.add(snapshot)

    logger.info(
        "Stored %d index snapshots and %d stock snapshots",
        len(index_snapshots),
        len(stock_snapshots),
    )

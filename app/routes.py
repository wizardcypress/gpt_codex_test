from __future__ import annotations

from datetime import datetime

from flask import Blueprint, render_template
from sqlalchemy import func

from .database import session_scope
from .models import IndexSnapshot, StockSnapshot

bp = Blueprint("main", __name__)


def _format_last_updated(timestamp: datetime | None) -> str | None:
    if timestamp is None:
        return None
    return timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")


@bp.route("/")
def dashboard():
    with session_scope() as session:
        latest_index_times = (
            session.query(
                IndexSnapshot.symbol, func.max(IndexSnapshot.fetched_at)
            )
            .group_by(IndexSnapshot.symbol)
            .all()
        )

        indices_by_symbol = {}
        for symbol, fetched_at in latest_index_times:
            snapshot = (
                session.query(IndexSnapshot)
                .filter(
                    IndexSnapshot.symbol == symbol,
                    IndexSnapshot.fetched_at == fetched_at,
                )
                .first()
            )
            if snapshot is not None:
                indices_by_symbol[symbol] = snapshot

        latest_stock_time = session.query(func.max(StockSnapshot.fetched_at)).scalar()
        top_stocks = []
        if latest_stock_time is not None:
            top_stocks = (
                session.query(StockSnapshot)
                .filter(StockSnapshot.fetched_at == latest_stock_time)
                .order_by(StockSnapshot.rank)
                .all()
            )

    last_updated_candidates = [
        latest_stock_time,
        max((index.fetched_at for index in indices_by_symbol.values()), default=None),
    ]
    last_updated = _format_last_updated(
        max((ts for ts in last_updated_candidates if ts is not None), default=None)
    )

    sorted_indices = sorted(indices_by_symbol.values(), key=lambda s: s.symbol)

    return render_template(
        "index.html",
        indices=sorted_indices,
        top_stocks=top_stocks,
        last_updated=last_updated,
    )

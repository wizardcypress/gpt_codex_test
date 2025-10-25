from __future__ import annotations

import atexit
import logging

from apscheduler.schedulers.background import BackgroundScheduler

from .fetcher import refresh_market_data

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def init_scheduler(app) -> None:
    global _scheduler
    if _scheduler is not None:
        return

    refresh_minutes = float(app.config.get("REFRESH_MINUTES", 15))
    interval = max(refresh_minutes, 1)

    scheduler = BackgroundScheduler()
    scheduler.add_job(refresh_market_data, "interval", minutes=interval, max_instances=1)

    @app.before_serving
    def _start_scheduler():  # pragma: no cover - flask hook
        if not scheduler.running:
            logger.info("Starting background scheduler with interval=%s minutes", interval)
            scheduler.start()
            try:
                refresh_market_data()
            except Exception:  # pragma: no cover - network errors
                logger.exception("Initial market data refresh failed")

    @app.after_serving
    def _shutdown_scheduler(exception):  # pragma: no cover - flask hook
        if scheduler.running:
            logger.info("Stopping background scheduler")
            scheduler.shutdown(wait=False)

    atexit.register(lambda: scheduler.shutdown(wait=False) if scheduler.running else None)

    _scheduler = scheduler

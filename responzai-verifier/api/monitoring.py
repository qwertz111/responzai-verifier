# api/monitoring.py
# Pipeline-Monitoring: Error-Log, Health-Check, Uptime

import time
import logging
from collections import deque
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger("responzai.monitoring")

# In-Memory Ringpuffer fuer die letzten 100 Fehler
_error_log: deque = deque(maxlen=100)

# Tracking
_start_time = time.time()
_pipeline_runs = {"total": 0, "success": 0, "failed": 0}


def log_pipeline_error(
    source: str,
    error: Exception,
    context: Optional[dict] = None,
):
    """Loggt einen Pipeline-Fehler in den Ringpuffer und ins Logging."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "error_type": type(error).__name__,
        "message": str(error),
        "context": context or {},
    }
    _error_log.append(entry)
    _pipeline_runs["failed"] += 1
    logger.error(f"Pipeline error in {source}: {error}", exc_info=True)


def log_pipeline_success():
    """Zaehlt einen erfolgreichen Pipeline-Durchlauf."""
    _pipeline_runs["success"] += 1


def log_pipeline_start():
    """Zaehlt einen gestarteten Pipeline-Durchlauf."""
    _pipeline_runs["total"] += 1


def get_errors(limit: int = 20) -> list:
    """Gibt die letzten N Fehler zurueck (neueste zuerst)."""
    errors = list(_error_log)
    errors.reverse()
    return errors[:limit]


def get_stats() -> dict:
    """Gibt Pipeline-Statistiken zurueck."""
    uptime_seconds = time.time() - _start_time
    return {
        "uptime_seconds": int(uptime_seconds),
        "uptime_human": _format_uptime(uptime_seconds),
        "pipeline_runs": dict(_pipeline_runs),
        "recent_errors": len(_error_log),
    }


def _format_uptime(seconds: float) -> str:
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"

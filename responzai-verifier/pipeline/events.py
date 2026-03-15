# pipeline/events.py

import asyncio
import json
from datetime import datetime, timezone


class PipelineEventBus:
    """In-memory async event bus for a single pipeline run."""

    def __init__(self):
        self._queue: asyncio.Queue = asyncio.Queue()

    async def emit(self, event_type: str, data: dict):
        event = {
            "type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **data,
        }
        await self._queue.put(event)

    async def finish(self):
        await self._queue.put(None)

    async def stream(self):
        while True:
            event = await self._queue.get()
            if event is None:
                break
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

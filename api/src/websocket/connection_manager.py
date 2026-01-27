"""WebSocket connection manager for broadcasting allergen updates."""

import asyncio
import json
import logging
import threading
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Singleton class managing WebSocket connections."""

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self._connections: set[WebSocket] = set()
        self._loop: asyncio.AbstractEventLoop | None = None

    @classmethod
    def get_instance(cls) -> "ConnectionManager":
        """Get or create the singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def set_event_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Set the event loop for async operations from sync context."""
        self._loop = loop

    async def connect(self, websocket: WebSocket) -> None:
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self._connections.add(websocket)
        logger.info(
            "WebSocket client connected. Total connections: %d", len(self._connections)
        )

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        self._connections.discard(websocket)
        logger.info(
            "WebSocket client disconnected. Total connections: %d",
            len(self._connections),
        )

    async def broadcast(self, data: dict[str, Any]) -> None:
        """Send data to all connected clients."""
        if not self._connections:
            return

        message = json.dumps(data)
        disconnected = set()

        for connection in self._connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.warning("Failed to send to WebSocket client: %s", e)
                disconnected.add(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self._connections.discard(connection)

    def broadcast_sync(self, data: dict[str, Any]) -> None:
        """Synchronous wrapper for broadcast, used from Firebase callback thread."""
        if not self._loop:
            logger.warning("Event loop not set, cannot broadcast")
            return

        if not self._connections:
            return

        try:
            # Schedule the broadcast coroutine in the main event loop
            asyncio.run_coroutine_threadsafe(self.broadcast(data), self._loop)
            logger.info("Scheduled broadcast to %d clients", len(self._connections))
        except Exception as e:
            logger.error("Failed to schedule broadcast: %s", e)

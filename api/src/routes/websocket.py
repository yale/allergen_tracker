"""WebSocket endpoint for real-time allergen updates."""

import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from services.realtime_listener import AllergenCache
from websocket.connection_manager import ConnectionManager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/allergens")
async def websocket_allergens(websocket: WebSocket):
    """WebSocket endpoint for real-time allergen updates."""
    manager = ConnectionManager.get_instance()
    await manager.connect(websocket)

    try:
        # Send current allergen data immediately on connect
        cache = AllergenCache.get_instance()
        allergens, last_updated = cache.get_allergens()

        if allergens:
            await websocket.send_json({
                "type": "update",
                "allergens": allergens,
                "last_updated": last_updated.isoformat() if last_updated else None
            })

        # Keep connection alive waiting for messages/disconnect
        while True:
            # Wait for any message (could be ping/pong or client disconnect)
            await websocket.receive_text()

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected normally")
    except Exception as e:
        logger.warning("WebSocket error: %s", e)
    finally:
        manager.disconnect(websocket)

"""Push notification routes."""

import logging
import os
from typing import Dict, Any

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.push_service import PushService

load_dotenv()

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize push service
push_service = PushService()


class SubscriptionInfo(BaseModel):
    """Push subscription information."""
    endpoint: str
    keys: Dict[str, str]
    expirationTime: int | None = None


@router.get("/push/vapid-public-key")
async def get_vapid_public_key():
    """Get VAPID public key for push subscriptions."""
    try:
        public_key = push_service.get_public_key()
        if not public_key:
            raise HTTPException(
                status_code=500,
                detail="VAPID keys not configured. Please set VAPID_PRIVATE_KEY and VAPID_PUBLIC_KEY environment variables."
            )
        return {"publicKey": public_key}
    except Exception as e:
        logger.error(f"Error getting VAPID public key: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/push/subscribe")
async def subscribe_to_push(subscription: SubscriptionInfo):
    """Subscribe to push notifications."""
    try:
        success = await push_service.add_subscription(subscription.model_dump())
        if success:
            return {"status": "subscribed"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save subscription")
    except Exception as e:
        logger.error(f"Error subscribing to push: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/push/unsubscribe")
async def unsubscribe_from_push(subscription: SubscriptionInfo):
    """Unsubscribe from push notifications."""
    try:
        success = await push_service.remove_subscription(subscription.endpoint)
        if success:
            return {"status": "unsubscribed"}
        else:
            raise HTTPException(status_code=500, detail="Failed to remove subscription")
    except Exception as e:
        logger.error(f"Error unsubscribing from push: {e}")
        raise HTTPException(status_code=500, detail=str(e))

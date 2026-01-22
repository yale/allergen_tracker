"""Service for managing push notifications."""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, List

from dotenv import load_dotenv
from pywebpush import webpush, WebPushException

load_dotenv()

logger = logging.getLogger(__name__)

SUBSCRIPTIONS_FILE = Path(__file__).parent.parent / "cache" / "push_subscriptions.json"


class PushService:
    """Service for managing push notification subscriptions."""

    def __init__(self):
        self.vapid_private_key = os.getenv("VAPID_PRIVATE_KEY")
        self.vapid_public_key = os.getenv("VAPID_PUBLIC_KEY")
        self.vapid_claims = {
            "sub": os.getenv("VAPID_SUBJECT", "mailto:admin@allergentracker.local")
        }

    def get_public_key(self) -> str | None:
        """Get the VAPID public key."""
        return self.vapid_public_key

    async def add_subscription(self, subscription: Dict[str, Any]) -> bool:
        """Add a push subscription."""
        try:
            subscriptions = self._load_subscriptions()

            # Check if subscription already exists
            endpoint = subscription.get("endpoint")
            if any(sub.get("endpoint") == endpoint for sub in subscriptions):
                logger.info(f"Subscription already exists: {endpoint}")
                return True

            subscriptions.append(subscription)
            self._save_subscriptions(subscriptions)
            logger.info(f"Added subscription: {endpoint}")
            return True
        except Exception as e:
            logger.error(f"Error adding subscription: {e}")
            return False

    async def remove_subscription(self, endpoint: str) -> bool:
        """Remove a push subscription."""
        try:
            subscriptions = self._load_subscriptions()
            original_count = len(subscriptions)
            subscriptions = [sub for sub in subscriptions if sub.get("endpoint") != endpoint]

            if len(subscriptions) < original_count:
                self._save_subscriptions(subscriptions)
                logger.info(f"Removed subscription: {endpoint}")
                return True
            else:
                logger.warning(f"Subscription not found: {endpoint}")
                return False
        except Exception as e:
            logger.error(f"Error removing subscription: {e}")
            return False

    async def send_notification(self, title: str, body: str, data: Dict[str, Any] = None) -> int:
        """Send push notification to all subscribed clients."""
        if not self.vapid_private_key or not self.vapid_public_key:
            logger.warning("VAPID keys not configured, skipping push notification")
            return 0

        subscriptions = self._load_subscriptions()
        success_count = 0
        failed_subscriptions = []

        notification_data = {
            "title": title,
            "body": body,
            "data": data or {}
        }

        for subscription in subscriptions:
            try:
                webpush(
                    subscription_info=subscription,
                    data=json.dumps(notification_data),
                    vapid_private_key=self.vapid_private_key,
                    vapid_claims=self.vapid_claims
                )
                success_count += 1
                logger.info(f"Sent notification to {subscription.get('endpoint')}")
            except WebPushException as e:
                logger.error(f"Failed to send notification: {e}")
                # If subscription is expired or invalid, mark for removal
                if e.response and e.response.status_code in [404, 410]:
                    failed_subscriptions.append(subscription.get('endpoint'))
            except Exception as e:
                logger.error(f"Unexpected error sending notification: {e}")

        # Clean up failed subscriptions
        if failed_subscriptions:
            self._remove_failed_subscriptions(failed_subscriptions)

        logger.info(f"Sent {success_count}/{len(subscriptions)} notifications successfully")
        return success_count

    def _load_subscriptions(self) -> List[Dict[str, Any]]:
        """Load subscriptions from file."""
        if not SUBSCRIPTIONS_FILE.exists():
            return []

        try:
            with open(SUBSCRIPTIONS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading subscriptions: {e}")
            return []

    def _save_subscriptions(self, subscriptions: List[Dict[str, Any]]) -> None:
        """Save subscriptions to file."""
        try:
            SUBSCRIPTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(SUBSCRIPTIONS_FILE, 'w') as f:
                json.dump(subscriptions, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving subscriptions: {e}")

    def _remove_failed_subscriptions(self, endpoints: List[str]) -> None:
        """Remove failed subscriptions."""
        subscriptions = self._load_subscriptions()
        subscriptions = [sub for sub in subscriptions if sub.get("endpoint") not in endpoints]
        self._save_subscriptions(subscriptions)
        logger.info(f"Removed {len(endpoints)} failed subscriptions")

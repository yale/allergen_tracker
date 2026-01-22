"""Real-time Firebase listener with in-memory cache for allergen data."""

import logging
import os
import threading
from datetime import datetime, timezone

from dotenv import load_dotenv
from huckleberry_api import HuckleberryAPI

from cache.file_cache import read_cache, write_cache, CACHE_FILE
from services.allergen_service import process_solid_food_data, calculate_allergen_exposure
from services.huckleberry import fetch_all_feed_intervals, extract_solid_food_entries

logger = logging.getLogger(__name__)


class AllergenCache:
    """Singleton class managing in-memory allergen cache with Firebase real-time updates."""

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self._allergens: list[dict] = []
        self._last_updated: datetime | None = None
        self._api: HuckleberryAPI | None = None
        self._child_uid: str | None = None
        self._listener_active = False

    @classmethod
    def get_instance(cls) -> "AllergenCache":
        """Get or create the singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def _load_from_file_cache(self) -> bool:
        """Load existing data from file cache for warm boot. Returns True if loaded."""
        try:
            if CACHE_FILE.exists():
                import json
                with open(CACHE_FILE, 'r') as f:
                    data = json.load(f)
                self._allergens = data.get('allergens', [])
                self._last_updated = datetime.fromisoformat(data['last_updated'])
                logger.info("Loaded %d allergens from file cache", len(self._allergens))
                return True
        except Exception as e:
            logger.warning("Could not load file cache: %s", e)
        return False

    def _fetch_and_update(self) -> None:
        """Fetch fresh data from Firestore and update caches."""
        try:
            if not self._api or not self._child_uid:
                logger.warning("Cannot fetch: API or child_uid not initialized")
                return

            # Fetch all feed intervals
            client = self._api._get_firestore_client()
            all_entries = fetch_all_feed_intervals(client, self._child_uid)
            solid_entries = extract_solid_food_entries(all_entries)

            if not solid_entries:
                logger.warning("No solid food entries found")
                return

            # Process and calculate allergen exposure
            df = process_solid_food_data(solid_entries)
            allergens = calculate_allergen_exposure(df)

            # Update in-memory cache
            self._allergens = allergens
            self._last_updated = datetime.now(timezone.utc)

            # Persist to file cache
            write_cache(allergens, self._last_updated)

            # Broadcast update to WebSocket clients
            from websocket.connection_manager import ConnectionManager
            manager = ConnectionManager.get_instance()
            manager.broadcast_sync({
                "type": "update",
                "allergens": allergens,
                "last_updated": self._last_updated.isoformat()
            })

            # Send push notification
            import asyncio
            from services.push_service import PushService
            push_service = PushService()
            try:
                # Run async push notification in a new event loop (we're in a callback thread)
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(
                    push_service.send_notification(
                        title="New Feed Logged",
                        body="A new feeding has been logged in Huckleberry",
                        data={"type": "feed_update"}
                    )
                )
                loop.close()
            except Exception as e:
                logger.error(f"Error sending push notification: {e}")

            logger.info("Updated allergen cache with %d allergens from %d solid food entries",
                       len(allergens), len(solid_entries))

        except Exception as e:
            logger.error("Error fetching and updating allergens: %s", e)

    def _on_feed_update(self, data: dict) -> None:
        """Callback for Firebase feed updates."""
        logger.info("Received feed update from Firebase, fetching fresh data")
        self._fetch_and_update()

    def start_listener(self) -> None:
        """Start the Firebase real-time listener."""
        if self._listener_active:
            logger.warning("Listener already active")
            return

        # Load from file cache first for immediate availability
        self._load_from_file_cache()

        # Authenticate with Huckleberry
        load_dotenv()
        self._api = HuckleberryAPI(
            email=os.getenv("HUCKLEBERRY_EMAIL"),
            password=os.getenv("HUCKLEBERRY_PASSWORD")
        )
        self._api.authenticate()
        logger.info("Authenticated with Huckleberry API")

        # Get child UID
        children = self._api.get_children()
        if not children:
            logger.error("No children found in Huckleberry account")
            return
        self._child_uid = children[0]["uid"]

        # Setup real-time listener
        self._api.setup_feed_listener(self._child_uid, self._on_feed_update)
        self._listener_active = True
        logger.info("Firebase listener started for child %s", self._child_uid)

    def stop_listener(self) -> None:
        """Stop the Firebase real-time listener."""
        if self._api and self._listener_active:
            self._api.stop_all_listeners()
            self._listener_active = False
            logger.info("Firebase listener stopped")

    def get_allergens(self) -> tuple[list[dict], datetime | None]:
        """Get current allergen data from cache."""
        return self._allergens, self._last_updated

    def refresh(self) -> tuple[list[dict], datetime]:
        """Force refresh allergen data from Huckleberry."""
        if not self._api or not self._child_uid:
            raise RuntimeError("Listener not started")

        self._fetch_and_update()

        if not self._last_updated:
            raise RuntimeError("Failed to refresh allergen data")

        return self._allergens, self._last_updated

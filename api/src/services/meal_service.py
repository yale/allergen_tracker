"""Service for submitting meals to Huckleberry Firestore."""

import logging
import time
import uuid
from datetime import datetime, timezone

from services.realtime_listener import AllergenCache

logger = logging.getLogger(__name__)


def submit_meal(components: list[list[str]]) -> dict:
    """
    Submit a meal with the given components to Huckleberry Firestore.

    Each component represents a separate dish and will create a separate Firestore entry.

    Args:
        components: List of components, each component is a list of food names

    Returns:
        dict with status, list of entry details, and timestamp
    """
    cache = AllergenCache.get_instance()

    if not cache._api or not cache._child_uid:
        raise RuntimeError("Huckleberry API not initialized")

    # Get Firestore client
    client = cache._api._get_firestore_client()
    child_uid = cache._child_uid

    # Create timestamp for all entries (same time for consistency)
    now = datetime.now(timezone.utc)
    timestamp_seconds = now.timestamp()

    # Get Firestore reference
    feed_ref = client.collection("feed").document(child_uid)
    intervals_ref = feed_ref.collection("intervals")

    # Create one entry per component
    entries = []
    for component_foods in components:
        # Build the foods dict with UUIDs as keys
        foods_dict = {}
        for food in component_foods:
            food_uuid = str(uuid.uuid4())
            foods_dict[food_uuid] = {"created_name": food}

        # Huckleberry solid food entry structure
        entry_data = {
            "mode": "solids",
            "start": timestamp_seconds,
            "lastUpdated": timestamp_seconds,
            "offset": -300.0,  # EST offset in minutes
            "foods": foods_dict,
        }

        # Create a new document
        new_doc_ref = intervals_ref.document()
        new_doc_ref.set(entry_data)

        logger.info(
            "Created solid food entry %s with %d foods: %s",
            new_doc_ref.id,
            len(component_foods),
            component_foods,
        )

        entries.append(
            {
                "entry_id": new_doc_ref.id,
                "foods": component_foods,
            }
        )

    return {
        "status": "success",
        "entries": entries,
        "timestamp": now.isoformat(),
    }

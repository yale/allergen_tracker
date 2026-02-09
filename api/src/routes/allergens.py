"""Allergen API routes."""

from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException

from models import AllergenResponse, RefreshResponse, FeedLogResponse, FeedEntry
from services.realtime_listener import AllergenCache
from services.huckleberry import fetch_solid_food_entries

router = APIRouter()


@router.get("/allergens", response_model=AllergenResponse)
async def get_allergens():
    """Returns all allergens with days since last exposure."""
    cache = AllergenCache.get_instance()
    allergens, last_updated = cache.get_allergens()

    if not allergens:
        raise HTTPException(
            status_code=503,
            detail="Allergen data not yet available. Please wait for cache to initialize.",
        )

    return AllergenResponse(allergens=allergens, last_updated=last_updated)


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_cache():
    """Manually trigger cache refresh."""
    cache = AllergenCache.get_instance()

    try:
        allergens, last_updated = cache.refresh()
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return RefreshResponse(
        status="success",
        message="Cache refreshed successfully",
        last_updated=last_updated,
    )


@router.get("/feeds", response_model=FeedLogResponse)
async def get_feed_log():
    """Returns all solid food feed entries."""
    try:
        solid_entries = fetch_solid_food_entries()

        # Convert raw entries to response format
        feed_entries = []
        for entry in solid_entries:
            timestamp = datetime.fromtimestamp(entry.get("start", 0), tz=timezone.utc)

            # Extract food names from the foods dict
            foods_dict = entry.get("foods", {})
            food_names = []
            if isinstance(foods_dict, dict):
                for food_data in foods_dict.values():
                    if isinstance(food_data, dict) and "created_name" in food_data:
                        food_names.append(food_data["created_name"])

            feed_entries.append(FeedEntry(timestamp=timestamp, foods=food_names))

        return FeedLogResponse(entries=feed_entries, total_count=len(feed_entries))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch feed log: {str(e)}")

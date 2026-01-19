"""Allergen API routes."""

from datetime import datetime, timezone
from fastapi import APIRouter

from models import AllergenResponse, RefreshResponse
from services.allergen_service import get_allergen_data
from cache.file_cache import read_cache, write_cache, clear_cache

router = APIRouter()


def _get_allergens_with_cache() -> tuple[list[dict], datetime]:
    """Get allergen data, using cache if valid."""
    cached = read_cache()

    if cached:
        return cached['allergens'], datetime.fromisoformat(cached['last_updated'])

    # Cache miss or invalid - fetch fresh data
    allergens = get_allergen_data()
    last_updated = datetime.now(timezone.utc)
    write_cache(allergens, last_updated)

    return allergens, last_updated


@router.get("/allergens", response_model=AllergenResponse)
async def get_allergens():
    """Returns all allergens with days since last exposure."""
    allergens, last_updated = _get_allergens_with_cache()
    return AllergenResponse(allergens=allergens, last_updated=last_updated)


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_cache():
    """Manually trigger cache refresh."""
    clear_cache()
    allergens = get_allergen_data()
    last_updated = datetime.now(timezone.utc)
    write_cache(allergens, last_updated)

    return RefreshResponse(
        status="success",
        message="Cache refreshed successfully",
        last_updated=last_updated
    )

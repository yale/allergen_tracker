"""Allergen API routes."""

from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException

from models import AllergenResponse, RefreshResponse
from services.realtime_listener import AllergenCache

router = APIRouter()


@router.get("/allergens", response_model=AllergenResponse)
async def get_allergens():
    """Returns all allergens with days since last exposure."""
    cache = AllergenCache.get_instance()
    allergens, last_updated = cache.get_allergens()

    if not allergens:
        raise HTTPException(
            status_code=503,
            detail="Allergen data not yet available. Please wait for cache to initialize."
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
        last_updated=last_updated
    )

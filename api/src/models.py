"""Pydantic models for API responses."""

from datetime import datetime
from pydantic import BaseModel


class Allergen(BaseModel):
    name: str
    days_since_exposure: int | None
    last_exposure_date: str | None
    foods: list[str]


class AllergenResponse(BaseModel):
    allergens: list[Allergen]
    last_updated: datetime


class HealthResponse(BaseModel):
    status: str
    message: str


class RefreshResponse(BaseModel):
    status: str
    message: str
    last_updated: datetime


class FeedEntry(BaseModel):
    timestamp: datetime
    foods: list[str]


class FeedLogResponse(BaseModel):
    entries: list[FeedEntry]
    total_count: int

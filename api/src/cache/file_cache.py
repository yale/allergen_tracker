"""JSON file-based caching for allergen data."""

import json
from datetime import datetime, timedelta
from pathlib import Path

CACHE_FILE = Path(__file__).parent.parent.parent / "cache" / "allergens.json"
CACHE_TTL_HOURS = 24


def _ensure_cache_dir():
    """Ensure the cache directory exists."""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)


def is_cache_valid() -> bool:
    """Check if cache exists and is less than 24 hours old."""
    if not CACHE_FILE.exists():
        return False

    try:
        with open(CACHE_FILE, "r") as f:
            data = json.load(f)

        last_updated = datetime.fromisoformat(data.get("last_updated", ""))
        age = datetime.now(last_updated.tzinfo) - last_updated

        return age < timedelta(hours=CACHE_TTL_HOURS)
    except (json.JSONDecodeError, ValueError, KeyError):
        return False


def read_cache() -> dict | None:
    """Read data from cache file. Returns None if cache is invalid."""
    if not is_cache_valid():
        return None

    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return None


def write_cache(allergens: list[dict], last_updated: datetime) -> None:
    """Write allergen data to cache file."""
    _ensure_cache_dir()

    data = {"allergens": allergens, "last_updated": last_updated.isoformat()}

    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def clear_cache() -> None:
    """Delete the cache file if it exists."""
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()

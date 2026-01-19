# Allergen Tracker - Implementation Plan

## Overview

This plan outlines the next steps for the allergen tracker project:
1. Python API layer (FastAPI) to expose allergen data as JSON
2. React frontend to display the data
3. File-based caching with daily refresh

---

## Phase 1: API Layer (FastAPI)

### Structure

```
api/
├── src/
│   ├── main.py              → FastAPI app entry point
│   ├── routes/
│   │   └── allergens.py     → Allergen endpoints
│   ├── services/
│   │   ├── allergen_service.py   → Business logic (refactored from current main.py)
│   │   └── huckleberry.py        → Huckleberry fetching (renamed from utils)
│   ├── cache/
│   │   └── file_cache.py    → JSON file caching logic
│   └── models.py            → Pydantic models for API responses
├── cache/
│   └── allergens.json       → Cached data (gitignored)
└── pyproject.toml           → Add fastapi, uvicorn
```

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/allergens` | Returns all allergens with days since last exposure |
| POST | `/api/refresh` | Manually trigger cache refresh |
| GET | `/api/health` | Health check |

### Response Format

```json
{
  "allergens": [
    {
      "name": "fish",
      "days_since_exposure": 5,
      "last_exposure_date": "2026-01-14",
      "foods": ["salmon", "sardine", "tuna", "cod", "tilapia", "anchovy"]
    }
  ],
  "last_updated": "2026-01-19T10:30:00Z"
}
```

### Dependencies to Add

- `fastapi`
- `uvicorn`

---

## Phase 2: Frontend (React + Vite)

### Structure

```
frontend/
├── src/
│   ├── App.tsx
│   ├── components/
│   │   └── AllergenCard.tsx
│   └── api/
│       └── allergens.ts     → API client
├── package.json
└── vite.config.ts
```

### Features

- Dashboard showing each allergen with days since last exposure
- Color-coded urgency (e.g., green < 3 days, yellow 3-7 days, red > 7 days)
- Manual refresh button
- Last updated timestamp

---

## Phase 3: Caching

### Strategy

- **Cache location:** `api/cache/allergens.json`
- **Cache TTL:** 24 hours
- **Behavior:**
  - On API request: check file timestamp
  - If cache is < 24h old: serve from cache
  - If cache is stale or missing: fetch from Huckleberry, update cache, return fresh data

### Daily Refresh Options

1. **Cron job:** Call `POST /api/refresh` endpoint daily
2. **CLI command:** `uv run src/main.py --refresh` for use with system cron
3. **Background task:** FastAPI background task that runs on startup and schedules refresh

---

## Implementation Order

1. [ ] Refactor `main.py` business logic into `services/allergen_service.py`
2. [ ] Rename `utils_fetch_solid_food_entries.py` to `services/huckleberry.py`
3. [ ] Create Pydantic models in `models.py`
4. [ ] Implement file cache in `cache/file_cache.py`
5. [ ] Create FastAPI app with routes
6. [ ] Add `fastapi` and `uvicorn` to dependencies
7. [ ] Test API endpoints
8. [ ] Initialize React + Vite frontend
9. [ ] Build allergen dashboard component
10. [ ] Connect frontend to API
11. [ ] Add daily cache refresh mechanism

# Allergen Tracker

Track allergen exposure for babies using data from the Huckleberry baby tracking app.

## Overview

This application fetches solid food feeding data from Huckleberry, parses the entries, and calculates how long it has been since your baby was exposed to specific allergens. It tracks the FDA top 9 allergens: dairy, egg, fish, crustacean shellfish, peanut, tree nut, wheat, soy, and sesame.

## Quick Start

### Prerequisites
- Python 3.10+ with [uv](https://github.com/astral-sh/uv)
- Node.js 18+
- Huckleberry account credentials

### 1. Start the API
```bash
cd api
uv sync

# Create .env file with your Huckleberry credentials
echo "HUCKLEBERRY_EMAIL=your-email@example.com" > .env
echo "HUCKLEBERRY_PASSWORD=your-password" >> .env

uv run src/main.py
```
The API runs at http://localhost:8000

### 2. Start the Frontend
```bash
cd frontend
npm install
npm run dev
```
The frontend runs at http://localhost:5173

## API Endpoints

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

## Features

- Dashboard showing each allergen with days since last exposure
- Color-coded urgency indicators:
  - Green: ≤3 days since exposure
  - Yellow: 4-7 days since exposure
  - Red: >7 days since exposure
- Manual refresh button
- 24-hour file-based caching
- Expandable food list per allergen

## Tech Stack

**Backend**
- Python 3.10+
- FastAPI + Uvicorn
- huckleberry-api, pandas

**Frontend**
- React 19 + TypeScript
- Vite
- Tailwind CSS v4

## Project Structure

```
├── api/
│   ├── src/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── models.py            # Pydantic models
│   │   ├── routes/
│   │   │   └── allergens.py     # API endpoints
│   │   ├── services/
│   │   │   ├── allergen_service.py
│   │   │   └── huckleberry.py
│   │   └── cache/
│   │       └── file_cache.py
│   └── cache/                   # Cached data (gitignored)
└── frontend/
    └── src/
        ├── App.tsx
        ├── components/
        │   ├── AllergenCard.tsx
        │   ├── AllergenList.tsx
        │   └── Header.tsx
        ├── api/
        │   └── allergens.ts
        └── types/
            └── allergen.ts
```

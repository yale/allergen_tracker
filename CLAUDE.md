# Allergen Tracker

A monorepo for tracking allergen exposure for babies using the Huckleberry API.

## Project Overview

This application fetches solid food feeding data from the Huckleberry baby tracking app, parses the entries, and calculates how long it has been since the baby was exposed to specific allergens (dairy, egg, fish, shellfish, peanut, tree nuts, wheat, soy, sesame).

## Repository Structure

```
/api        - FastAPI backend
/frontend   - React + Vite frontend
```

## API (`/api`)

### Tech Stack
- Python 3.10+
- FastAPI + Uvicorn
- Package manager: uv
- Key dependencies: huckleberry-api, pandas, python-dotenv, fastapi, uvicorn

### Setup
```bash
cd api
uv sync
# Create .env with HUCKLEBERRY_EMAIL and HUCKLEBERRY_PASSWORD
```

### Running
```bash
cd api
uv run src/main.py  # Runs on http://localhost:8000
```

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/allergens` | Returns all allergens with days since last exposure |
| POST | `/api/refresh` | Manually trigger cache refresh |
| GET | `/api/health` | Health check |

### Project Structure
```
api/src/
├── main.py              # FastAPI app entry point
├── models.py            # Pydantic response models
├── routes/
│   └── allergens.py     # Allergen endpoints
├── services/
│   ├── allergen_service.py  # Business logic
│   └── huckleberry.py       # Huckleberry API fetching
└── cache/
    └── file_cache.py    # JSON file caching (24h TTL)
```

### Caching
- Cache location: `api/cache/allergens.json`
- Cache TTL: 24 hours
- Use `POST /api/refresh` to force refresh

## Frontend (`/frontend`)

### Tech Stack
- React 19 + TypeScript
- Vite
- Tailwind CSS v4

### Setup
```bash
cd frontend
npm install
```

### Running
```bash
cd frontend
npm run dev  # Runs on http://localhost:5173
```

### Features
- Dashboard showing each allergen with days since last exposure
- Color-coded urgency (green ≤3 days, yellow 4-7 days, red >7 days)
- Manual refresh button
- Last updated timestamp
- Expandable food list per allergen

## Environment Variables

Required in `api/.env`:
- `HUCKLEBERRY_EMAIL` - Huckleberry account email
- `HUCKLEBERRY_PASSWORD` - Huckleberry account password

## Allergen Categories

The app tracks these FDA top 9 allergens:
- dairy, egg, fish, crustacean shellfish, peanut, tree nut, wheat, soy, sesame

Each allergen maps to specific foods (e.g., dairy → cheese, yogurt, butter, etc.)

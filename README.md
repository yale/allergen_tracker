# Allergen Tracker

Track allergen exposure for babies using data from the Huckleberry baby tracking app.

## Overview

This application fetches solid food feeding data from Huckleberry, parses the entries, and calculates how long it has been since your baby was exposed to specific allergens. It tracks the FDA top 9 allergens: dairy, egg, fish, crustacean shellfish, peanut, tree nut, wheat, soy, and sesame.

## Quick Start

### Prerequisites
- Python 3.10+ with [uv](https://github.com/astral-sh/uv)
- Node.js 18+
- Huckleberry account credentials
- Anthropic API key (for AI-powered meal logging)

### Setup

```bash
# Install dependencies for both API and frontend
make install

# Create .env file with your Huckleberry credentials and Anthropic API key
cd api
echo "HUCKLEBERRY_EMAIL=your-email@example.com" > .env
echo "HUCKLEBERRY_PASSWORD=your-password" >> .env
echo "ANTHROPIC_API_KEY=your-anthropic-key" >> .env
cd ..
```

### Running

```bash
# Run both API and frontend in parallel
make dev

# Or run individually:
make api       # API runs at http://localhost:8000
make frontend  # Frontend runs at http://localhost:5173
```

<details>
<summary>Manual setup (without Make)</summary>

#### 1. Start the API
```bash
cd api
uv sync
uv run src/main.py
```
The API runs at http://localhost:8000

#### 2. Start the Frontend
```bash
cd frontend
npm install
npm run dev
```
The frontend runs at http://localhost:5173

</details>

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/allergens` | Returns all allergens with days since last exposure |
| POST | `/api/refresh` | Manually trigger cache refresh |
| GET | `/api/health` | Health check |
| POST | `/api/meals/analyze` | Analyze meal photo with AI, returns foods grouped by component |
| POST | `/api/meals/submit` | Submit meal components to Huckleberry (creates one entry per component) |
| GET | `/api/meals/suggestions` | Get known foods for autocomplete |

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
- AI-powered meal logging:
  - Take photos of meals to automatically identify foods
  - Foods are grouped by component (separate dishes/sides)
  - Each component creates a separate Huckleberry entry
  - Multiselect combobox UI for easy editing
  - Autocomplete suggestions for known allergen foods

## Roadmap

See [IDEAS.md](./IDEAS.md) for planned features and improvements.

## Tech Stack

**Backend**
- Python 3.10+
- FastAPI + Uvicorn
- huckleberry-api, pandas
- Anthropic API (Claude Vision for meal photo analysis)

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
│   │   │   ├── allergens.py     # Allergen tracking endpoints
│   │   │   └── meals.py         # Meal logging endpoints
│   │   ├── services/
│   │   │   ├── allergen_service.py  # Allergen tracking logic
│   │   │   ├── ai_service.py        # Claude Vision API integration
│   │   │   ├── meal_service.py      # Meal submission to Huckleberry
│   │   │   └── huckleberry.py       # Huckleberry API client
│   │   └── cache/
│   │       └── file_cache.py
│   └── cache/                   # Cached data (gitignored)
└── frontend/
    └── src/
        ├── App.tsx
        ├── components/
        │   ├── AllergenCard.tsx
        │   ├── AllergenList.tsx
        │   ├── Header.tsx
        │   ├── MealLogger.tsx   # Meal logging modal
        │   ├── PhotoCapture.tsx # Camera/photo upload
        │   └── FoodReview.tsx   # Component-based food editor
        ├── api/
        │   ├── allergens.ts
        │   └── meals.ts         # Meal logging API client
        └── types/
            ├── allergen.ts
            └── meal.ts          # Meal/component types
```

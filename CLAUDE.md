# Allergen Tracker

A monorepo for tracking allergen exposure for babies using the Huckleberry API.

## Project Overview

This application fetches solid food feeding data from the Huckleberry baby tracking app, parses the entries, and calculates how long it has been since the baby was exposed to specific allergens (dairy, egg, fish, shellfish, peanut, tree nuts, wheat, soy, sesame).

## Repository Structure

```
/api        - FastAPI backend
/frontend   - React + Vite frontend
IDEAS.md    - Feature ideas and roadmap
Makefile    - Development automation
```

## Quick Development Commands

```bash
make install   # Install dependencies for both API and frontend
make dev       # Run API and frontend in parallel
make api       # Run API only
make frontend  # Run frontend only
```

## API (`/api`)

### Tech Stack
- Python 3.10+
- FastAPI + Uvicorn
- Package manager: uv
- Key dependencies: huckleberry-api, pandas, python-dotenv, fastapi, uvicorn, anthropic

### Setup
```bash
# From project root:
make install  # Installs both API and frontend dependencies

# Or manually:
cd api
uv sync
# Create .env with HUCKLEBERRY_EMAIL, HUCKLEBERRY_PASSWORD, and ANTHROPIC_API_KEY
```

### Running
```bash
# From project root:
make api  # Runs on http://localhost:8000

# Or manually:
cd api
uv run src/main.py
```

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/allergens` | Returns all allergens with days since last exposure |
| POST | `/api/refresh` | Manually trigger cache refresh |
| GET | `/api/health` | Health check |
| POST | `/api/meals/analyze` | Analyze meal photo with AI, returns identified foods grouped by component |
| POST | `/api/meals/submit` | Submit confirmed meal components to Huckleberry (creates one entry per component) |
| GET | `/api/meals/suggestions` | Get known foods for autocomplete |
| GET | `/api/push/vapid-public-key` | Get VAPID public key for push notifications |
| POST | `/api/push/subscribe` | Subscribe to push notifications |
| POST | `/api/push/unsubscribe` | Unsubscribe from push notifications |

### Project Structure
```
api/src/
├── main.py              # FastAPI app entry point
├── models.py            # Pydantic response models
├── routes/
│   ├── allergens.py     # Allergen endpoints
│   └── meals.py         # Meal logging endpoints
├── services/
│   ├── allergen_service.py  # Business logic & ALLERGEN_FOOD_MAP
│   ├── ai_service.py        # Claude Vision API integration
│   ├── meal_service.py      # Firestore write logic
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
# From project root:
make install  # Installs both API and frontend dependencies

# Or manually:
cd frontend
npm install
```

### Running
```bash
# From project root:
make frontend  # Runs on http://localhost:5173

# Or manually:
cd frontend
npm run dev
```

### Features
- Dashboard showing each allergen with days since last exposure
- Color-coded urgency (green ≤3 days, yellow 4-7 days, red >7 days)
- Manual refresh button
- Last updated timestamp
- Expandable food list per allergen
- AI-powered meal logging with component-based grouping:
  - Photograph meals to auto-identify foods grouped by dish/side
  - Each component creates a separate Huckleberry entry
  - Example: broccoli side, rice side, yogurt+shrimp → 3 separate entries
  - Multiselect combobox UI for easy food management
- **PWA Support**: Install as a Progressive Web App on mobile devices
- **Push Notifications**: Get notified when a new feed is logged

## Environment Variables

Required in `api/.env`:
- `HUCKLEBERRY_EMAIL` - Huckleberry account email
- `HUCKLEBERRY_PASSWORD` - Huckleberry account password
- `ANTHROPIC_API_KEY` - Anthropic API key for Claude Vision (meal photo analysis)

Optional (for push notifications):
- `VAPID_PRIVATE_KEY` - VAPID private key for push notifications
- `VAPID_PUBLIC_KEY` - VAPID public key for push notifications
- `VAPID_SUBJECT` - VAPID subject (mailto: or https: URL, default: `mailto:admin@allergentracker.local`)

To generate VAPID keys for push notifications, you can use the `pywebpush` library:
```bash
cd api
uv run python -c "from pywebpush import generate_vapid_keys; keys = generate_vapid_keys(); print(f'VAPID_PRIVATE_KEY={keys[\"private_key\"]}\nVAPID_PUBLIC_KEY={keys[\"public_key\"]}')"
```

Add the generated keys to your `api/.env` file.

## Allergen Categories

The app tracks these FDA top 9 allergens:
- dairy, egg, fish, crustacean shellfish, peanut, tree nut, wheat, soy, sesame

Each allergen maps to specific foods (e.g., dairy → cheese, yogurt, butter, etc.)

## Development Notes

- See `IDEAS.md` for planned features and roadmap
- After completing significant tasks, consider whether `CLAUDE.md` or `README.md` need updates

## Known Tech Debt

### High Priority
- **Hardcoded timezone**: `meal_service.py` has EST offset hardcoded (`-300.0`), should detect user timezone
- **No tests**: No unit or integration tests for component-based meal logging functionality
- **No validation on component limits**: Users can add unlimited components (should consider a reasonable max)

### Medium Priority
- **Component naming**: Components are only numbered ("Component 1"), users might want descriptive names
- **Magic numbers**: Blur timeout delays (200ms) are hardcoded in FoodReview component
- **Duplicate color mapping**: `allergenColors` object could be centralized in a constants file
- **Error handling**: Failed suggestions load logs to console, should have user-facing error states
- **Empty component handling**: Frontend filters empty components, but validation could be more explicit

### Low Priority
- **Type safety improvements**: `componentInputs` uses `Record<number, string>` which could be more strictly typed
- **No visual feedback**: Adding foods could use animations or toasts for better UX
- **Mobile optimization**: UI may need responsive improvements for smaller screens
- **Z-index management**: Uses inline z-index values instead of a design system approach
- **Return type hints**: Some Python functions (e.g., `submit_meal`) could specify return type more precisely

# Allergen Tracker

A tool to track allergen exposure for babies using the Huckleberry API.

## Status

Work in progress. Currently fetches and displays solid food entries from Huckleberry with timestamps, foods eaten, notes, and reactions.

## Setup

1. Install dependencies using uv:
```bash
uv sync
```

2. Copy `.env.example` to `.env` and add your Huckleberry credentials:
```bash
cp .env.example .env
```

3. Edit `.env` with your Huckleberry account credentials:
```
HUCKLEBERRY_EMAIL=your_email@example.com
HUCKLEBERRY_PASSWORD=your_password_here
```

## Usage

Run the script to fetch and display all solid food entries:

```bash
uv run src/allergen_tracker/main.py
```

This will display:
- All solid food entries sorted by date
- Foods eaten at each meal
- Any notes or reactions recorded
- Summary breakdown by feeding mode

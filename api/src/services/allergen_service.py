"""Business logic for allergen tracking."""

import pandas as pd
from datetime import date

from services.huckleberry import fetch_solid_food_entries


ALLERGEN_FOOD_MAP = {
    'dairy': ['cheese', 'sour cream', 'butter', 'yogurt', 'yoghurt', 'greek yogurt', 'greek yoghurt',
              'mozzarella', 'cheddar cheese', 'cream cheese', 'cottage cheese', 'ricotta cheese'],
    'egg': ['egg', 'omlette', 'scrambled egg', 'egg white', 'egg yolk', 'challah'],
    'fish': ['salmon', 'sardine', 'tuna', 'cod', 'tilapia', 'anchovy'],
    'crustacean shellfish': ['shrimp', 'prawn', 'lobster', 'crab', 'crayfish', 'crawfish'],
    'peanut': ['peanut', 'peanut butter', 'bamba'],
    'tree nut': ['almond', 'almond flour', 'almond milk', 'almond butter',
                 'cashew', 'walnut', 'pecan', 'pistachio', 'brazil nut', 'hazelnut', 'macadamia', 'pine nut'],
    'wheat': ['pizza', 'wheat', 'toast', 'bread', 'pasta', 'noodles', 'couscous', 'matzah', 'challah'],
    'soy': ['soybean oil', 'soy milk', 'soybean', 'edamame', 'tofu'],
    'sesame': ['sesame', 'sesame oil', 'tahini', 'hummus']
}


def process_solid_food_data(solid_food_data_raw: list[dict]) -> pd.DataFrame:
    """Clean and process raw solid food data into a DataFrame."""
    df = pd.DataFrame(solid_food_data_raw)

    # Convert timestamps
    df['start'] = pd.to_datetime(df['start'], unit='s')
    df['start'] = df['start'].dt.tz_localize('UTC').dt.tz_convert('US/Eastern')

    # Flatten the food entries
    df['foods_list'] = df['foods'].apply(
        lambda x: list(x.values()) if isinstance(x, dict) else []
    )
    df_exploded = df.explode('foods_list')
    df_final = pd.json_normalize(df_exploded['foods_list'].dropna())
    df_exploded = df_exploded.reset_index(drop=True)
    df = pd.concat([df_exploded.drop(['foods', 'foods_list'], axis=1), df_final], axis=1)
    df['created_name'] = df['created_name'].str.lower()

    # Select and rename only relevant columns
    df = df[['start', 'created_name']]
    df.rename(columns={'start': 'datetime', 'created_name': 'food'}, inplace=True)

    return df


def calculate_allergen_exposure(df: pd.DataFrame) -> list[dict]:
    """
    Calculate days since last exposure for each allergen.

    Returns:
        List of allergen data dicts sorted by days_since_exposure (descending)
    """
    today = date.today()
    allergen_data = []

    for allergen, foods in ALLERGEN_FOOD_MAP.items():
        # Find entries matching this allergen's foods
        mask = df['food'].isin(foods)
        matching_entries = df[mask]

        if matching_entries.empty:
            last_exposure_date = None
            days_since = None
        else:
            last_exposure_date = matching_entries['datetime'].max().date()
            days_since = (today - last_exposure_date).days

        allergen_data.append({
            'name': allergen,
            'days_since_exposure': days_since,
            'last_exposure_date': last_exposure_date.isoformat() if last_exposure_date else None,
            'foods': foods
        })

    # Sort by days_since_exposure descending (most urgent first), None values at end
    allergen_data.sort(key=lambda x: (x['days_since_exposure'] is None, x['days_since_exposure'] or 0), reverse=True)

    return allergen_data


def get_allergen_data() -> list[dict]:
    """Fetch and process allergen exposure data."""
    solid_food_data = fetch_solid_food_entries()
    df = process_solid_food_data(solid_food_data)
    return calculate_allergen_exposure(df)

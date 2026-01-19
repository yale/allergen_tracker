"""Business logic for allergen tracking."""

import pandas as pd
from datetime import date

from services.huckleberry import fetch_solid_food_entries


# Keywords used for partial/fuzzy matching against food entries
# Matching is case-insensitive and tolerant of misspellings via substring matching
ALLERGEN_KEYWORDS = {
    'dairy': [
        # Milk products
        'milk', 'cream', 'butter', 'ghee',
        # Yogurt (including misspellings)
        'yogurt', 'yoghurt', 'yogart', 'yougurt', 'yohgurt',
        # Cheese varieties
        'cheese', 'cheez', 'mozzarella', 'mozarella', 'mozzarela', 'cheddar', 'chedar',
        'parmesan', 'parmasan', 'parmasean', 'parm', 'brie', 'gouda', 'feta', 'ricotta',
        'ricota', 'cottage', 'cotage', 'swiss', 'provolone', 'colby', 'jack', 'goat cheese',
        'paneer', 'queso', 'mascarpone',
        # Other dairy
        'custard', 'pudding', 'ice cream', 'icecream', 'gelato', 'whey', 'casein',
        'kefir', 'lassi', 'ranch', 'alfredo',
    ],
    'egg': [
        'egg', 'eggs', 'eggg', 'egs',
        # Preparations
        'omelette', 'omelet', 'omlette', 'omlet', 'scramble', 'frittata', 'quiche',
        'souffle', 'soufle', 'meringue', 'merang', 'custard',
        # Baked goods with egg as key ingredient
        'challah', 'chalah', 'challa', 'brioche', 'french toast',
        # Egg components
        'yolk', 'albumin',
        # Mayo-based
        'mayo', 'mayonnaise', 'mayonaise', 'aioli',
    ],
    'fish': [
        'fish', 'salmon', 'salman', 'samon', 'tuna', 'tunna', 'cod', 'tilapia', 'tillapia',
        'sardine', 'sardines', 'anchovy', 'anchovies', 'anchove', 'herring', 'mackerel',
        'mackeral', 'trout', 'bass', 'halibut', 'haddock', 'sole', 'flounder', 'snapper',
        'grouper', 'catfish', 'perch', 'pike', 'pollock', 'whiting', 'swordfish', 'mahi',
        'wahoo', 'branzino', 'sea bass', 'seabass', 'arctic char',
    ],
    'crustacean shellfish': [
        'shrimp', 'shripm', 'shrinp', 'prawn', 'prawns', 'lobster', 'lobstar', 'crab',
        'crabs', 'crayfish', 'crawfish', 'crawdad', 'langoustine', 'scampi', 'krill',
    ],
    'peanut': [
        'peanut', 'peanuts', 'penut', 'penuts', 'peanit', 'groundnut',
        'bamba', 'bamaba', 'bambas',
        # Note: "pb" commonly used for peanut butter
        'pb&j', 'pb and j', 'pbj',
    ],
    'tree nut': [
        'almond', 'almonds', 'amond', 'almand', 'cashew', 'cashews', 'cashue', 'cashu',
        'walnut', 'walnuts', 'wallnut', 'pecan', 'pecans', 'pican', 'pistachio',
        'pistachios', 'pistacho', 'hazelnut', 'hazelnuts', 'hazelnut', 'filbert',
        'macadamia', 'macademia', 'brazil nut', 'brazilnut', 'pine nut', 'pinenut',
        'chestnut', 'chesnut', 'praline', 'marzipan', 'nutella',
        # Nut milks/butters
        'almond milk', 'cashew milk', 'almond butter', 'cashew butter',
    ],
    'wheat': [
        'wheat', 'wheatgerm', 'bread', 'breads', 'bred', 'toast', 'toasted',
        'pasta', 'pastas', 'noodle', 'noodles', 'spaghetti', 'spagetti', 'spagheti',
        'macaroni', 'maccaroni', 'penne', 'fusilli', 'rigatoni', 'linguine', 'fettuccine',
        'lasagna', 'lasagne', 'ravioli', 'tortellini', 'gnocchi',
        'couscous', 'cous cous', 'couscouse', 'bulgur', 'bulgar', 'farro', 'semolina',
        # Baked goods
        'matzah', 'matza', 'matzoh', 'matzo', 'challah', 'chalah', 'bagel', 'bagle',
        'croissant', 'croissan', 'muffin', 'biscuit', 'biscit', 'cracker', 'pretzel',
        'pretsel', 'pancake', 'pancakes', 'waffle', 'waffles', 'wafel', 'pita', 'pitta',
        'tortilla', 'tortila', 'wrap', 'flour tortilla', 'naan', 'nan', 'roti', 'chapati',
        # Cereals and grains
        'cereal', 'cheerios', 'oatmeal', 'farina', 'cream of wheat',
        # Breaded items
        'breaded', 'breadcrumb', 'panko', 'crusted',
        # Other wheat products
        'seitan', 'flour', 'gluten',
    ],
    'soy': [
        'soy', 'soya', 'soybean', 'soybeans', 'edamame', 'edamamme', 'edemame',
        'tofu', 'toffu', 'tempeh', 'tempe', 'miso', 'natto',
        'soy sauce', 'soysauce', 'tamari', 'teriyaki',
        'soy milk', 'soymilk',
    ],
    'sesame': [
        'sesame', 'seseme', 'seasame', 'sesamee',
        'tahini', 'tahina', 'tehini', 'tehina',
        'hummus', 'humus', 'hummous', 'houmous', 'houmus',
        'halvah', 'halva', 'halawa',
        'baba ganoush', 'baba ghanoush', 'babaganoush',
    ],
}


def food_matches_allergen(food: str, keywords: list[str]) -> bool:
    """
    Check if a food entry matches any allergen keyword using fuzzy matching.

    Uses substring matching in both directions:
    - Checks if any keyword is contained in the food entry
    - Checks if the food entry is contained in any keyword

    This handles misspellings, plurals, and food descriptions like "scrambled eggs with cheese".
    """
    food_lower = food.lower().strip()

    for keyword in keywords:
        keyword_lower = keyword.lower()
        # Check if keyword is in food entry (e.g., "egg" in "scrambled eggs")
        if keyword_lower in food_lower:
            return True
        # Check if food entry is in keyword (e.g., "eggs" matching "scrambled eggs")
        if food_lower in keyword_lower:
            return True

    return False


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

    for allergen, keywords in ALLERGEN_KEYWORDS.items():
        # Find entries matching this allergen using fuzzy matching
        mask = df['food'].apply(lambda food: food_matches_allergen(food, keywords))
        matching_entries = df[mask]

        # Get unique foods that matched for display
        matched_foods = matching_entries['food'].unique().tolist() if not matching_entries.empty else []

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
            'foods': matched_foods,  # Show actual matched foods instead of keyword list
        })

    # Sort by days_since_exposure descending (most urgent first), None values at end
    allergen_data.sort(key=lambda x: (x['days_since_exposure'] is None, x['days_since_exposure'] or 0), reverse=True)

    return allergen_data


def get_allergen_data() -> list[dict]:
    """Fetch and process allergen exposure data."""
    solid_food_data = fetch_solid_food_entries()
    df = process_solid_food_data(solid_food_data)
    return calculate_allergen_exposure(df)

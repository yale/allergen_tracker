# ==================================
#          IMPORTS SECTION
# ==================================

import pandas as pd
from datetime import datetime, date  
from utils_fetch_solid_food_entries import fetch_solid_food_entries

# ==================================
#          DEFINE ALLERGEN FOOD MAP 
# ==================================

allergen_food_map = {
    'dairy': ['cheese', 'sour cream', 'butter', 'yogurt', 'yoghurt', 'greek yogurt', 'greek yoghurt',
    'mozzarella', 'cheddar cheese', 'cream cheese', 'cottage cheese', 'ricotta cheese'],
    'egg': ['egg', 'omlette', 'scrambled egg', 'egg white', 'egg yolk', 'challah'],
    'fish': ['salmon', 'sardine', 'tuna', 'cod', 'tilapia', 'anchovy'],
    'crustacean shellfish': ['shrimp', 'prawn', 'lobster', 'crab', 'crayfish', 'crawfish'],
    'peanut': ['peanut', 'peanut butter', 'bamba'],
    'tree nut': ['almond', 'almond flour', 'almond milk', 'almond butter',    
    'cashew', 'walnut', 'pecan', 'pistachio', 'brazil nut', 'hazelnut', 'macadamia', 'pine nut'],
    'wheat': ['wheat', 'toast', 'bread', 'pasta', 'noodles', 'couscous', 'matzah', 'challah'],
    'soy': ['soybean oil', 'soy milk', 'soybean', 'edamame', 'tofu'],
    'sesame': ['sesame', 'sesame oil', 'tahini', 'hummus']
    }

# ==================================
#          FETCH & CLEAN DATA 
# ==================================

# Fetch solid food data from huckleberry
solid_food_data_raw = fetch_solid_food_entries()

# Clean solid food data 
solid_food_data_clean = pd.DataFrame(solid_food_data_raw) 

#convert  date times
solid_food_data_clean['start'] = pd.to_datetime(solid_food_data_clean['start'], unit='s')
solid_food_data_clean['start'] = solid_food_data_clean['start'].dt.tz_localize('UTC').dt.tz_convert('US/Eastern')

# Flatten the food entries 
solid_food_data_clean['foods_list'] = solid_food_data_clean['foods'].apply(
    lambda x: list(x.values()) if isinstance(x, dict) else []
)
df_exploded = solid_food_data_clean.explode('foods_list')
df_final = pd.json_normalize(df_exploded['foods_list'].dropna())
df_exploded = df_exploded.reset_index(drop=True)
solid_food_data_clean = pd.concat([df_exploded.drop(['foods', 'foods_list'], axis=1), df_final], axis=1)
solid_food_data_clean['created_name'] = solid_food_data_clean['created_name'].str.lower()

# Select and rename only relevant columns
solid_food_data_clean = solid_food_data_clean[['start', 'created_name']]
solid_food_data_clean.rename(columns={'start': 'datetime', 'created_name': 'food'}, inplace=True)

# ==================================
# IDENTIFY DAYS SINCE LAST CONSUMPTION 
# ==================================

allergen_consumption_dates = {}
allergan_df = solid_food_data_clean.copy()

for allergen, foods in allergen_food_map.items():

    # Create binary column for the allergen
    col_name = f'is_{allergen}'
    allergan_df[col_name] = solid_food_data_clean['food'].isin(foods).astype(int)
    # Find the last consumption date for the allergen
    allergen_consumption_dates[allergen] = allergan_df[allergan_df[col_name] == 1]['datetime'].max().date()

# Identify the number of days since each allergen was last consumed
today = date.today() 
days_since_last_consumption = []

for allergen in allergen_food_map.keys():

    delta = today - allergen_consumption_dates[allergen] 
    days_difference = delta.days
    days_since_last_consumption.append((allergen, days_difference))

days_since_last_consumption = sorted(days_since_last_consumption, key=lambda item: item[1], reverse =True)

print(days_since_last_consumption)
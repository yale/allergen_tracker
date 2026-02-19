// Allergen to emoji mapping
export const ALLERGEN_EMOJIS: Record<string, string> = {
  dairy: '🥛',
  egg: '🥚',
  fish: '🐟',
  'crustacean shellfish': '🦐',
  peanut: '🥜',
  'tree nut': '🌰',
  wheat: '🌾',
  soy: '🫘',
  sesame: '🌱',
};

// Allergen food map (synced with backend)
export const ALLERGEN_FOOD_MAP: Record<string, string[]> = {
  dairy: [
    'cheese',
    'sour cream',
    'butter',
    'yogurt',
    'yoghurt',
    'greek yogurt',
    'greek yoghurt',
    'mozzarella',
    'cheddar cheese',
    'cream cheese',
    'cottage cheese',
    'ricotta cheese',
  ],
  egg: ['egg', 'omelette', 'omlette', 'scrambled egg', 'egg white', 'egg yolk', 'challah'],
  fish: ['salmon', 'sardine', 'tuna', 'cod', 'tilapia', 'anchovy'],
  'crustacean shellfish': [
    'shrimp',
    'prawn',
    'lobster',
    'crab',
    'crayfish',
    'crawfish',
    "shrimp gyoza (trader joe's)",
  ],
  peanut: ['peanut', 'peanut butter', 'bamba'],
  'tree nut': [
    'almond',
    'almond flour',
    'almond milk',
    'almond butter',
    'cashew',
    'walnut',
    'pecan',
    'pistachio',
    'brazil nut',
    'hazelnut',
    'macadamia',
    'pine nut',
  ],
  wheat: [
    'pizza',
    'wheat',
    'toast',
    'bread',
    'pasta',
    'noodles',
    'couscous',
    'matzah',
    'challah',
    "shrimp gyoza (trader joe's)",
  ],
  soy: ['soybean oil', 'soy milk', 'soybean', 'edamame', 'tofu', "shrimp gyoza (trader joe's)"],
  sesame: ['sesame', 'sesame oil', 'tahini', 'hummus'],
};

/**
 * Get allergen emojis for a given food name
 * @param foodName - The food name to look up (case insensitive)
 * @returns Array of emoji strings for matching allergens
 */
export function getAllergenEmojis(foodName: string): string[] {
  const foodLower = foodName.toLowerCase();
  const emojis: string[] = [];

  for (const [allergen, foods] of Object.entries(ALLERGEN_FOOD_MAP)) {
    const foodsLower = foods.map((f) => f.toLowerCase());
    if (foodsLower.includes(foodLower)) {
      const emoji = ALLERGEN_EMOJIS[allergen];
      if (emoji) {
        emojis.push(emoji);
      }
    }
  }

  return emojis;
}

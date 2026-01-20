export interface FoodItem {
  name: string;
  allergens: string[];
}

export interface MealComponent {
  foods: FoodItem[];
}

export interface AnalyzeResponse {
  components: MealComponent[];
  notes: string;
}

export interface SubmitRequest {
  components: string[][];  // List of components, each is a list of food names
}

export interface MealEntry {
  entry_id: string;
  foods: string[];
}

export interface SubmitResponse {
  status: string;
  entries: MealEntry[];  // Multiple entries, one per component
  timestamp: string;
}

export interface FoodSuggestion {
  name: string;
  allergens: string[];
}

export interface SuggestionsResponse {
  suggestions: FoodSuggestion[];
}

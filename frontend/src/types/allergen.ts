export interface Allergen {
  name: string;
  days_since_exposure: number | null;
  last_exposure_date: string | null;
  foods: string[];
}

export interface AllergenResponse {
  allergens: Allergen[];
  last_updated: string;
}

export interface RefreshResponse {
  status: string;
  message: string;
  last_updated: string;
}

import type { AllergenResponse, RefreshResponse } from '../types/allergen';

const API_BASE = '/api';

export async function fetchAllergens(): Promise<AllergenResponse> {
  const response = await fetch(`${API_BASE}/allergens`);
  if (!response.ok) {
    throw new Error(`Failed to fetch allergens: ${response.statusText}`);
  }
  return response.json();
}

export async function refreshAllergens(): Promise<RefreshResponse> {
  const response = await fetch(`${API_BASE}/refresh`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`Failed to refresh allergens: ${response.statusText}`);
  }
  return response.json();
}

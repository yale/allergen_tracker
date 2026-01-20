import type { AnalyzeResponse, SubmitResponse, SuggestionsResponse } from '../types/meal';

const API_BASE = '/api';

export async function analyzeMealPhoto(imageFile: File): Promise<AnalyzeResponse> {
  const formData = new FormData();
  formData.append('image', imageFile);

  const response = await fetch(`${API_BASE}/meals/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `Failed to analyze photo: ${response.statusText}`);
  }

  return response.json();
}

export async function submitMeal(components: string[][]): Promise<SubmitResponse> {
  const response = await fetch(`${API_BASE}/meals/submit`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ components }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `Failed to submit meal: ${response.statusText}`);
  }

  return response.json();
}

export async function getFoodSuggestions(): Promise<SuggestionsResponse> {
  const response = await fetch(`${API_BASE}/meals/suggestions`);

  if (!response.ok) {
    throw new Error(`Failed to get suggestions: ${response.statusText}`);
  }

  return response.json();
}

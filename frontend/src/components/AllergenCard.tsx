import { useState } from 'react';
import type { Allergen } from '../types/allergen';

interface AllergenCardProps {
  allergen: Allergen;
}

function getBackgroundColor(days: number | null): string {
  if (days === null) return 'bg-gray-200';
  if (days <= 3) return 'bg-green-200';
  if (days <= 7) return 'bg-yellow-200';
  return 'bg-red-200';
}

function getBorderColor(days: number | null): string {
  if (days === null) return 'border-gray-400';
  if (days <= 3) return 'border-green-400';
  if (days <= 7) return 'border-yellow-400';
  return 'border-red-400';
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return 'Never';
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

export function AllergenCard({ allergen }: AllergenCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const bgColor = getBackgroundColor(allergen.days_since_exposure);
  const borderColor = getBorderColor(allergen.days_since_exposure);

  return (
    <div
      className={`${bgColor} ${borderColor} border-2 rounded-lg p-4 shadow-md transition-all`}
    >
      <div className="flex justify-between items-start">
        <h3 className="text-lg font-semibold capitalize">{allergen.name}</h3>
        <div className="text-right">
          <div className="text-3xl font-bold">
            {allergen.days_since_exposure !== null
              ? allergen.days_since_exposure
              : '—'}
          </div>
          <div className="text-xs text-gray-600">
            {allergen.days_since_exposure !== null ? 'days ago' : 'never'}
          </div>
        </div>
      </div>

      <div className="mt-2 text-sm text-gray-600">
        Last: {formatDate(allergen.last_exposure_date)}
      </div>

      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="mt-2 text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1"
      >
        <span>{isExpanded ? '▼' : '▶'}</span>
        <span>{allergen.foods.length} tracked foods</span>
      </button>

      {isExpanded && (
        <div className="mt-2 text-sm text-gray-600">
          <ul className="list-disc list-inside">
            {allergen.foods.map((food) => (
              <li key={food}>{food}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

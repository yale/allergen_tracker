import type { Allergen } from '../types/allergen';
import { AllergenCard } from './AllergenCard';

interface AllergenListProps {
  allergens: Allergen[];
}

export function AllergenList({ allergens }: AllergenListProps) {
  if (allergens.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        No allergen data available
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
      {allergens.map((allergen) => (
        <AllergenCard key={allergen.name} allergen={allergen} />
      ))}
    </div>
  );
}

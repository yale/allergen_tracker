import { useEffect, useState } from "react";
import type { FoodItem, FoodSuggestion, MealComponent } from "../types/meal";
import { getFoodSuggestions } from "../api/meals";

interface FoodReviewProps {
  components: MealComponent[];
  onComponentsChange: (components: MealComponent[]) => void;
  onSubmit: () => void;
  onCancel: () => void;
  isSubmitting: boolean;
}

export function FoodReview({
  components,
  onComponentsChange,
  onSubmit,
  onCancel,
  isSubmitting,
}: FoodReviewProps) {
  const [componentInputs, setComponentInputs] = useState<
    Record<number, string>
  >({});
  const [focusedComponent, setFocusedComponent] = useState<number | null>(null);
  const [suggestions, setSuggestions] = useState<FoodSuggestion[]>([]);

  useEffect(() => {
    getFoodSuggestions()
      .then((data) => setSuggestions(data.suggestions))
      .catch((err) => console.error("Failed to load suggestions:", err));
  }, []);

  const getFilteredSuggestions = (componentIndex: number, input: string) => {
    if (!input.trim()) return [];
    const componentFoods = components[componentIndex]?.foods || [];
    return suggestions
      .filter(
        (s) =>
          s.name.toLowerCase().includes(input.toLowerCase()) &&
          !componentFoods.some((f) =>
            f.name.toLowerCase() === s.name.toLowerCase()
          ),
      )
      .slice(0, 5);
  };

  const removeFood = (componentIndex: number, foodIndex: number) => {
    const updated = [...components];
    updated[componentIndex] = {
      ...updated[componentIndex],
      foods: updated[componentIndex].foods.filter((_, i) => i !== foodIndex),
    };
    onComponentsChange(updated);
  };

  const addFoodToComponent = (componentIndex: number, food: FoodItem) => {
    const updated = [...components];
    const component = updated[componentIndex];

    if (
      !component.foods.some((f) =>
        f.name.toLowerCase() === food.name.toLowerCase()
      )
    ) {
      updated[componentIndex] = {
        ...component,
        foods: [...component.foods, food],
      };
      onComponentsChange(updated);
    }
    setComponentInputs({ ...componentInputs, [componentIndex]: "" });
  };

  const handleAddCustomFood = (componentIndex: number) => {
    const input = componentInputs[componentIndex]?.trim();
    if (!input) return;

    const suggestion = suggestions.find(
      (s) => s.name.toLowerCase() === input.toLowerCase(),
    );
    if (suggestion) {
      addFoodToComponent(componentIndex, suggestion);
    } else {
      addFoodToComponent(componentIndex, {
        name: input.toLowerCase(),
        allergens: [],
      });
    }
  };

  const handleKeyDown = (componentIndex: number, e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      const filtered = getFilteredSuggestions(
        componentIndex,
        componentInputs[componentIndex] || "",
      );
      if (filtered.length > 0) {
        addFoodToComponent(componentIndex, filtered[0]);
      } else {
        handleAddCustomFood(componentIndex);
      }
    }
  };

  const addNewComponent = () => {
    onComponentsChange([...components, { foods: [] }]);
  };

  const removeComponent = (componentIndex: number) => {
    const updated = components.filter((_, i) => i !== componentIndex);
    onComponentsChange(updated.length > 0 ? updated : [{ foods: [] }]);
  };

  const getTotalFoodCount = () => {
    return components.reduce((sum, c) => sum + c.foods.length, 0);
  };

  const allergenColors: Record<string, string> = {
    dairy: "bg-blue-100 text-blue-800",
    egg: "bg-yellow-100 text-yellow-800",
    fish: "bg-cyan-100 text-cyan-800",
    "crustacean shellfish": "bg-red-100 text-red-800",
    peanut: "bg-amber-100 text-amber-800",
    "tree nut": "bg-orange-100 text-orange-800",
    wheat: "bg-stone-100 text-stone-800",
    soy: "bg-green-100 text-green-800",
    sesame: "bg-lime-100 text-lime-800",
  };

  return (
    <div className="space-y-4">
      <h3 className="font-medium text-gray-700">Meal Components</h3>

      {/* Component list */}
      <div className="space-y-3">
        {components.map((component, componentIndex) => {
          const input = componentInputs[componentIndex] || "";
          const filteredSuggestions = getFilteredSuggestions(
            componentIndex,
            input,
          );
          const showSuggestions = focusedComponent === componentIndex &&
            filteredSuggestions.length > 0;

          return (
            <div
              key={componentIndex}
              className="border border-gray-200 rounded-lg p-3 bg-gray-50"
            >
              {/* Component header */}
              <div className="flex items-center justify-between mb-2">
                {components.length > 1 && (
                  <button
                    onClick={() => removeComponent(componentIndex)}
                    className="text-gray-400 hover:text-red-500 transition-colors"
                    aria-label={`Remove component ${componentIndex + 1}`}
                  >
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  </button>
                )}
              </div>

              {/* Food chips (multiselect display) */}
              {component.foods.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-2">
                  {component.foods.map((food, foodIndex) => (
                    <div
                      key={foodIndex}
                      className="inline-flex items-center gap-1.5 bg-white border border-gray-200 rounded-full px-3 py-1.5"
                    >
                      <span className="text-sm font-medium capitalize">
                        {food.name}
                      </span>
                      {food.allergens.map((allergen) => (
                        <span
                          key={allergen}
                          className={`text-xs px-1.5 py-0.5 rounded-full ${allergenColors[allergen] ||
                            "bg-gray-100 text-gray-800"
                            }`}
                        >
                          {allergen}
                        </span>
                      ))}
                      <button
                        onClick={() => removeFood(componentIndex, foodIndex)}
                        className="ml-0.5 text-gray-400 hover:text-red-500 transition-colors"
                        aria-label={`Remove ${food.name}`}
                      >
                        <svg
                          className="w-3.5 h-3.5"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M6 18L18 6M6 6l12 12"
                          />
                        </svg>
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {/* Add food input */}
              <div className="relative">
                <input
                  type="text"
                  value={input}
                  onChange={(e) =>
                    setComponentInputs({
                      ...componentInputs,
                      [componentIndex]: e.target.value,
                    })}
                  onKeyDown={(e) => handleKeyDown(componentIndex, e)}
                  onFocus={() => setFocusedComponent(componentIndex)}
                  onBlur={() =>
                    setTimeout(() => setFocusedComponent(null), 200)}
                  placeholder="Add foods..."
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                />

                {/* Autocomplete suggestions */}
                {showSuggestions && (
                  <ul className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-40 overflow-auto">
                    {filteredSuggestions.map((suggestion) => (
                      <li key={suggestion.name}>
                        <button
                          onClick={() =>
                            addFoodToComponent(componentIndex, suggestion)}
                          className="w-full px-3 py-2 text-left hover:bg-gray-50 flex items-center gap-2 text-sm"
                        >
                          <span className="capitalize">{suggestion.name}</span>
                          {suggestion.allergens.map((allergen) => (
                            <span
                              key={allergen}
                              className={`text-xs px-1.5 py-0.5 rounded-full ${allergenColors[allergen] ||
                                "bg-gray-100 text-gray-800"
                                }`}
                            >
                              {allergen}
                            </span>
                          ))}
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Add component button */}
      <button
        onClick={addNewComponent}
        className="w-full py-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-gray-400 hover:text-gray-700 transition-colors font-medium text-sm"
      >
        + Add Component
      </button>

      {/* Action buttons */}
      <div className="flex gap-3 pt-4">
        <button
          onClick={onCancel}
          disabled={isSubmitting}
          className="flex-1 py-3 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 transition-colors disabled:bg-gray-50 disabled:cursor-not-allowed"
        >
          Cancel
        </button>
        <button
          onClick={onSubmit}
          disabled={getTotalFoodCount() === 0 || isSubmitting}
          className="flex-1 py-3 bg-green-500 text-white rounded-lg font-medium hover:bg-green-600 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {isSubmitting
            ? (
              <>
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                    fill="none"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                Logging...
              </>
            )
            : (
              `Log ${components.length} Component${components.length !== 1 ? "s" : ""
              } (${getTotalFoodCount()} food${getTotalFoodCount() !== 1 ? "s" : ""
              })`
            )}
        </button>
      </div>
    </div>
  );
}

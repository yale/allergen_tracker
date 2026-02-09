import { useState } from "react";
import type { Allergen } from "../types/allergen";
import { useCurrentTime } from "../hooks/useCurrentTime";
import { formatRelativeTime } from "../utils/timeUtils";

interface AllergenCardProps {
  allergen: Allergen;
}

function getBackgroundColor(days: number | null): string {
  if (days === null) return "bg-gray-200";
  if (days <= 3) return "bg-green-200";
  if (days <= 6) return "bg-yellow-200";
  return "bg-red-200";
}

function getBorderColor(days: number | null): string {
  if (days === null) return "border-gray-400";
  if (days <= 3) return "border-green-400";
  if (days <= 6) return "border-yellow-400";
  return "border-red-400";
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "Never";
  const date = new Date(dateStr);
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

const ALLERGEN_EMOJI: Record<string, string> = {
  dairy: "🥛",
  egg: "🥚",
  fish: "🐟",
  "crustacean shellfish": "🦐",
  peanut: "🥜",
  "tree nut": "🌰",
  wheat: "🌾",
  soy: "🫛",
  sesame: "🫘",
};

export function AllergenCard({ allergen }: AllergenCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const currentTime = useCurrentTime(60000); // Update every minute

  // Format relative time for exposure
  const relativeTime = allergen.last_exposure_date
    ? formatRelativeTime(new Date(allergen.last_exposure_date), currentTime)
    : null;

  const bgColor = getBackgroundColor(allergen.days_since_exposure);
  const borderColor = getBorderColor(allergen.days_since_exposure);

  return (
    <div
      className={`${bgColor} ${borderColor} border-2 rounded-lg p-2.5 shadow-sm transition-all`}
    >
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-base font-semibold capitalize">
            {ALLERGEN_EMOJI[allergen.name] || "🍽️"} {allergen.name}
          </h3>
          <div className="mt-1 text-xs text-gray-600">
            Last: {formatDate(allergen.last_exposure_date)}
          </div>

          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="mt-1 text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1"
          >
            <span>{isExpanded ? "▼" : "▶"}</span>
            <span>{allergen.foods.length} tracked foods</span>
          </button>

          {isExpanded && (
            <div className="mt-1.5 text-xs text-gray-600">
              <ul className="list-disc list-inside">
                {allergen.foods.map((food) => <li key={food}>{food}</li>)}
              </ul>
            </div>
          )}
        </div>
        <div className="text-right">
          <div className="text-sm font-semibold text-gray-700">
            {relativeTime || "never"}
          </div>
        </div>
      </div>
    </div>
  );
}

import { useCurrentTime } from '../hooks/useCurrentTime';
import { formatRelativeTime } from '../utils/timeUtils';

interface HeaderProps {
  lastUpdated: string | null;
  onRefresh: () => void;
  isLoading: boolean;
  isConnected?: boolean;
  onLogMeal?: () => void;
}

export function Header({ lastUpdated, onRefresh, isLoading, isConnected, onLogMeal }: HeaderProps) {
  const currentTime = useCurrentTime(60000); // Update every minute

  const relativeTime = lastUpdated
    ? formatRelativeTime(new Date(lastUpdated), currentTime)
    : 'never';

  return (
    <header className="bg-white shadow-sm mb-3">
      <div className="max-w-6xl mx-auto px-4 py-2">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-xl font-bold text-gray-800 flex items-center gap-2">
              Allergen Tracker
              {isConnected !== undefined && (
                <span
                  className={`inline-block w-2 h-2 rounded-full ${
                    isConnected ? 'bg-red-500 animate-pulse' : 'bg-gray-400'
                  }`}
                  title={isConnected ? 'Live' : 'Disconnected'}
                />
              )}
            </h1>
            <p className="text-xs text-gray-500">
              Last updated: {relativeTime}
            </p>
          </div>
          <div className="flex items-center gap-2">
            {onLogMeal && (
              <button
                onClick={onLogMeal}
                className="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors bg-green-500 text-white hover:bg-green-600 flex items-center gap-1"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Log Meal
              </button>
            )}
            <button
              onClick={onRefresh}
              disabled={isLoading}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                isLoading
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-500 text-white hover:bg-blue-600'
              }`}
            >
              {isLoading ? 'Refreshing...' : 'Refresh'}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

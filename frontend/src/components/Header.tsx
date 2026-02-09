import { useState, useRef, useEffect } from 'react';
import { useCurrentTime } from '../hooks/useCurrentTime';
import { formatRelativeTime } from '../utils/timeUtils';

interface HeaderProps {
  lastUpdated: string | null;
  onRefresh: () => void;
  isLoading: boolean;
  isConnected?: boolean;
  onLogMeal?: () => void;
  onViewFeedLog?: () => void;
}

export function Header({ lastUpdated, onRefresh, isLoading, isConnected, onLogMeal, onViewFeedLog }: HeaderProps) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const currentTime = useCurrentTime(60000); // Update every minute

  const relativeTime = lastUpdated
    ? formatRelativeTime(new Date(lastUpdated), currentTime)
    : 'never';

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    }

    if (isDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isDropdownOpen]);

  const handleAction = (action: () => void) => {
    setIsDropdownOpen(false);
    action();
  };

  return (
    <header className="sticky top-0 bg-white shadow-sm mb-3 z-50">
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
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors bg-blue-500 text-white hover:bg-blue-600 flex items-center gap-1"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
              Menu
            </button>

            {isDropdownOpen && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1">
                {onLogMeal && (
                  <button
                    onClick={() => handleAction(onLogMeal)}
                    className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    Log Meal
                  </button>
                )}
                {onViewFeedLog && (
                  <button
                    onClick={() => handleAction(onViewFeedLog)}
                    className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                    View Feed Log
                  </button>
                )}
                <button
                  onClick={() => handleAction(onRefresh)}
                  disabled={isLoading}
                  className={`w-full px-4 py-2 text-left text-sm flex items-center gap-2 ${
                    isLoading
                      ? 'text-gray-400 cursor-not-allowed'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  {isLoading ? 'Refreshing...' : 'Refresh'}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}

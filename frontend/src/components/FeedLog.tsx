import { useState, useEffect } from 'react';
import { fetchFeedLog } from '../api/allergens';
import type { FeedEntry } from '../types/allergen';
import { getAllergenEmojis } from '../utils/allergenUtils';

interface FeedLogProps {
  isOpen: boolean;
  onClose: () => void;
}

export function FeedLog({ isOpen, onClose }: FeedLogProps) {
  const [entries, setEntries] = useState<FeedEntry[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadFeedLog();
    }
  }, [isOpen]);

  const loadFeedLog = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchFeedLog();
      setEntries(data.entries);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load feed log');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] flex flex-col">
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold">Feed Log</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {isLoading ? (
            <div className="text-center text-gray-500 py-8">Loading...</div>
          ) : error ? (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          ) : entries.length === 0 ? (
            <div className="text-center text-gray-500 py-8">No feed entries found</div>
          ) : (
            <div className="space-y-4">
              {entries.map((entry, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="text-sm text-gray-500 mb-2">
                    {formatDate(entry.timestamp)}
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {entry.foods.map((food, foodIndex) => {
                      const emojis = getAllergenEmojis(food);
                      return (
                        <span
                          key={foodIndex}
                          className="inline-block bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm"
                        >
                          {emojis.length > 0 && (
                            <span className="mr-1">{emojis.join(' ')}</span>
                          )}
                          {food}
                        </span>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="p-4 border-t border-gray-200">
          <button
            onClick={onClose}
            className="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

import { useState, useEffect, useCallback } from 'react';
import { Header } from './components/Header';
import { AllergenList } from './components/AllergenList';
import { MealLogger } from './components/MealLogger';
import { FeedLog } from './components/FeedLog';
import { UpdatePrompt } from './components/UpdatePrompt';
import { fetchAllergens, refreshAllergens } from './api/allergens';
import { useWebSocket } from './hooks/useWebSocket';
import { config } from './config';
import type { Allergen, AllergenResponse } from './types/allergen';

function App() {
  const [allergens, setAllergens] = useState<Allergen[]>([]);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isMealLoggerOpen, setIsMealLoggerOpen] = useState(false);
  const [isFeedLogOpen, setIsFeedLogOpen] = useState(false);

  const handleWebSocketUpdate = useCallback((data: AllergenResponse) => {
    setAllergens(data.allergens);
    setLastUpdated(data.last_updated);
    setIsLoading(false);
  }, []);

  const { isConnected } = useWebSocket({ onUpdate: handleWebSocketUpdate });

  const loadAllergens = async () => {
    try {
      setError(null);
      const data = await fetchAllergens();
      setAllergens(data.allergens);
      setLastUpdated(data.last_updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load allergens');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = async () => {
    setIsLoading(true);
    try {
      setError(null);
      await refreshAllergens();
      const data = await fetchAllergens();
      setAllergens(data.allergens);
      setLastUpdated(data.last_updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to refresh allergens');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadAllergens();
  }, []);

  return (
    <div className="min-h-screen bg-gray-100">
      <Header
        lastUpdated={lastUpdated}
        onRefresh={handleRefresh}
        isLoading={isLoading}
        isConnected={isConnected}
        onLogMeal={config.features.mealLogging ? () => setIsMealLoggerOpen(true) : undefined}
        onViewFeedLog={() => setIsFeedLogOpen(true)}
      />
      <main className="max-w-6xl mx-auto px-4 pb-4">
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        {isLoading && allergens.length === 0 ? (
          <div className="text-center text-gray-500 py-8">Loading...</div>
        ) : (
          <AllergenList allergens={allergens} />
        )}
      </main>
      {config.features.mealLogging && (
        <MealLogger
          isOpen={isMealLoggerOpen}
          onClose={() => setIsMealLoggerOpen(false)}
        />
      )}
      <FeedLog
        isOpen={isFeedLogOpen}
        onClose={() => setIsFeedLogOpen(false)}
      />
      <UpdatePrompt />
    </div>
  );
}

export default App;

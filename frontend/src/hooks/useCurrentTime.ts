import { useState, useEffect } from 'react';

/**
 * Hook that returns the current time and updates it periodically.
 * Triggers a re-render every `intervalMs` milliseconds.
 */
export function useCurrentTime(intervalMs: number = 60000): Date {
  const [currentTime, setCurrentTime] = useState(() => new Date());

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(new Date());
    }, intervalMs);

    return () => clearInterval(interval);
  }, [intervalMs]);

  return currentTime;
}

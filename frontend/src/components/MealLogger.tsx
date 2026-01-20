import { useState } from 'react';
import { PhotoCapture } from './PhotoCapture';
import { FoodReview } from './FoodReview';
import { analyzeMealPhoto, submitMeal } from '../api/meals';
import type { MealComponent } from '../types/meal';

type LoggerState = 'capture' | 'review' | 'success';

interface MealLoggerProps {
  isOpen: boolean;
  onClose: () => void;
}

export function MealLogger({ isOpen, onClose }: MealLoggerProps) {
  const [state, setState] = useState<LoggerState>('capture');
  const [components, setComponents] = useState<MealComponent[]>([{ foods: [] }]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const reset = () => {
    setState('capture');
    setComponents([{ foods: [] }]);
    setError(null);
    setIsAnalyzing(false);
    setIsSubmitting(false);
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  const handlePhotoSelected = async (file: File) => {
    setError(null);
    setIsAnalyzing(true);

    try {
      const result = await analyzeMealPhoto(file);
      setComponents(result.components.length > 0 ? result.components : [{ foods: [] }]);
      setState('review');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze photo');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSubmit = async () => {
    setError(null);
    setIsSubmitting(true);

    try {
      // Filter out empty components and convert to food name arrays
      const nonEmptyComponents = components
        .filter((c) => c.foods.length > 0)
        .map((c) => c.foods.map((f) => f.name));

      if (nonEmptyComponents.length === 0) {
        setError('Please add at least one food to a component');
        setIsSubmitting(false);
        return;
      }

      await submitMeal(nonEmptyComponents);
      setState('success');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to log meal');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    reset();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold text-gray-800">
            {state === 'capture' && 'Log Meal'}
            {state === 'review' && 'Review Foods'}
            {state === 'success' && 'Success!'}
          </h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="Close"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-4">
          {error && (
            <div className="mb-4 p-3 bg-red-100 border border-red-200 text-red-700 rounded-lg text-sm">
              {error}
            </div>
          )}

          {state === 'capture' && (
            <PhotoCapture onPhotoSelected={handlePhotoSelected} isLoading={isAnalyzing} />
          )}

          {state === 'review' && (
            <FoodReview
              components={components}
              onComponentsChange={setComponents}
              onSubmit={handleSubmit}
              onCancel={handleCancel}
              isSubmitting={isSubmitting}
            />
          )}

          {state === 'success' && (
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg
                  className="w-8 h-8 text-green-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-800 mb-2">Meal Logged!</h3>
              <p className="text-gray-600 mb-6">
                Your meal has been recorded and the dashboard will update automatically.
              </p>
              <button
                onClick={handleClose}
                className="px-6 py-2 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 transition-colors"
              >
                Done
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

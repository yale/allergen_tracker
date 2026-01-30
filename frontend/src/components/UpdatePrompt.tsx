import { useEffect, useState } from 'react';
import { useRegisterSW } from 'virtual:pwa-register/react';

export function UpdatePrompt() {
  const [showPrompt, setShowPrompt] = useState(false);

  const {
    offlineReady: [, setOfflineReady],
    needRefresh: [needRefresh, setNeedRefresh],
    updateServiceWorker,
  } = useRegisterSW({
    onRegistered(r) {
      console.log('Service Worker registered:', r);
    },
    onRegisterError(error) {
      console.error('Service Worker registration error:', error);
    },
  });

  useEffect(() => {
    if (needRefresh) {
      setShowPrompt(true);
    }
  }, [needRefresh]);

  const close = () => {
    setOfflineReady(false);
    setNeedRefresh(false);
    setShowPrompt(false);
  };

  const reload = () => {
    updateServiceWorker(true);
  };

  if (!showPrompt) {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 bg-white shadow-lg rounded-lg border border-gray-200 p-4 max-w-sm z-50">
      <div className="flex flex-col gap-3">
        <div className="flex items-start gap-2">
          <div className="flex-shrink-0 mt-0.5">
            <svg
              className="w-5 h-5 text-blue-500"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900">Update Available</h3>
            <p className="text-sm text-gray-600 mt-1">
              A new version of the app is available. Reload to update.
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={reload}
            className="flex-1 bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium px-4 py-2 rounded transition-colors"
          >
            Reload
          </button>
          <button
            onClick={close}
            className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm font-medium px-4 py-2 rounded transition-colors"
          >
            Later
          </button>
        </div>
      </div>
    </div>
  );
}

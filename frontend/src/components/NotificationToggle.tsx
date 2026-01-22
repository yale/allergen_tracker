import { useState, useEffect } from 'react';
import {
  subscribeToPushNotifications,
  unsubscribeFromPushNotifications,
  isSubscribedToPushNotifications,
} from '../services/notifications';

export function NotificationToggle() {
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSupported, setIsSupported] = useState(true);

  useEffect(() => {
    // Check if notifications are supported
    if (!('Notification' in window) || !('serviceWorker' in navigator) || !('PushManager' in window)) {
      setIsSupported(false);
      return;
    }

    // Check current subscription status
    isSubscribedToPushNotifications().then(setIsSubscribed);
  }, []);

  const handleToggle = async () => {
    setIsLoading(true);
    try {
      if (isSubscribed) {
        const success = await unsubscribeFromPushNotifications();
        if (success) {
          setIsSubscribed(false);
        }
      } else {
        const success = await subscribeToPushNotifications();
        if (success) {
          setIsSubscribed(true);
        }
      }
    } catch (error) {
      console.error('Error toggling notifications:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isSupported) {
    return null;
  }

  return (
    <div className="flex items-center gap-3 p-4 bg-white rounded-lg shadow">
      <div className="flex-1">
        <h3 className="font-semibold text-gray-900">Push Notifications</h3>
        <p className="text-sm text-gray-600">
          Get notified when a new feed is logged
        </p>
      </div>
      <button
        onClick={handleToggle}
        disabled={isLoading}
        className={`
          relative inline-flex h-6 w-11 items-center rounded-full
          transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
          ${isSubscribed ? 'bg-blue-600' : 'bg-gray-200'}
          ${isLoading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
        role="switch"
        aria-checked={isSubscribed}
      >
        <span
          className={`
            inline-block h-4 w-4 transform rounded-full bg-white transition-transform
            ${isSubscribed ? 'translate-x-6' : 'translate-x-1'}
          `}
        />
      </button>
    </div>
  );
}

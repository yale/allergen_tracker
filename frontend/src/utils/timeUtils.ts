/**
 * Calculate the number of days between two dates
 */
export function daysBetween(date1: Date, date2: Date): number {
  const msPerDay = 1000 * 60 * 60 * 24;
  const utc1 = Date.UTC(date1.getFullYear(), date1.getMonth(), date1.getDate());
  const utc2 = Date.UTC(date2.getFullYear(), date2.getMonth(), date2.getDate());
  return Math.floor((utc2 - utc1) / msPerDay);
}

/**
 * Calculate days since a past date
 */
export function daysSince(pastDate: Date, currentDate: Date = new Date()): number {
  return daysBetween(pastDate, currentDate);
}

/**
 * Format a date as relative time using Intl.RelativeTimeFormat
 * (e.g., "2 minutes ago", "3 hours ago", "2 days ago")
 */
export function formatRelativeTime(date: Date, currentDate: Date = new Date()): string {
  const seconds = Math.floor((currentDate.getTime() - date.getTime()) / 1000);

  const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' });

  if (seconds < 10) {
    return 'just now';
  }

  if (seconds < 60) {
    return rtf.format(-seconds, 'second');
  }

  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) {
    return rtf.format(-minutes, 'minute');
  }

  const hours = Math.floor(minutes / 60);
  if (hours < 24) {
    return rtf.format(-hours, 'hour');
  }

  const days = Math.floor(hours / 24);
  if (days < 30) {
    return rtf.format(-days, 'day');
  }

  const months = Math.floor(days / 30);
  if (months < 12) {
    return rtf.format(-months, 'month');
  }

  const years = Math.floor(months / 12);
  return rtf.format(-years, 'year');
}

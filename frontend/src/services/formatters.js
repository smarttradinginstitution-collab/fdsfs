/**
 * A service for consistently formatting data across the application.
 */

/**
 * Formats a number as a currency string (e.g., $1,234.56).
 * @param {number} value - The number to format.
 * @returns {string} The formatted currency string.
 */
export function formatCurrency(value) {
  if (typeof value !== 'number') {
    return '$0.00';
  }
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(value);
}

/**
 * Formats a number with a specific number of decimal places.
 * @param {number} value - The number to format.
 * @param {number} digits - The number of decimal places.
 * @returns {string} The formatted number string.
 */
export function formatNumber(value, digits = 0) {
    if (typeof value !== 'number') {
        return '0';
    }
    return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: digits,
        maximumFractionDigits: digits,
    }).format(value);
}

/**
 * Formats a number as a percentage string.
 * @param {number} value - The number to format (e.g., 85.5 for 85.5%).
 * @returns {string} The formatted percentage string.
 */
export function formatPercentage(value) {
    if (typeof value !== 'number') {
        return '0%';
    }
    return `${formatNumber(value, 2)}%`;
}
/**
 * Formatta una data in una stringa 'MM/DD/YYYY'.
 * @param {string | Date} date - La data da formattare.
 * @returns {string} La data formattata o un trattino se la data non è valida.
 */
export function formatDate(date) {
  if (!date) return '-';
  try {
    const d = new Date(date);
    // Controlla se la data è valida
    if (isNaN(d.getTime())) {
      return '-';
    }
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();
    return `${month}/${day}/${year}`;
  } catch (error) {
    return '-';
  }
}

/**
 * Formatta un numero in una stringa di valuta con segno e separatore delle migliaia.
 * @param {number} value - Il valore numerico da formattare.
 * @returns {string} La stringa formattata (es. "+$1,234.56" o "-$50.00").
 */
export function formatCurrency(value) {
  if (typeof value !== 'number') return '-';

  const sign = value >= 0 ? '+' : '-';
  const absoluteValue = Math.abs(value);

  const formattedValue = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD', // Puoi cambiarlo se necessario
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(absoluteValue);

  return `${sign}${formattedValue}`;
}

/**
 * Formatta un numero in una stringa percentuale.
 * @param {number} value - Il valore da formattare (es. 0.0819 per 8.19%).
 * @returns {string} La stringa formattata (es. "8.19%").
 */
export function formatPercentage(value) {
  if (typeof value !== 'number') return '-';

  return `${(value * 100).toFixed(2)}%`;
}
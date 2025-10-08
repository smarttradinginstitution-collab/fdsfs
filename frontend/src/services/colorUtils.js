/**
 * Converts a hex color code to an RGBA string.
 * @param {string} hex - The hex color code (e.g., "#RRGGBB").
 * @param {number} alpha - The alpha transparency value (0 to 1).
 * @returns {string} The RGBA color string.
 */
export function hexToRgba(hex, alpha = 1) {
  if (!hex || typeof hex !== 'string') {
    return `rgba(204, 204, 204, ${alpha})`; // Default gray if hex is invalid
  }

  const hexValue = hex.startsWith('#') ? hex.slice(1) : hex;
  const bigint = parseInt(hexValue, 16);
  const r = (bigint >> 16) & 255;
  const g = (bigint >> 8) & 255;
  const b = bigint & 255;

  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}
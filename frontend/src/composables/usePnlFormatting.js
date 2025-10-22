// frontend/src/composables/usePnlFormatting.js
import { computed } from 'vue';

export function usePnlFormatting() {
  const pnlStyle = (pnl, isLoss = false) => {
    if (isLoss) {
      return { color: 'var(--semantic-color-feedback-negative-text)' };
    }
    if (pnl > 0) {
      return { color: 'var(--semantic-color-feedback-positive-text)' };
    }
    if (pnl < 0) {
      return { color: 'var(--semantic-color-feedback-negative-text)' };
    }
    return {};
  };

  const formatPnl = (pnl, isLoss = false) => {
    if (pnl === null || pnl === undefined) return '$0.00';

    if (isLoss) {
      return `-$${Math.abs(pnl).toFixed(2)}`;
    }

    const sign = pnl >= 0 ? '+' : '-';
    return `${sign}$${Math.abs(pnl).toFixed(2)}`;
  };

  return {
    pnlStyle,
    formatPnl,
  };
}

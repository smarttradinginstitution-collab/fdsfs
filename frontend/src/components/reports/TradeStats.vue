<script setup>
import { computed } from 'vue';
import { formatCurrency, formatNumber, formatPercentage } from '@/services/formatters.js';
import IconButton from '@/components/ui/IconButton.vue';
import PencilIcon from '@/components/icons/PencilIcon.vue';

const props = defineProps({
  trade: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['open-edit-modal']);

const displayStats = computed(() => {
  if (!props.trade) return [];

  const t = props.trade;
  const placeholder = '$ -';
  const rMultiplePlaceholder = '0.00 R';

  // Define a static structure for all stats
  const stats = [
    // Net P&L
    {
      label: 'Net P&L',
      value: formatCurrency(t.p_l),
      style: t.p_l >= 0 ? 'pnl-positive' : 'pnl-negative',
      specialClass: 'net-pnl-stat'
    },
    // Side
    {
      label: 'Side',
      value: t.direction || '-'
    },
    // Commissions & Fees
    {
      label: 'Commissions & Fees',
      value: formatCurrency((t.fees || 0) + (t.commissions || 0) * -1),
      style: 'pnl-negative'
    },
    // Net ROI
    {
      label: 'Net ROI',
      value: t.net_roi != null ? formatPercentage(t.net_roi) : '0.00%',
      style: t.net_roi >= 0 ? 'pnl-positive' : 'pnl-negative'
    },
    // Gross P&L
    {
      label: 'Gross P&L',
      value: t.gross_p_l != null ? formatCurrency(t.gross_p_l) : placeholder
    },
    // Take Profit
    {
      label: 'Take Profit',
      value: t.take_profit_price != null ? formatCurrency(t.take_profit_price) : placeholder
    },
    // Stop Loss
    {
      label: 'Stop Loss',
      value: t.stop_loss_price != null ? formatCurrency(t.stop_loss_price) : placeholder,
      style: 'pnl-negative'
    },
    // MAE / MFE
    {
      label: 'MAE / MFE',
      isMaeMfe: true,
      mae: {
        value: t.mae_usd != null ? formatCurrency(t.mae_usd) : placeholder,
        style: 'pnl-negative' // Always red
      },
      mfe: {
        value: t.mfe_usd != null ? formatCurrency(t.mfe_usd) : placeholder,
        style: 'pnl-positive' // Always green
      }
    },
    // Playbook
    {
      label: 'Playbook',
      value: t.playbook ? t.playbook.title : 'Select Playbook',
      interactive: !t.playbook
    },
    // Trade Risk
    {
      label: 'Trade Risk',
      value: t.trade_risk != null ? formatCurrency(t.trade_risk) : placeholder,
      style: 'pnl-negative'
    },
    // Realized R-Multiple
    {
      label: 'Realized R-Multiple',
      value: t.r_multiple != null ? `${formatNumber(t.r_multiple, 2)} R` : rMultiplePlaceholder,
      style: t.r_multiple >= 0 ? 'pnl-positive' : 'pnl-negative'
    },
    // Average Entry
    {
      label: 'Average Entry',
      value: t.entry_price != null ? formatCurrency(t.entry_price) : placeholder
    },
    // Average Exit
    {
      label: 'Average Exit',
      value: t.exit_price != null ? formatCurrency(t.exit_price) : placeholder
    },
    // Entry Time
    {
      label: 'Entry Time',
      value: t.entry_timestamp ? new Date(t.entry_timestamp).toLocaleTimeString('en-GB') : '-'
    },
    // Exit Time
    {
      label: 'Exit Time',
      value: t.exit_timestamp ? new Date(t.exit_timestamp).toLocaleTimeString('en-GB') : '-'
    },
    // Confluences (Example of placeholder for interactive elements)
    {
      label: 'Confluences',
      value: t.tags && t.tags.length > 0 ? t.tags.map(tag => tag.name).join(', ') : 'Select tag',
      interactive: !(t.tags && t.tags.length > 0)
    },
    // Entry Timeframe
    {
      label: 'Entry Timeframe',
      value: 'Select Timeframe', // Assuming this is always interactive for now
      interactive: true
    }
  ];

  return stats;
});

</script>

<template>
  <div class="trade-stats-list">
    <div v-for="stat in displayStats" :key="stat.label" :class="['stat-item', stat.specialClass]">

      <div class="stat-label-wrapper">
        <span class="stat-label">{{ stat.label }}</span>
        <IconButton v-if="stat.specialClass === 'net-pnl-stat'" @click="$emit('open-edit-modal')" aria-label="Edit Details">
            <PencilIcon />
        </IconButton>
      </div>

      <div v-if="stat.isMaeMfe" class="mae-mfe-values">
          <span :class="['stat-value', 'pill', stat.mae.style]">{{ stat.mae.value }}</span>
          <span :class="['stat-value', 'pill', stat.mfe.style]">{{ stat.mfe.value }}</span>
      </div>

      <span v-else :class="['stat-value', stat.style, { 'is-interactive': stat.interactive }]">
        {{ stat.value }}
      </span>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.trade-stats-list {
  display: flex;
  flex-direction: column;
}

.stat-item {
  display: grid;
  grid-template-columns: 40% 1fr;
  gap: var(--semantic-size-stack-md);
  align-items: center;
  padding: var(--semantic-size-inset-sm) 0;
  border-bottom: 1px solid var(--semantic-color-border-subtle);
}

.stat-label-wrapper {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.stat-label {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
}

.stat-value {
  font: var(--semantic-font-style-label-md);
  color: var(--semantic-color-text-primary);

  &.pnl-positive {
    color: var(--semantic-color-feedback-positive-text);
  }

  &.pnl-negative {
    color: var(--semantic-color-feedback-negative-text);
  }

  &.is-interactive {
    cursor: pointer;
    color: var(--semantic-color-text-interactive);
    &:hover {
      text-decoration: underline;
    }
  }
}

.mae-mfe-values {
  display: flex;
  gap: var(--semantic-size-stack-xs);
}

.pill {
  padding: var(--semantic-size-inset-xs) var(--semantic-size-inset-sm);
  border-radius: var(--semantic-border-radius-tag);
  font: var(--semantic-font-style-label-sm);

  &.pnl-positive {
    background-color: var(--semantic-color-feedback-positive-surface);
    color: var(--semantic-color-feedback-positive-text);
  }

  &.pnl-negative {
    background-color: var(--semantic-color-feedback-negative-surface);
    color: var(--semantic-color-feedback-negative-text);
  }
}

// Special styling for the main Net P&L stat
.net-pnl-stat {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: var(--semantic-size-stack-xxs);
  padding-bottom: var(--semantic-size-inset-md);
  margin-bottom: var(--semantic-size-stack-sm);
  border-bottom: 1px solid var(--semantic-color-border-default);

  .stat-label-wrapper {
    font: var(--semantic-font-style-label-md);
  }

  .stat-value {
    font: var(--semantic-font-style-metric-display);
  }
}
</style>
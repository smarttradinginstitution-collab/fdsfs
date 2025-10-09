<script setup>
import { computed, ref } from 'vue';
import { useTradesStore } from '@/stores/trades';
import { useTagsStore } from '@/stores/tagsStore';
import { formatCurrency, formatNumber, formatPercentage } from '@/services/formatters.js';
import IconButton from '@/components/ui/IconButton.vue';
import PencilIcon from '@/components/icons/PencilIcon.vue';
import TagSelector from '@/components/tags/TagSelector.vue';
import BasePill from '@/components/ui/BasePill.vue';
import BaseButton from '@/components/ui/BaseButton.vue';

const props = defineProps({
  trade: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['open-edit-modal']);

const tradesStore = useTradesStore();
const tagsStore = useTagsStore();
const isEditingTags = ref(false);
const selectedTagIds = ref(props.trade.tags?.map(t => t.id) || []);

const displayStats = computed(() => {
    if (!props.trade) return [];
    const t = props.trade;
    const placeholder = '$ -';
    const rMultiplePlaceholder = '0.00 R';
    return [
        { label: 'Net P&L', value: formatCurrency(t.p_l), style: t.p_l >= 0 ? 'pnl-positive' : 'pnl-negative', specialClass: 'net-pnl-stat' },
        { label: 'Side', value: t.direction || '-' },
        { label: 'Commissions & Fees', value: formatCurrency((t.fees || 0) + (t.commissions || 0) * -1), style: 'pnl-negative' },
        { label: 'Net ROI', value: t.net_roi != null ? formatPercentage(t.net_roi) : '0.00%', style: t.net_roi >= 0 ? 'pnl-positive' : 'pnl-negative' },
        { label: 'Gross P&L', value: t.gross_p_l != null ? formatCurrency(t.gross_p_l) : placeholder },
        { label: 'Take Profit', value: t.take_profit_price != null ? formatCurrency(t.take_profit_price) : placeholder },
        { label: 'Stop Loss', value: t.stop_loss_price != null ? formatCurrency(t.stop_loss_price) : placeholder },
        { label: 'MAE / MFE', isMaeMfe: true, mae: { value: t.mae_usd != null ? formatCurrency(t.mae_usd) : placeholder, style: 'pnl-negative' }, mfe: { value: t.mfe_usd != null ? formatCurrency(t.mfe_usd) : placeholder, style: 'pnl-positive' }},
        { label: 'Playbook', value: t.playbook ? t.playbook.title : 'Select Playbook', interactive: !t.playbook },
        { label: 'Planned Target', value: t.planned_target != null ? formatCurrency(t.planned_target) : placeholder, style: 'pnl-positive' },
        { label: 'Trade Risk', value: t.trade_risk != null ? formatCurrency(t.trade_risk) : placeholder, style: 'pnl-negative' },
        { label: 'Planned R-multiple', value: t.planned_r_multiple != null ? `${formatNumber(t.planned_r_multiple, 2)} R` : '- R', style: 'pnl-positive' },
        { label: 'Realized R-Multiple', value: t.r_multiple != null ? `${formatNumber(t.r_multiple, 2)} R` : rMultiplePlaceholder, style: t.r_multiple >= 0 ? 'pnl-positive' : 'pnl-negative' },
        { label: 'Average Entry', value: t.entry_price != null ? formatCurrency(t.entry_price) : placeholder },
        { label: 'Average Exit', value: t.exit_price != null ? formatCurrency(t.exit_price) : placeholder },
        { label: 'Entry Time', value: t.entry_timestamp ? new Date(t.entry_timestamp).toLocaleTimeString('en-GB') : '-' },
        { label: 'Exit Time', value: t.exit_timestamp ? new Date(t.exit_timestamp).toLocaleTimeString('en-GB') : '-' },
    ];
});

const groupedTradeTags = computed(() => {
    if (!props.trade?.tags?.length) return [];
    const groups = {};
    props.trade.tags.forEach(tag => {
        const groupId = tag.group_id;
        if (!groups[groupId]) {
            const groupInfo = tagsStore.tagGroups.find(g => g.id === groupId);
            groups[groupId] = {
                id: groupId,
                name: groupInfo ? groupInfo.name : 'Uncategorized',
                tags: []
            };
        }
        groups[groupId].tags.push(tag);
    });
    return Object.values(groups);
});

const getTextColor = (bgColor) => {
  if (!bgColor) return '#ffffff';
  const color = (bgColor.charAt(0) === '#') ? bgColor.substring(1, 7) : bgColor;
  const r = parseInt(color.substring(0, 2), 16);
  const g = parseInt(color.substring(2, 4), 16);
  const b = parseInt(color.substring(4, 6), 16);
  const brightness = ((r * 299) + (g * 587) + (b * 114)) / 1000;
  return (brightness > 155) ? '#000000' : '#ffffff';
};

const handleSaveTags = async () => {
    await tradesStore.updateTradeTags(props.trade.id, selectedTagIds.value);
    isEditingTags.value = false;
};

const handleCancelEditTags = () => {
    selectedTagIds.value = props.trade.tags?.map(t => t.id) || [];
    isEditingTags.value = false;
};

</script>

<template>
  <div class="trade-stats-container">
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
          /
          <span :class="['stat-value', 'pill', stat.mfe.style]">{{ stat.mfe.value }}</span>
        </div>
        <span v-else :class="['stat-value', stat.style, { 'is-interactive': stat.interactive }]">
          {{ stat.value }}
        </span>
      </div>
    </div>

    <div class="tags-section">
      <div class="tags-header">
        <h3 class="section-title">Tags</h3>
        <IconButton @click="isEditingTags = true" v-if="!isEditingTags">
          <PencilIcon />
        </IconButton>
      </div>
      <div v-if="!isEditingTags" class="tags-display">
        <div v-for="group in groupedTradeTags" :key="group.id" class="stat-item">
          <span class="stat-label">{{ group.name }}</span>
          <div class="tag-pills-display">
            <BasePill
              v-for="tag in group.tags"
              :key="tag.id"
              :style="{ backgroundColor: tag.color, color: getTextColor(tag.color) }"
            >
              {{ tag.name }}
            </BasePill>
          </div>
        </div>
        <p v-if="groupedTradeTags.length === 0" class="no-tags-message">No tags assigned.</p>
      </div>
      <div v-else class="tag-editor">
        <TagSelector v-model="selectedTagIds" />
        <div class="editor-actions">
          <BaseButton variant="secondary" size="small" @click="handleCancelEditTags">Cancel</BaseButton>
          <BaseButton size="small" @click="handleSaveTags" :loading="tradesStore.isTradeLoading">Save Tags</BaseButton>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.trade-stats-container {
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
  &.pnl-positive { color: var(--semantic-color-feedback-positive-text); }
  &.pnl-negative { color: var(--semantic-color-feedback-negative-text); }
  &.is-interactive {
    cursor: pointer;
    color: var(--semantic-color-text-interactive);
    &:hover { text-decoration: underline; }
  }
}
.mae-mfe-values {
  display: flex;
  gap: var(--semantic-size-stack-xs);
}
.pill {
  padding: var(--semantic-size-inset-xs) var(--semantic-size-inset-sm);
  border-radius: var(--semantic-border-radius-interactive);
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
.net-pnl-stat {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: var(--semantic-size-stack-xxs);
  padding-bottom: var(--semantic-size-inset-md);
  margin-bottom: var(--semantic-size-stack-sm);
  border-bottom: 1px solid var(--semantic-color-border-default);
  .stat-label-wrapper { font: var(--semantic-font-style-label-md); }
  .stat-value { font: var(--semantic-font-style-metric-display); }
}
.tags-section {
  margin-top: var(--semantic-size-stack-lg);
}
.tags-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--semantic-size-stack-sm);
  h3 {
    font: var(--semantic-font-style-heading-md);
    color: var(--semantic-color-text-primary);
  }
}
.tag-pills-display {
  display: flex;
  flex-wrap: wrap;
  gap: var(--semantic-size-stack-xs);
}
.no-tags-message {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  padding: var(--semantic-size-inset-sm) 0;
}
.tag-editor {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
}
.editor-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--semantic-size-stack-sm);
}
</style>
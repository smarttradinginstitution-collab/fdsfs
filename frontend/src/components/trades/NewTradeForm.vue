<!--
// =============================================================================
// FILE: components/trades/NewTradeForm.vue
// DESCRIZIONE: Questo è un componente specifico che rappresenta il form
// per inserire un nuovo trade. Viene tipicamente usato all'interno di una
// finestra modale.
// =============================================================================
-->

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useTradesStore } from '@/stores/trades';
import { usePlaybookStore } from '@/stores/playbookStore';
import { useLabelsStore } from '@/stores/labelsStore';
import { useNewsImpactsStore } from '@/stores/newsImpactsStore';
import BaseInput from '../ui/BaseInput.vue';
import BaseButton from '../ui/BaseButton.vue';
import BaseSelect from '../ui/BaseInput.vue'; // Sostituito BaseMultiSelect

const tradesStore = useTradesStore();
const playbookStore = usePlaybookStore();
const labelsStore = useLabelsStore();
const newsImpactsStore = useNewsImpactsStore();
const emit = defineEmits(['submit']);

onMounted(() => {
  playbookStore.fetchPlaybooks();
  labelsStore.fetchLabelsIfNeeded('mistakes');
  labelsStore.fetchLabelsIfNeeded('psychology-states');
  labelsStore.fetchLabelsIfNeeded('tags');
  newsImpactsStore.fetchAllNewsImpactsData();
});

// CORREZIONE: Tutti i componenti ora usano il formato `{ value, text }` richiesto da BaseSelect
const playbooksOptions = computed(() =>
  playbookStore.playbooks.map(p => ({ value: p.id, text: p.title }))
);

const mistakesOptions = computed(() =>
  (labelsStore.labels.mistakes || []).map(m => ({ value: m.id, text: m.name }))
);

const psychologyStatesOptions = computed(() =>
  (labelsStore.labels['psychology-states'] || []).map(p => ({ value: p.id, text: p.name }))
);

const tagsOptions = computed(() =>
  (labelsStore.labels.tags || []).map(t => ({ value: t.id, text: t.name }))
);

const newsImpactsOptions = computed(() =>
  newsImpactsStore.newsImpacts.map(ni => ({ value: ni.id, text: ni.name }))
);

const rulesOptions = computed(() => {
  if (!playbookStore.ruleGroups) return [];
  return playbookStore.ruleGroups.flatMap(group =>
    group.rules.map(rule => ({ value: rule.id, text: `(${group.name_group}) ${rule.rule}` }))
  );
});

const getInitialFormState = () => ({
  symbol_snapshot: '',
  pnl: 0,
  direction: 'LONG',
  entry_price: null,
  exit_price: null,
  stop_loss_price: null,
  take_profit_price: null,
  position_size: null,
  lowest_price_during_trade: null,
  highest_price_during_trade: null,
  entry_timestamp: null,
  exit_timestamp: null,
  playbook_id: null,
  tag_ids: [],
  mistake_ids: [],
  news_impact_ids: [],
  psychology_state_ids: [],
  rules_followed_ids: [],
});

const form = ref(getInitialFormState());

watch(() => form.value.playbook_id, (newPlaybookId) => {
  if (newPlaybookId) {
    playbookStore.fetchRuleGroups(newPlaybookId);
  }
  form.value.rules_followed_ids = [];
});

const handleSubmit = () => {
  const payload = { ...form.value };
  if (payload.entry_timestamp) {
    payload.entry_timestamp = new Date(payload.entry_timestamp).toISOString();
  }
  if (payload.exit_timestamp) {
    payload.exit_timestamp = new Date(payload.exit_timestamp).toISOString();
  }
  emit('submit', payload);
  form.value = getInitialFormState();
};
</script>

<template>
  <form class="new-trade-form" @submit.prevent="handleSubmit">

    <fieldset class="form-section">
      <legend>Timestamps</legend>
      <div class="grid-group grid-group-2-col">
        <BaseInput v-model="form.entry_timestamp" label="Entry Timestamp" type="datetime-local" />
        <BaseInput v-model="form.exit_timestamp" label="Exit Timestamp" type="datetime-local" />
      </div>
    </fieldset>

    <fieldset class="form-section">
      <legend>Core Information</legend>
      <div class="grid-group grid-group-3-col">
        <BaseInput v-model="form.symbol_snapshot" label="Symbol" placeholder="e.g., AAPL" />
        <BaseSelect v-model="form.direction" label="Direction" :options="[{value: 'LONG', text: 'Long'}, {value: 'SHORT', text: 'Short'}]" />
        <BaseInput v-model.number="form.pnl" label="Net P&L" type="number" step="0.01" />
      </div>
    </fieldset>

    <fieldset class="form-section">
      <legend>Playbook & Associations</legend>
      <div class="grid-group grid-group-1-col">
        <BaseSelect v-model="form.playbook_id" label="Playbook" :options="playbooksOptions" default-option-text="Select a playbook" />
      </div>
       <div class="grid-group grid-group-2-col associations-group">
        <BaseSelect v-model="form.tag_ids" label="Tags" :options="tagsOptions" :multiple="true" />
        <BaseSelect v-model="form.mistake_ids" label="Mistakes" :options="mistakesOptions" :multiple="true" />
        <BaseSelect v-model="form.news_impact_ids" label="News Impacts" :options="newsImpactsOptions" :multiple="true" />
        <BaseSelect v-model="form.psychology_state_ids" label="Psychology States" :options="psychologyStatesOptions" :multiple="true" />
      </div>
      <div v-if="rulesOptions.length > 0" class="grid-group grid-group-1-col associations-group">
        <BaseSelect v-model="form.rules_followed_ids" label="Rules Followed" :options="rulesOptions" :multiple="true" />
      </div>
    </fieldset>

    <fieldset class="form-section">
      <legend>Prices & Size</legend>
      <div class="grid-group grid-group-4-col">
        <BaseInput v-model.number="form.entry_price" label="Entry Price" type="number" step="0.01" />
        <BaseInput v-model.number="form.exit_price" label="Exit Price" type="number" step="0.01" />
        <BaseInput v-model.number="form.stop_loss_price" label="Stop Loss" type="number" step="0.01" />
        <BaseInput v-model.number="form.take_profit_price" label="Take Profit" type="number" step="0.01" />
        <BaseInput v-model.number="form.lowest_price_during_trade" label="Lowest Price (MAE)" type="number" step="0.01" />
        <BaseInput v-model.number="form.highest_price_during_trade" label="Highest Price (MFE)" type="number" step="0.01" />
        <BaseInput v-model.number="form.position_size" label="Position Size" type="number" step="0.01" />
      </div>
    </fieldset>

    <div class="form-actions">
      <BaseButton type="submit" :is-loading="tradesStore.isLoading">
        Save Trade
      </Button>
    </div>
  </form>
</template>

<style scoped>
.new-trade-form {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xl);
}

.form-section {
  border: 1px solid var(--semantic-color-border-default);
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-surface);
  padding: var(--semantic-size-inset-lg);
  padding-top: var(--semantic-size-inset-xl);
  margin-top: var(--semantic-size-stack-lg);
  position: relative;
}

.form-section:first-of-type {
  margin-top: 0;
}

.form-section legend {
  position: absolute;
  top: 0;
  left: 16px;
  transform: translateY(-50%);
  background: var(--semantic-color-surface-secondary);
  padding: var(--semantic-size-inset-xs) var(--semantic-size-inset-md);
  font: var(--semantic-font-style-label-md);
  font-weight: 600;
  color: var(--semantic-color-text-primary);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-pill);
}

.grid-group {
  display: grid;
  gap: var(--semantic-size-stack-md);
}

.grid-group-4-col { grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); }
.grid-group-3-col { grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }
.grid-group-2-col { grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }

.form-actions {
  margin-top: var(--semantic-size-stack-lg);
  display: flex;
  justify-content: flex-end;
}
</style>

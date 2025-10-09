<template>
  <div class="qualitative-analysis-section">
    <!-- Existing Tag Manager -->
    <div class="label-row">
        <span class="label-title">Tags</span>
        <div class="selector-wrapper">
            <TradeTagManager :trade="trade" />
        </div>
    </div>

    <!-- Mistakes Selector -->
    <div class="label-row">
        <span class="label-title">Mistakes</span>
        <div class="selector-wrapper">
            <SimpleLabelSelector
                item-type-name="Mistake"
                placeholder="Select mistakes..."
                :all-items="mistakesStore.mistakes"
                :model-value="tradeMistakeIds"
                @update:modelValue="tradesStore.updateTradeMistakes(trade.id, $event)"
            />
        </div>
    </div>

    <!-- Psychology Selector -->
    <div class="label-row">
        <span class="label-title">Psychology</span>
        <div class="selector-wrapper">
            <SimpleLabelSelector
                item-type-name="Psychology State"
                placeholder="Select psychology states..."
                :all-items="psychologyStore.psychologyStates"
                :model-value="tradePsychologyStateIds"
                @update:modelValue="tradesStore.updateTradePsychologyStates(trade.id, $event)"
            />
        </div>
    </div>

    <!-- News Impact Selector -->
    <div class="label-row">
        <span class="label-title">News Impact</span>
        <div class="selector-wrapper">
             <SimpleLabelSelector
                item-type-name="News Impact"
                placeholder="Select news impacts..."
                :all-items="newsImpactsStore.newsImpacts"
                :model-value="tradeNewsImpactIds"
                @update:modelValue="tradesStore.updateTradeNewsImpacts(trade.id, $event)"
            />
        </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, onMounted, computed } from 'vue';
import TradeTagManager from './TradeTagManager.vue';
import SimpleLabelSelector from './SimpleLabelSelector.vue';
import { useTradesStore } from '@/stores/trades';
import { useMistakesStore } from '@/stores/mistakesStore';
import { usePsychologyStatesStore } from '@/stores/psychologyStatesStore';
import { useNewsImpactsStore } from '@/stores/newsImpactsStore';

const props = defineProps({
  trade: {
    type: Object,
    required: true,
  },
});

const tradesStore = useTradesStore();
const mistakesStore = useMistakesStore();
const psychologyStore = usePsychologyStatesStore();
const newsImpactsStore = useNewsImpactsStore();

onMounted(() => {
    // Fetch all available labels if they aren't already in the stores
    if (mistakesStore.mistakes.length === 0) mistakesStore.fetchAllMistakes();
    if (psychologyStore.psychologyStates.length === 0) psychologyStore.fetchAllPsychologyStates();
    if (newsImpactsStore.newsImpacts.length === 0) newsImpactsStore.fetchAllNewsImpacts();
});

// Computed properties to extract just the IDs for v-model
const tradeMistakeIds = computed(() => props.trade.mistakes?.map(item => item.id) || []);
const tradePsychologyStateIds = computed(() => props.trade.psychology_states?.map(item => item.id) || []);
const tradeNewsImpactIds = computed(() => props.trade.news_impacts?.map(item => item.id) || []);

</script>

<style scoped>
.qualitative-analysis-section {
  display: flex;
  flex-direction: column;
}
.label-row {
  display: grid;
  grid-template-columns: 40% 1fr;
  gap: var(--semantic-size-stack-md);
  align-items: center;
  padding: var(--semantic-size-inset-sm) 0;
  border-bottom: 1px solid var(--semantic-color-border-subtle);
}
.label-title {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  justify-self: start;
}
.selector-wrapper {
    min-width: 0;
}
</style>
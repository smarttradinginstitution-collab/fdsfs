<template>
  <div class="qualitative-analysis-section">
    <!-- Mistakes Row -->
    <div class="label-row">
      <span class="label-title">Mistakes</span>
      <div class="pills-container">
        <BasePill
          v-for="item in selectedMistakes"
          :key="item.id"
          :style="{ backgroundColor: item.color, color: getTextColor(item.color) }"
        >
          {{ item.name }}
        </BasePill>
        <p v-if="selectedMistakes.length === 0" class="no-items-message">-</p>
        <IconButton @click="openModal('mistakes')" class="add-btn"><PlusIcon /></IconButton>
      </div>
    </div>

    <!-- Psychology Row -->
    <div class="label-row">
      <span class="label-title">Psychology</span>
      <div class="pills-container">
        <BasePill
          v-for="item in selectedPsychologyStates"
          :key="item.id"
          :style="{ backgroundColor: item.color, color: getTextColor(item.color) }"
        >
          {{ item.name }}
        </BasePill>
        <p v-if="selectedPsychologyStates.length === 0" class="no-items-message">-</p>
        <IconButton @click="openModal('psychology')" class="add-btn"><PlusIcon /></IconButton>
      </div>
    </div>

    <!-- News Impact Row -->
    <div class="label-row">
      <span class="label-title">News Impact</span>
      <div class="pills-container">
        <BasePill
          v-for="item in selectedNewsImpacts"
          :key="item.id"
          :style="{ backgroundColor: item.color, color: getTextColor(item.color) }"
        >
          {{ item.name }}
        </BasePill>
        <p v-if="selectedNewsImpacts.length === 0" class="no-items-message">-</p>
        <IconButton @click="openModal('news')" class="add-btn"><PlusIcon /></IconButton>
      </div>
    </div>

    <!-- Reusable Modal -->
    <LabelSelectorModal
      v-if="activeModal"
      :show="!!activeModal"
      :title="modalConfig.title"
      :item-type-name="modalConfig.itemTypeName"
      :all-items="modalConfig.allItems"
      :selected-ids="modalConfig.selectedIds"
      @close="closeModal"
      @save="handleSave"
    />
  </div>
</template>

<script setup>
import { defineProps, onMounted, computed, ref } from 'vue';
import BasePill from '@/components/ui/BasePill.vue';
import IconButton from '@/components/ui/IconButton.vue';
import PlusIcon from '@/components/icons/PlusIcon.vue';
import LabelSelectorModal from './LabelSelectorModal.vue';
import { useTradesStore } from '@/stores/trades';
import { useMistakesStore } from '@/stores/mistakesStore';
import { usePsychologyStatesStore } from '@/stores/psychologyStatesStore';
import { useNewsImpactsStore } from '@/stores/newsImpactsStore';

const props = defineProps({
  trade: { type: Object, required: true },
});

// --- STORES ---
const tradesStore = useTradesStore();
const mistakesStore = useMistakesStore();
const psychologyStore = usePsychologyStatesStore();
const newsImpactsStore = useNewsImpactsStore();

// --- STATE ---
const activeModal = ref(null); // can be 'mistakes', 'psychology', 'news', or null

// --- LIFECYCLE ---
onMounted(() => {
  if (mistakesStore.mistakes.length === 0) mistakesStore.fetchAllMistakes();
  if (psychologyStore.psychologyStates.length === 0) psychologyStore.fetchAllPsychologyStates();
  if (newsImpactsStore.newsImpacts.length === 0) newsImpactsStore.fetchAllNewsImpacts();
});

// --- COMPUTED ---
const selectedMistakes = computed(() => props.trade.mistakes || []);
const selectedPsychologyStates = computed(() => props.trade.psychology_states || []);
const selectedNewsImpacts = computed(() => props.trade.news_impacts || []);

const modalConfig = computed(() => {
  switch (activeModal.value) {
    case 'mistakes':
      return {
        title: 'Select Mistakes',
        itemTypeName: 'Mistake',
        allItems: mistakesStore.mistakes,
        selectedIds: selectedMistakes.value.map(i => i.id),
      };
    case 'psychology':
      return {
        title: 'Select Psychology States',
        itemTypeName: 'Psychology State',
        allItems: psychologyStore.psychologyStates,
        selectedIds: selectedPsychologyStates.value.map(i => i.id),
      };
    case 'news':
      return {
        title: 'Select News Impacts',
        itemTypeName: 'News Impact',
        allItems: newsImpactsStore.newsImpacts,
        selectedIds: selectedNewsImpacts.value.map(i => i.id),
      };
    default:
      return {};
  }
});

// --- METHODS ---
const openModal = (modalType) => {
  activeModal.value = modalType;
};

const closeModal = () => {
  activeModal.value = null;
};

const handleSave = (selectedIds) => {
  const tradeId = props.trade.id;
  switch (activeModal.value) {
    case 'mistakes':
      tradesStore.updateTradeMistakes(tradeId, selectedIds);
      break;
    case 'psychology':
      tradesStore.updateTradePsychologyStates(tradeId, selectedIds);
      break;
    case 'news':
      tradesStore.updateTradeNewsImpacts(tradeId, selectedIds);
      break;
  }
  closeModal();
};

const getTextColor = (bgColor) => {
  if (!bgColor) return '#ffffff';
  const color = (bgColor.charAt(0) === '#') ? bgColor.substring(1, 7) : bgColor;
  const r = parseInt(color.substring(0, 2), 16);
  const g = parseInt(color.substring(2, 4), 16);
  const b = parseInt(color.substring(4, 6), 16);
  const brightness = ((r * 299) + (g * 587) + (b * 114)) / 1000;
  return (brightness > 155) ? '#000000' : '#ffffff';
};
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
.pills-container {
  display: flex;
  flex-wrap: wrap;
  gap: var(--semantic-size-stack-xs);
  align-items: center;
}
.no-items-message {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  margin: 0;
  padding: 0 var(--semantic-size-inset-sm);
}
.add-btn {
  margin-left: var(--semantic-size-stack-xs);
}
</style>
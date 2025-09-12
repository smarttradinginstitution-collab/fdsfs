<script setup>
import { computed } from 'vue';
import StatCard from './StatCard.vue';
import { useUiStore } from '../../stores/uiStore';
import { useTradesStore } from '../../stores/trades';

const uiStore = useUiStore();
const tradesStore = useTradesStore();

const visibleStats = computed(() => {
  const visibleKeys = uiStore.visibleStatKeys;
  const allStats = tradesStore.allDashboardStats;
  return visibleKeys.map(key => allStats[key]).filter(Boolean);
});
</script>

<template>
  <div class="stats-grid-widget">
    <StatCard
      v-for="stat in visibleStats"
      :key="stat.key"
      :stat="stat"
    />
  </div>
</template>

<style scoped>
.stats-grid-widget {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--semantic-size-stack-md);
  width: 100%;
  height: 100%;
  overflow-y: auto; /* Aggiunto per gestire lo scroll interno se necessario */
}
</style>

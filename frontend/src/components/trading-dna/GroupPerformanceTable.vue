<template>
  <div class="group-performance-container">
    <h3 class="title">Analysis by Tag Group</h3>
    <div class="table-container">
      <div class="table-header">
        <span class="header-item group-name">Group</span>
        <span class="header-item">Trades</span>
        <span class="header-item">Win Rate</span>
        <span class="header-item">Avg. R-Multiple</span>
      </div>
      <div v-if="performanceData.length === 0" class="empty-state">
        <p>No data to display. Apply some filters to see the analysis.</p>
      </div>
      <div v-else class="table-body">
        <div v-for="item in performanceData" :key="item.group.id" class="table-row">
          <span class="row-item group-name">{{ item.group.name }}</span>
          <span class="row-item">{{ item.metrics.trade_count }}</span>
          <span class="row-item">{{ item.metrics.win_rate_percent }}%</span>
          <span class="row-item">{{ item.metrics.average_r_multiple }}R</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  performanceData: {
    type: Array,
    required: true,
  },
});
</script>

<style scoped>
.group-performance-container {
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-surface);
  padding: var(--semantic-size-inset-lg);
}

.title {
  font: var(--semantic-font-style-heading-lg);
  margin-bottom: var(--semantic-size-stack-md);
}

.table-container {
  display: flex;
  flex-direction: column;
}

.table-header, .table-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: var(--semantic-size-stack-md);
  padding: var(--semantic-size-inset-sm) 0;
  align-items: center;
}

.table-header {
  font: var(--semantic-font-style-label-md);
  color: var(--semantic-color-text-secondary);
  border-bottom: 1px solid var(--semantic-color-border-default);
}

.table-row {
  font: var(--semantic-font-style-body-base);
  border-bottom: 1px solid var(--semantic-color-surface-secondary);
}

.table-row:last-child {
  border-bottom: none;
}

.group-name {
  font-weight: var(--semantic-font-weight-bold);
}

.empty-state {
  text-align: center;
  padding: var(--semantic-size-inset-xl);
  color: var(--semantic-color-text-secondary);
  font: var(--semantic-font-style-body-base);
}
</style>
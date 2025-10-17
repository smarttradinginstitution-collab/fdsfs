<template>
  <div class="progress-tracker-view">
    <div class="main-content">
      <div class="left-column">
        <SummarySidebar />
      </div>
      <div class="right-column">
        <Heatmap />
        <RulesTable />
      </div>
    </div>
  </div>
</template>

<script setup>
import SummarySidebar from '../components/progress-tracker/SummarySidebar.vue';
import Heatmap from '../components/progress-tracker/Heatmap.vue';
import RulesTable from '../components/progress-tracker/RulesTable.vue';
</script>

<style scoped>
.progress-tracker-view {
  padding: 2rem;
}

.main-content {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 2rem;
}

.right-column {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}
</style>
<template>
  <div class="progress-tracker-container">
    <div class="main-content">
      <SummarySidebar
        :score="disciplineStore.dailyScore"
        :completed="disciplineStore.completedRulesCount"
        :total="disciplineStore.totalRulesCount"
      />
      <DailyChecklist
        :manual-rules="disciplineStore.manualRules"
        :automated-rules="disciplineStore.automatedRules"
        @update-rule-status="handleUpdateStatus"
      />
      <CalendarHeatmap :heatmap-data="disciplineStore.heatmapData" />
    </div>
    <RulesTable
      :rules="disciplineStore.disciplineRules"
      @edit-rules="isEditModalOpen = true"
    />
    <EditRulesModal
      :is-open="isEditModalOpen"
      @close="isEditModalOpen = false"
      @save="handleSaveRules"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useDisciplineStore } from '@/stores/disciplineStore';
import SummarySidebar from '@/components/discipline/SummarySidebar.vue';
import DailyChecklist from '@/components/discipline/DailyChecklist.vue';
import CalendarHeatmap from '@/components/discipline/CalendarHeatmap.vue';
import RulesTable from '@/components/discipline/RulesTable.vue';
import EditRulesModal from '@/components/discipline/EditRulesModal.vue';

const disciplineStore = useDisciplineStore();
const isEditModalOpen = ref(false);

onMounted(() => {
  disciplineStore.fetchDailyChecklist();
  disciplineStore.fetchDisciplineRules();

  const today = new Date();
  const year = today.getFullYear();
  const month = today.getMonth() + 1; // JS months are 0-indexed
  disciplineStore.fetchHeatmapData(year, month);
});

function handleUpdateStatus(instanceId, newStatus) {
  disciplineStore.updateManualRuleStatus(instanceId, newStatus);
}

function handleSaveRules() {
  // Logic to save rules will be implemented here
  console.log('Saving rules...');
}
</script>

<style scoped>
.progress-tracker-container {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.main-content {
  display: flex;
  gap: 2rem;
}
</style>
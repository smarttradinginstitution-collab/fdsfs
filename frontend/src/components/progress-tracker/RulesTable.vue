<template>
  <div class="rules-table">
    <div class="table-header">
      <h3>Current Rules</h3>
      <button @click="openEditRulesModal">Edit Rules</button>
    </div>
    <table>
      <thead>
        <tr>
          <th>Rule</th>
          <th>Condition</th>
          <th>Average Performance</th>
          <th>Follow Rate</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="rule in rules" :key="rule.id">
          <td>{{ rule.name }}</td>
          <td>{{ getCondition(rule) }}</td>
          <td>N/A</td>
          <td>{{ summary?.follow_rate[rule.name] || 0 }}%</td>
        </tr>
      </tbody>
    </table>
    <EditRulesModal ref="editRulesModal" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import EditRulesModal from './EditRulesModal.vue';
import { useDisciplineStore } from '../../stores/disciplineStore';

const disciplineStore = useDisciplineStore();
const editRulesModal = ref(null);

const rules = computed(() => disciplineStore.rules);
const summary = computed(() => disciplineStore.summary);

const openEditRulesModal = () => {
  if (editRulesModal.value) {
    editRulesModal.value.openModal();
  }
};

const getCondition = (rule) => {
  if (rule.condition_type === 'TIME') {
    return rule.condition_value.time;
  }
  if (rule.condition_type === 'PERCENTAGE') {
    return `${rule.condition_value.percentage}%`;
  }
  if (rule.condition_type === 'FIXED_AMOUNT') {
    return `$${rule.condition_value.amount}`;
  }
  if (rule.condition_type === 'PERCENTAGE_OR_FIXED') {
    return `${rule.condition_value.percentage}% or $${rule.condition_value.amount}`;
  }
  return 'N/A';
};

onMounted(() => {
  disciplineStore.fetchRules();
  disciplineStore.fetchSummary();
});
</script>

<style scoped>
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}
</style>
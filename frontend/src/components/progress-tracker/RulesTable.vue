<template>
  <div class="rules-table">
    <div class="table-header">
      <h3>Current Rules</h3>
      <button @click="openEditRulesModal">Edit Rules</button>
    </div>
    <!-- Rules table will go here -->
    <EditRulesModal ref="editRulesModal" />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import EditRulesModal from './EditRulesModal.vue';

const editRulesModal = ref(null);

const openEditRulesModal = () => {
  if (editRulesModal.value) {
    editRulesModal.value.openModal();
  }
};
</script>

<style scoped>
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
</style>

<style scoped>
.rules-table {
  padding: 1.5rem;
  background-color: #f9fafb;
  border-radius: 8px;
}
</style>
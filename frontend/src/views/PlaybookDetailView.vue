<template>
  <div class="playbook-detail-view">
    <h1>Playbook Detail Page</h1>
    <p>Details for Playbook with ID: <strong>{{ playbookId }}</strong></p>
    <div class="placeholder-content">
      <p>This page is under construction.</p>
      <p>Full editing and rule management features for this playbook will be available here soon.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const playbookId = ref(null);

onMounted(() => {
  playbookId.value = route.params.id;
});
</script>

<style scoped>
.playbook-detail-view {
  padding: 2rem;
  color: var(--semantic-color-text-primary);
}

h1 {
  font: var(--semantic-font-style-heading-xl);
  margin-bottom: 1rem;
}

p {
  font: var(--semantic-font-style-body-lg);
  margin-bottom: 2rem;
}

.placeholder-content {
  border: 1px dashed var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-container);
  padding: 2rem;
  text-align: center;
  background-color: var(--semantic-color-surface-secondary);
}

.placeholder-content p {
  margin: 0.5rem 0;
  color: var(--semantic-color-text-secondary);
}
</style>
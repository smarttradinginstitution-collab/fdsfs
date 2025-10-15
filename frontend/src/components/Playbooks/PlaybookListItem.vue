<template>
  <div :class="['playbook-card', layoutClass]" @click="goToPlaybookDetails">
    <div class="playbook-card-content">
      <h3 class="playbook-title">{{ playbook.title }}</h3>
      <p class="playbook-description">{{ playbook.description }}</p>
      <div class="playbook-stats">
        <span>Rules: {{ playbook.rules_count || 0 }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps({
  playbook: {
    type: Object,
    required: true,
  },
  layout: {
    type: String,
    default: 'grid', // 'grid' or 'list'
  },
});

const router = useRouter();

const layoutClass = computed(() => {
  return props.layout === 'grid' ? 'layout-grid' : 'layout-list';
});

function goToPlaybookDetails() {
  router.push({ name: 'playbook-detail', params: { id: props.playbook.id } });
}
</script>

<style scoped>
.playbook-card {
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-container);
  padding: var(--semantic-size-inset-lg);
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  background-color: var(--semantic-color-surface-primary);
}

.playbook-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--semantic-effect-shadow-md);
  border-color: var(--semantic-color-border-hover);
}

.layout-list {
  display: flex;
  flex-direction: column;
}

.playbook-title {
  font: var(--semantic-font-style-heading-sm);
  color: var(--semantic-color-text-primary);
  margin-bottom: var(--semantic-size-stack-sm);
}

.playbook-description {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  margin-bottom: var(--semantic-size-stack-md);
  flex-grow: 1;
}

.playbook-stats {
  display: flex;
  gap: var(--semantic-size-gap-lg);
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-tertiary);
}
</style>
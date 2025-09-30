<script setup>
import { ref, defineEmits } from 'vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import PlusIcon from '@/components/icons/PlusIcon.vue';
import ViewGridIcon from '@/components/icons/ViewGridIcon.vue';
import ViewListIcon from '@/components/icons/ViewListIcon.vue';

const emit = defineEmits(['update:layout']);
const currentLayout = ref('grid');

function setLayout(layout) {
  if (currentLayout.value === layout) return;
  currentLayout.value = layout;
  emit('update:layout', layout);
}
</script>

<template>
  <div class="playbook-controls">
    <router-link :to="{ name: 'create-playbook' }" custom v-slot="{ navigate }">
      <BaseButton variant="primary" @click="navigate">
        <PlusIcon />
        <span>Create New Playbook</span>
      </BaseButton>
    </router-link>

    <div class="layout-switchers">
      <BaseButton
        :variant="currentLayout === 'grid' ? 'primary' : 'secondary'"
        @click="setLayout('grid')"
        aria-label="Grid Layout"
      >
        <ViewGridIcon />
      </BaseButton>
      <BaseButton
        :variant="currentLayout === 'list' ? 'primary' : 'secondary'"
        @click="setLayout('list')"
        aria-label="List Layout"
      >
        <ViewListIcon />
      </BaseButton>
    </div>
  </div>
</template>

<style scoped>
.playbook-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.layout-switchers {
  display: flex;
  gap: var(--semantic-size-stack-xs);
}

/* Hide layout switchers on smaller screens, matching user requirements */
@media (max-width: 1024px) {
  .layout-switchers {
    display: none;
  }
}
</style>
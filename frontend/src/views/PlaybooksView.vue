<template>
  <div class="playbooks-view">
    <PlaybookControls @update:layout="updateLayout" />
    <PlaybookList :playbooks="playbookStore.allPlaybooks" :layout="layout" :is-loading="playbookStore.isLoading" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { usePlaybookStore } from '@/stores/playbookStore';
import PlaybookControls from '@/components/Playbooks/PlaybookControls.vue';
import PlaybookList from '@/components/Playbooks/PlaybookList.vue';

const playbookStore = usePlaybookStore();

// Layout state, 'grid' is the default
const layout = ref('grid');

function updateLayout(newLayout) {
  layout.value = newLayout;
}

// Fetch playbooks when the component is mounted
onMounted(() => {
  playbookStore.fetchPlaybooks();
});
</script>

<style scoped>
.playbooks-view {
  display: flex;
  flex-direction: column;
  gap: 1rem; /* Spacing between controls and list */
}
</style>
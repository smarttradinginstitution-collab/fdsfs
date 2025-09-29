<template>
  <div class="playbooks-view">
    <PlaybookControls @update:layout="updateLayout" @create="isModalOpen = true" />
    <PlaybookList :playbooks="playbookStore.allPlaybooks" :layout="layout" :is-loading="playbookStore.isLoading" />
    <CreatePlaybookModal v-if="isModalOpen" @close="isModalOpen = false" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { usePlaybookStore } from '@/stores/playbookStore';
import PlaybookControls from '@/components/Playbooks/PlaybookControls.vue';
import PlaybookList from '@/components/Playbooks/PlaybookList.vue';
import CreatePlaybookModal from '@/components/Playbooks/CreatePlaybookModal.vue';

const playbookStore = usePlaybookStore();

const isModalOpen = ref(false);
const layout = ref('grid');

function updateLayout(newLayout) {
  layout.value = newLayout;
}

onMounted(() => {
  playbookStore.fetchPlaybooks();
});
</script>

<style scoped>
.playbooks-view {
  width: 100%;
  padding: var(--semantic-size-inset-xl);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-lg);
}
</style>
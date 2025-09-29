<template>
  <div class="playbooks-view">
    <PlaybookControls @update:layout="updateLayout" @create="toggleModal(true)" />
    <PlaybookList :playbooks="playbookStore.allPlaybooks" :layout="layout" :is-loading="playbookStore.isLoading" />
    <CreatePlaybookModal v-if="isModalOpen" @close="toggleModal(false)" />
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
const layout = ref('grid'); // Default layout

const toggleModal = (state) => {
  isModalOpen.value = state;
};

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
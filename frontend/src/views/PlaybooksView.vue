<template>
  <div class="playbooks-view">
    <PlaybookControls @update:layout="updateLayout" @create="isModalOpen = true" />
    <PlaybookList :playbooks="playbookStore.allPlaybooks" :layout="layout" :is-loading="playbookStore.isLoading" />
    <CreatePlaybookModal v-if="isModalOpen" @close="isModalOpen = false" @save-success="handleSaveSuccess" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { usePlaybookStore } from '@/stores/playbookStore';
import PlaybookControls from '@/components/Playbooks/PlaybookControls.vue';
import PlaybookList from '@/components/Playbooks/PlaybookList.vue';
import CreatePlaybookModal from '@/components/Playbooks/CreatePlaybookModal.vue';

const playbookStore = usePlaybookStore();
const router = useRouter();

const isModalOpen = ref(false);
const layout = ref('grid');

const handleSaveSuccess = (newPlaybook) => {
  isModalOpen.value = false;
  router.push({ name: 'playbook-detail', params: { id: newPlaybook.id } });
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
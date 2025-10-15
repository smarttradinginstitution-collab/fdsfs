<script setup>
import { computed, onMounted } from 'vue';
import { usePlaybookStore } from '@/stores/playbookStore';
import BaseModal from '@/components/ui/BaseModal.vue';
import BaseButton from '@/components/ui/BaseButton.vue';

const props = defineProps({
  show: {
    type: Boolean,
    required: true,
  },
});

const emit = defineEmits(['close', 'select']);

const playbookStore = usePlaybookStore();
const playbooks = computed(() => playbookStore.allPlaybooks);
const isLoading = computed(() => playbookStore.isLoading);

onMounted(() => {
  playbookStore.fetchPlaybooks();
});

const selectPlaybook = (playbookId) => {
  emit('select', playbookId);
};
</script>

<template>
  <BaseModal :show="show" @close="$emit('close')">
    <template #title>Select a Playbook</template>
    <div v-if="isLoading">Loading playbooks...</div>
    <div v-else>
      <ul>
        <li v-for="playbook in playbooks" :key="playbook.id" @click="selectPlaybook(playbook.id)">
          {{ playbook.title }}
        </li>
      </ul>
    </div>
    <template #footer>
      <BaseButton @click="$emit('close')">Cancel</BaseButton>
    </template>
  </BaseModal>
</template>

<style scoped>
ul {
  list-style-type: none;
  padding: 0;
}
li {
  padding: 0.75rem;
  cursor: pointer;
  border-bottom: 1px solid #eee;
}
li:hover {
  background-color: #f5f5f5;
}
</style>
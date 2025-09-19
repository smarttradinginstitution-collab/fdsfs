<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';
import BaseTable from '@/components/ui/BaseTable.vue';
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue';
import ConfirmationModal from '@/components/ui/ConfirmationModal.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import { useUiStore } from '@/stores/uiStore';

const users = ref([]);
const isLoading = ref(true);
const error = ref(null);
const showConfirmation = ref(false);
const userToDelete = ref(null);
const uiStore = useUiStore();

const tableHeaders = [
  { key: 'userId', text: 'SnapTrade User ID' },
  { key: 'actions', text: 'Actions' },
];

async function fetchUsers() {
  try {
    const response = await apiClient.get('/api/v1/admin/snaptrade-users');
    users.value = response.data.map(userId => ({ userId }));
  } catch (err) {
    error.value = 'Failed to fetch SnapTrade users.';
    console.error(err);
  } finally {
    isLoading.value = false;
  }
}

function openConfirmation(user) {
  userToDelete.value = user;
  showConfirmation.value = true;
}

async function handleDelete() {
  console.log('handleDelete called');
  if (!userToDelete.value) return;

  try {
    await apiClient.delete(`/api/v1/admin/snaptrade-users/${userToDelete.value.userId}`);
    users.value = users.value.filter(u => u.userId !== userToDelete.value.userId);
    uiStore.showToast({ message: 'User queued for deletion successfully.', type: 'success' });
  } catch (err) {
    uiStore.showToast({ message: 'Failed to delete user.', type: 'error' });
    console.error(err);
  } finally {
    showConfirmation.value = false;
    userToDelete.value = null;
  }
}

onMounted(fetchUsers);
</script>

<template>
  <div class="p-4 sm:p-6">
    <h1 class="text-2xl font-bold mb-4">Admin - SnapTrade Users</h1>
    <div v-if="isLoading" class="flex justify-center items-center h-64">
      <LoadingSpinner />
    </div>
    <div v-else-if="error" class="text-red-500 bg-red-100 p-4 rounded-md">
      {{ error }}
    </div>
    <div v-else>
      <BaseTable :headers="tableHeaders" :items="users">
        <template #actions="{ item }">
          <BaseButton @click="openConfirmation(item)" variant="secondary" size="small">
            Delete
          </BaseButton>
        </template>
      </BaseTable>
    </div>
    <ConfirmationModal
      :show="showConfirmation"
      title="Delete SnapTrade User"
      confirmation-word="delete"
      @close="showConfirmation = false"
      @confirm="handleDelete"
    >
      <p>Are you sure you want to delete this user? This action is irreversible.</p>
      <p class="mt-2">The user's SnapTrade secret will be cleared from the database.</p>
    </ConfirmationModal>
  </div>
</template>

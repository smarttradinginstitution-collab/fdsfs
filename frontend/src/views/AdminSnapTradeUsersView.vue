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
const uiStore = useUiStore();

// State for Delete Modal
const showDeleteConfirmation = ref(false);
const userToDelete = ref(null);

// State for Rotate Secret Modal
const showRotateConfirmation = ref(false);
const userToRotate = ref(null);

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

function openDeleteConfirmation(user) {
  userToDelete.value = user;
  showDeleteConfirmation.value = true;
}

function openRotateConfirmation(user) {
  userToRotate.value = user;
  showRotateConfirmation.value = true;
}

async function handleDelete() {
  if (!userToDelete.value) return;

  try {
    await apiClient.delete(`/api/v1/admin/snaptrade-users/${userToDelete.value.userId}`);
    users.value = users.value.filter(u => u.userId !== userToDelete.value.userId);
    uiStore.showNotification({ message: 'User queued for deletion successfully.', type: 'success' });
  } catch (err) {
    uiStore.showNotification({ message: 'Failed to delete user.', type: 'error' });
    console.error(err);
  } finally {
    showDeleteConfirmation.value = false;
    userToDelete.value = null;
  }
}

async function handleRotateSecret() {
  if (!userToRotate.value) return;

  try {
    await apiClient.post(`/api/v1/admin/snaptrade-users/${userToRotate.value.userId}/rotate-secret`);
    uiStore.showNotification({ message: 'User secret rotated successfully.', type: 'success' });
  } catch (err) {
    uiStore.showNotification({ message: 'Failed to rotate secret.', type: 'error' });
    console.error(err);
  } finally {
    showRotateConfirmation.value = false;
    userToRotate.value = null;
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
          <div class="flex space-x-2">
            <BaseButton @click="openRotateConfirmation(item)" variant="secondary" size="small">
              Rotate Secret
            </BaseButton>
            <BaseButton @click="openDeleteConfirmation(item)" variant="danger" size="small">
              Delete
            </BaseButton>
          </div>
        </template>
      </BaseTable>
    </div>

    <!-- Delete Confirmation Modal -->
    <ConfirmationModal
      :show="showDeleteConfirmation"
      title="Delete SnapTrade User"
      confirmation-word="delete"
      @close="showDeleteConfirmation = false"
      @confirm="handleDelete"
    >
      <p>Are you sure you want to delete this user? This action is irreversible.</p>
      <p class="mt-2">The user's SnapTrade secret will be cleared from the database.</p>
    </ConfirmationModal>

    <!-- Rotate Secret Confirmation Modal -->
    <ConfirmationModal
      :show="showRotateConfirmation"
      title="Rotate SnapTrade User Secret"
      confirmation-word="rotate"
      @close="showRotateConfirmation = false"
      @confirm="handleRotateSecret"
    >
      <p>Are you sure you want to rotate this user's secret? This action is irreversible.</p>
      <p class="mt-2">The user will need to be provided with the new secret to access their account.</p>
    </ConfirmationModal>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { usePlaybookStore } from '@/stores/playbookStore';
import BaseWidget from '@/components/layout/BaseWidget.vue';
import IconButton from '@/components/ui/IconButton.vue';
import CloseIcon from '@/components/icons/CloseIcon.vue';
import Stepper from '@/components/ui/Stepper.vue';
import ColorSelector from '@/components/ui/ColorSelector.vue';
import IconSelector from '@/components/ui/IconSelector.vue';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';

const router = useRouter();
const playbookStore = usePlaybookStore();

// Form state
const playbookData = ref({
  title: '',
  description: '',
  color: '#4A90E2', // Default color
  icon_name: 'BuildingLibraryIcon', // Default icon
  private: false,
});
const isLoading = ref(false);
const error = ref(null);

const currentStep = ref(0);
const steps = ['Setup', 'Rules'];

const closeModal = () => {
  router.push({ name: 'playbooks' });
};

const goToNextStep = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    // Call the store action to create the playbook
    const newPlaybook = await playbookStore.createPlaybook(playbookData.value);
    // On success, navigate to the detail page of the new playbook
    router.push({ name: 'playbook-detail', params: { id: newPlaybook.id } });
  } catch (err) {
    console.error("Failed to create playbook:", err);
    error.value = playbookStore.error || 'An unknown error occurred.';
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="create-playbook-overlay" @click.self="closeModal">
    <div class="create-playbook-modal">
      <BaseWidget>
        <template #header>
          <div class="modal-header">
            <div class="header-placeholder"></div>
            <IconButton @click="closeModal" aria-label="Close" :disabled="isLoading">
              <CloseIcon />
            </IconButton>
          </div>
        </template>
        <div class="modal-content">
          <Stepper :steps="steps" :current-step="currentStep" />

          <div class="form-section">
            <h3 class="section-title">Color</h3>
            <ColorSelector v-model="playbookData.color" />
          </div>

          <div class="form-section">
            <h3 class="section-title">Icon</h3>
            <IconSelector v-model="playbookData.icon_name" />
          </div>

          <div class="form-section">
            <BaseInput
              v-model="playbookData.title"
              label="Playbook Name"
              placeholder="e.g., 'Opening Range Breakout'"
              id="playbook-title"
              :disabled="isLoading"
            />
          </div>

          <div class="form-section">
             <BaseInput
              v-model="playbookData.description"
              label="Description"
              placeholder="Describe the strategy, entry/exit criteria, etc."
              id="playbook-description"
              type="textarea"
              :rows="4"
              :disabled="isLoading"
            />
          </div>

          <div v-if="error" class="error-message">{{ error }}</div>

          <div class="form-actions">
            <BaseButton variant="secondary" @click="closeModal" :disabled="isLoading">Cancel</BaseButton>
            <BaseButton variant="primary" @click="goToNextStep" :is-loading="isLoading">Next</BaseButton>
          </div>
        </div>
      </BaseWidget>
    </div>
  </div>
</template>

<style scoped>
.create-playbook-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: var(--semantic-size-stack-lg);
}

.create-playbook-modal {
  width: 100%;
  max-width: 600px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.header-placeholder {
  flex-grow: 1;
}

.modal-content {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-lg);
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-sm);
}

.section-title {
  font: var(--semantic-font-style-body-lg-bold);
  color: var(--semantic-color-text-primary);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--semantic-size-stack-md);
  border-top: 1px solid var(--semantic-color-border-default);
  padding-top: var(--semantic-size-stack-lg);
  margin-top: var(--semantic-size-stack-md);
}

.error-message {
  color: var(--semantic-color-text-danger);
  background-color: var(--semantic-color-surface-danger-subtle);
  border: 1px solid var(--semantic-color-border-danger);
  padding: var(--semantic-size-inset-md);
  border-radius: var(--semantic-border-radius-surface);
  text-align: center;
}
</style>
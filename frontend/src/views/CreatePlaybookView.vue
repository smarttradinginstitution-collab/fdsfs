<script setup>
import { ref, computed } from 'vue';
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
  color: '#4A90E2',
  icon_name: 'BuildingLibraryIcon',
  private: false,
});
const isLoading = ref(false);
const error = ref(null);

const currentStep = ref(0);
const steps = [
  { title: 'Setup', description: 'Personalize your playbook' },
  { title: 'Rules', description: 'Define your entry/exit criteria' },
];

const isLastStep = computed(() => currentStep.value === steps.length - 1);

const closeModal = () => {
  router.push({ name: 'playbooks' });
};

const handleNext = () => {
  if (isLastStep.value) {
    submitPlaybook();
  } else {
    currentStep.value++;
  }
};

const submitPlaybook = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const newPlaybook = await playbookStore.createPlaybook(playbookData.value);
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

          <!-- Step 1: Setup -->
          <div v-if="currentStep === 0" class="form-content">
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
          </div>

          <!-- Step 2: Rules (Placeholder) -->
          <div v-if="currentStep === 1" class="form-content">
            <div class="placeholder-content">
              <p>Rule configuration will be available in a future update.</p>
            </div>
          </div>


          <div v-if="error" class="error-message">{{ error }}</div>

          <div class="form-actions">
            <BaseButton variant="secondary" @click="closeModal" :disabled="isLoading">Cancel</BaseButton>
            <BaseButton variant="primary" @click="handleNext" :is-loading="isLoading">
              {{ isLastStep ? 'Finish' : 'Next' }}
            </BaseButton>
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

.form-content {
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

.placeholder-content {
    text-align: center;
    padding: var(--semantic-size-inset-xl);
    color: var(--semantic-color-text-secondary);
    min-height: 200px;
    display: flex;
    align-items: center;
    justify-content: center;
}
</style>
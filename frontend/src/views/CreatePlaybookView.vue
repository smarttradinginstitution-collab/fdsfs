<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { usePlaybookStore } from '@/stores/playbookStore';
import { useUiStore } from '@/stores/uiStore';
import BaseWidget from '@/components/layout/BaseWidget.vue';
import ColorSelector from '@/components/ui/ColorSelector.vue';
import IconSelector from '@/components/ui/IconSelector.vue';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';

const router = useRouter();
const playbookStore = usePlaybookStore();
const uiStore = useUiStore();

const playbookData = ref({
  title: '',
  description: '',
  color: '#4A90E2',
  icon_name: 'BuildingLibraryIcon',
  private: false,
});
const error = ref(null);

const cancelCreation = () => {
  router.push('/playbooks');
};

const submitPlaybook = async () => {
  uiStore.showLoader();
  error.value = null;
  try {
    const newPlaybook = await playbookStore.createPlaybook(playbookData.value);
    // Redirect to the new edit view for the created playbook
    router.push({ name: 'edit-playbook', params: { id: newPlaybook.id } });
  } catch (err) {
    console.error("Failed to create playbook:", err);
    error.value = playbookStore.error || 'An unknown error occurred during save.';
  } finally {
    uiStore.hideLoader();
  }
};
</script>

<template>
  <div class="create-playbook-view">
    <div class="create-playbook-container">
      <BaseWidget>
        <template #header>
          <div class="page-header">
            <h2 class="page-title">Create New Playbook</h2>
          </div>
        </template>
        <div class="page-content">
          <div class="form-content">
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
                :disabled="uiStore.isAppLoading"
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
                :disabled="uiStore.isAppLoading"
              />
            </div>
          </div>

          <div v-if="error" class="error-message">{{ error }}</div>

          <div class="form-actions">
            <BaseButton variant="secondary" @click="cancelCreation" :disabled="uiStore.isAppLoading">Cancel</BaseButton>
            <BaseButton variant="primary" @click="submitPlaybook" :is-loading="uiStore.isAppLoading">
              Create and Continue
            </BaseButton>
          </div>
        </div>
      </BaseWidget>
    </div>
  </div>
</template>

<style scoped>
.create-playbook-view {
  width: 100%;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: var(--semantic-size-inset-xl);
  background-color: var(--semantic-color-surface-primary);
}

.create-playbook-container {
  width: 100%;
  max-width: 600px;
}

.page-header {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
}

.page-title {
  font: var(--semantic-font-style-headline-lg);
}

.page-content {
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
</style>

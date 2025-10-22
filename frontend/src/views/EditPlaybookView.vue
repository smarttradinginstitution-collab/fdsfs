<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { usePlaybookStore } from '@/stores/playbookStore';
import { useUiStore } from '@/stores/uiStore';
import BaseWidget from '@/components/layout/BaseWidget.vue';
import IconButton from '@/components/ui/IconButton.vue';
import ArrowLeftIcon from '@/components/icons/ArrowLeftIcon.vue';
import Stepper from '@/components/ui/Stepper.vue';
import ColorSelector from '@/components/ui/ColorSelector.vue';
import IconSelector from '@/components/ui/IconSelector.vue';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import RuleGroupManager from '@/components/Playbooks/RuleGroupManager.vue';

const router = useRouter();
const route = useRoute();
const playbookStore = usePlaybookStore();
const uiStore = useUiStore();
const ruleGroupManagerRef = ref(null);

const playbookId = ref(null);
const pageTitle = 'Edit Playbook';

const playbookData = ref({
  title: '',
  description: '',
  color: '#4A90E2',
  icon_name: 'BuildingLibraryIcon',
  private: false,
});
const error = ref(null);

onMounted(async () => {
  playbookId.value = route.params.id;
  try {
    const existingPlaybook = await playbookStore.fetchPlaybookDetails(playbookId.value);
    playbookData.value = { ...existingPlaybook };
  } catch (err) {
    console.error('Failed to fetch playbook details, redirecting.', err);
    router.push('/playbooks');
  }
});

const currentStep = ref(0);
const steps = [
  { title: 'Setup', description: 'Personalize your playbook' },
  { title: 'Rules', description: 'Define your entry/exit criteria' },
];

const isLastStep = computed(() => currentStep.value === steps.length - 1);

const cancelEdit = () => {
  router.push('/playbooks');
};

const goBack = () => {
  if (currentStep.value > 0) {
    currentStep.value--;
  }
};

const handleNext = () => {
  if (isLastStep.value) {
    submitPlaybookUpdate();
  } else {
    currentStep.value++;
  }
};

const submitPlaybookUpdate = async () => {
  if (!ruleGroupManagerRef.value?.ruleGroups) {
    error.value = "Could not find rule groups data.";
    return;
  }

  uiStore.showLoader();
  error.value = null;
  try {
    const ruleGroups = ruleGroupManagerRef.value.ruleGroups;
    await playbookStore.updatePlaybook(playbookId.value, playbookData.value, ruleGroups);
    router.push({ name: 'playbook-detail', params: { id: playbookId.value } });
  } catch (err) {
    console.error("Failed to update playbook with rules:", err);
    error.value = playbookStore.error || 'An unknown error occurred during save.';
  } finally {
    uiStore.hideLoader();
  }
};
</script>

<template>
  <div class="edit-playbook-view">
    <div class="edit-playbook-container">
      <BaseWidget>
        <template #header>
          <div class="page-header">
            <div class="header-left-controls">
              <IconButton v-if="currentStep > 0" @click="goBack" aria-label="Go back" :disabled="uiStore.isAppLoading">
                <ArrowLeftIcon />
              </IconButton>
            </div>
            <h2 class="page-title">{{ pageTitle }}</h2>
          </div>
        </template>
        <div class="page-content">
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

          <!-- Step 2: Rules -->
          <div v-if="currentStep === 1" class="form-content">
            <RuleGroupManager ref="ruleGroupManagerRef" :playbook-id="playbookId" />
          </div>

          <div v-if="error" class="error-message">{{ error }}</div>

          <div class="form-actions">
            <BaseButton variant="secondary" @click="cancelEdit" :disabled="uiStore.isAppLoading">Cancel</BaseButton>
            <BaseButton variant="primary" @click="handleNext" :is-loading="uiStore.isAppLoading">
              {{ isLastStep ? 'Update' : 'Next' }}
            </BaseButton>
          </div>
        </div>
      </BaseWidget>
    </div>
  </div>
</template>

<style scoped>
.edit-playbook-view {
  width: 100%;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: var(--semantic-size-inset-xl);
  background-color: var(--semantic-color-surface-primary);
}

.edit-playbook-container {
  width: 100%;
  max-width: 600px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.header-left-controls {
  min-width: 36px;
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

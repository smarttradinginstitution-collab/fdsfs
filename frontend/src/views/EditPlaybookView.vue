<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { storeToRefs } from 'pinia';
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

const router = useRouter();
const route = useRoute();
const playbookStore = usePlaybookStore();
const uiStore = useUiStore();

const pageTitle = 'Edit Playbook';

const playbookData = ref(null);
const error = ref(null);
const playbookId = ref(null);

const addNewBlock = async (blockType) => {
  if (!playbookId.value) return;

  // Determine the order for the new block
  const maxOrder = playbookData.value.blocks.reduce((max, block) => Math.max(max, block.order), -1);
  const newOrder = maxOrder + 1;

  // Define default content based on block type
  let defaultContent = {};
  if (blockType === 'THESIS') {
    defaultContent = { text: 'New thesis block...' };
  } else if (blockType === 'CONDITIONS') {
    // Conditions are managed separately, no content needed in the block itself
    defaultContent = {};
  } else if (blockType === 'GALLERY') {
    defaultContent = { images: [] };
  }

  try {
    await playbookStore.createBlockForPlaybook({
      playbookId: playbookId.value,
      blockType: blockType,
      content: defaultContent,
      order: newOrder,
    });
    // The store should reactively update the component, but if not,
    // we might need to refetch the playbook data. For now, we rely on the store's reactivity.
  } catch (err) {
    error.value = 'Failed to add the new block. Please try again.';
    console.error("Error adding new block:", err);
  }
};

// Import block components
import ThesisBlock from '@/components/Playbooks/ThesisBlock.vue';
import GalleryBlock from '@/components/Playbooks/GalleryBlock.vue';
import ConditionsBlock from '@/components/Playbooks/ConditionsBlock.vue';
import PsychologyBlock from '@/components/Playbooks/PsychologyBlock.vue';
import LegacyRulesBlock from '@/components/Playbooks/LegacyRulesBlock.vue';

const blockComponentMap = {
  THESIS: ThesisBlock,
  GALLERY: GalleryBlock,
  CONDITIONS: ConditionsBlock,
  PSYCHOLOGY: PsychologyBlock,
  LEGACY_RULES: LegacyRulesBlock,
};

onMounted(async () => {
  const id = route.params.id;
  playbookId.value = id;
  try {
    const data = await playbookStore.fetchPlaybookDetails(id);
    playbookData.value = data; // This will include blocks and conditions
  } catch (err) {
    console.error('Failed to fetch playbook data, redirecting.', err);
    router.push('/playbooks');
  }
});

const cancelEdit = () => {
  router.push('/playbooks');
};

const submitPlaybookUpdate = async () => {
  uiStore.showLoader();
  error.value = null;
  try {
    // This is a simplified update. A more robust implementation would
    // separate the updates for playbook details, blocks, and conditions.
    await playbookStore.updatePlaybook(playbookId.value, playbookData.value);
    router.push({ name: 'playbook-detail', params: { id: playbookId.value } });
  } catch (err) {
    console.error("Failed to update playbook:", err);
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
            <h2 class="page-title">{{ pageTitle }}</h2>
          </div>
        </template>
        <div v-if="playbookData" class="page-content">
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

            <!-- Dynamic Block Rendering -->
            <div class="form-section">
              <h3 class="section-title">Playbook Content</h3>
              <div v-if="playbookData.blocks && playbookData.blocks.length > 0">
                <div v-for="(block, index) in playbookData.blocks" :key="index" class="playbook-block">
                  <component
                    :is="blockComponentMap[block.block_type]"
                    :content="block.content"
                    :conditions="playbookData.conditions"
                    @update:content="block.content = $event"
                  />
                </div>
              </div>
               <div v-else class="no-blocks-message">
                This playbook has no content. Add a block to get started.
              </div>
            </div>

             <!-- Add New Block Controls -->
            <div class="form-section">
                <h3 class="section-title">Add New Block</h3>
                <div class="add-block-controls">
                    <BaseButton @click="addNewBlock('THESIS')" variant="secondary">Add Thesis</BaseButton>
                    <BaseButton @click="addNewBlock('CONDITIONS')" variant="secondary">Add Conditions</BaseButton>
                    <BaseButton @click="addNewBlock('GALLERY')" variant="secondary">Add Gallery</BaseButton>
                </div>
            </div>
          </div>

          <div v-if="error" class="error-message">{{ error }}</div>

          <div class="form-actions">
            <BaseButton variant="secondary" @click="cancelEdit" :disabled="uiStore.isAppLoading">Cancel</BaseButton>
            <BaseButton variant="primary" @click="submitPlaybookUpdate" :is-loading="uiStore.isAppLoading">
              Update Playbook
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

.playbook-block {
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-surface);
  padding: var(--semantic-size-inset-md);
  margin-bottom: var(--semantic-size-stack-md);
}

.no-blocks-message {
  color: var(--semantic-color-text-subtle);
  padding: var(--semantic-size-inset-lg);
  text-align: center;
  border: 2px dashed var(--semantic-color-border-subtle);
  border-radius: var(--semantic-border-radius-surface);
}

.add-block-controls {
  display: flex;
  gap: var(--semantic-size-stack-md);
  justify-content: center;
  padding-top: var(--semantic-size-stack-sm);
}
</style>

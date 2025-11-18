
<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { usePlaybookStore } from '@/stores/playbookStore';
import { useUiStore } from '@/stores/uiStore';
import BaseWidget from '@/components/layout/BaseWidget.vue';
import ColorSelector from '@/components/ui/ColorSelector.vue';
import IconSelector from '@/components/ui/IconSelector.vue';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import SmartBlock from '@/components/Playbooks/SmartBlock.vue';
import AddBlockModal from '@/components/Playbooks/AddBlockModal.vue';

const router = useRouter();
const route = useRoute();
const playbookStore = usePlaybookStore();
const uiStore = useUiStore();

const playbookData = ref(null);
const error = ref(null);
const playbookId = computed(() => route.params.id);

onMounted(async () => {
  if (playbookId.value) {
    uiStore.showLoader();
    try {
      // Fetch fresh data. The store might be stale.
      const data = await playbookStore.fetchPlaybookDetails(playbookId.value);
      playbookData.value = data;
    } catch (err) {
      console.error('Failed to fetch playbook data, redirecting.', err);
      router.push('/playbooks');
    } finally {
      uiStore.hideLoader();
    }
  }
});

const isModalVisible = ref(false);

const handleCreateBlock = async (blockData) => {
  isModalVisible.value = false;
  if (playbookId.value) {
    uiStore.showLoader();
    try {
      let defaultContent = {};
      if (blockData.block_type === 'CONDITIONS') {
        defaultContent = { groups: [] };
      } else if (blockData.block_type === 'THESIS') {
        defaultContent = { html: "<p>Write your thesis here...</p>" };
      } else if (blockData.block_type === 'GALLERY') {
        defaultContent = { images: [] };
      }

      await playbookStore.createBlockForPlaybook({
        playbookId: playbookId.value,
        ...blockData,
        content: defaultContent,
      });

      // Refetch to get the updated list of blocks
      playbookData.value = await playbookStore.fetchPlaybookDetails(playbookId.value);
    } catch (err) {
      error.value = 'Failed to add the new block.';
      console.error("Error adding new block:", err);
    } finally {
      uiStore.hideLoader();
    }
  }
};

const handleDeleteBlock = async (blockId) => {
    if (playbookId.value && blockId) {
        uiStore.showLoader();
        try {
            await playbookStore.deleteBlock(playbookId.value, blockId);
            // Refetch to update the UI
            playbookData.value = await playbookStore.fetchPlaybookDetails(playbookId.value);
        } catch (err) {
            error.value = 'Failed to delete the block.';
            console.error("Error deleting block:", err);
        } finally {
            uiStore.hideLoader();
        }
    }
};

const savePlaybookDetails = async () => {
  uiStore.showLoader();
  error.value = null;
  try {
    const { blocks, ...detailsToUpdate } = playbookData.value;
    await playbookStore.updatePlaybook(playbookId.value, detailsToUpdate);
    // Optionally show a success message
  } catch (err) {
    error.value = 'Failed to save playbook details.';
    console.error("Failed to update playbook:", err);
  } finally {
    uiStore.hideLoader();
  }
};
</script>

<template>
  <div class="edit-playbook-view">
    <div class="edit-playbook-container">
      <BaseWidget v-if="playbookData">
        <template #header>
          <div class="page-header">
            <h2 class="page-title">Edit Playbook</h2>
          </div>
        </template>
        <div class="page-content">
          <div class="form-content">
            <!-- Playbook Details Section -->
            <div class="form-section">
                <h3 class="section-title">Playbook Details</h3>
                <div class="details-grid">
                    <BaseInput v-model="playbookData.title" label="Playbook Name" id="playbook-title" @blur="savePlaybookDetails" />
                    <BaseInput v-model="playbookData.description" label="Description" id="playbook-description" type="textarea" :rows="3" @blur="savePlaybookDetails"/>
                    <div>
                        <h4 class="input-label">Color</h4>
                        <ColorSelector v-model="playbookData.color" @update:modelValue="savePlaybookDetails" />
                    </div>
                    <div>
                        <h4 class="input-label">Icon</h4>
                        <IconSelector v-model="playbookData.icon_name" @update:modelValue="savePlaybookDetails" />
                    </div>
                </div>
            </div>

            <!-- Blocks Section -->
            <div class="form-section">
              <h3 class="section-title">Playbook Content</h3>
              <div v-if="playbookData.blocks && playbookData.blocks.length > 0">
                <SmartBlock
                    v-for="block in playbookData.blocks"
                    :key="block.id"
                    :block="block"
                    @delete-block="handleDeleteBlock"
                />
              </div>
              <div v-else class="no-blocks-message">
                This playbook has no content. Add a block to get started.
              </div>
            </div>

            <div class="add-block-section">
                <BaseButton @click="isModalVisible = true" variant="primary" size="lg">
                    + Add New Content Block
                </BaseButton>
            </div>
          </div>

          <div v-if="error" class="error-message">{{ error }}</div>
        </div>
      </BaseWidget>
    </div>

    <AddBlockModal
      v-if="isModalVisible"
      @close="isModalVisible = false"
      @create-block="handleCreateBlock"
    />
  </div>
</template>

<style scoped>
.edit-playbook-view {
  width: 100%;
  padding: var(--semantic-size-inset-xl);
  background-color: var(--semantic-color-surface-primary);
}
.edit-playbook-container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}
.page-header {
  text-align: center;
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
  gap: var(--semantic-size-stack-xl);
}
.form-section {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
}
.section-title {
  font: var(--semantic-font-style-headline-xs);
  color: var(--semantic-color-text-primary);
  border-bottom: 1px solid var(--semantic-color-border-subtle);
  padding-bottom: var(--semantic-size-stack-sm);
}
.details-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--semantic-size-stack-md);
}
.details-grid > *:nth-child(2) { /* Description */
    grid-column: 1 / -1;
}
.input-label {
    font: var(--semantic-font-style-body-md-bold);
    margin-bottom: var(--semantic-size-stack-xs);
}
.no-blocks-message {
  color: var(--semantic-color-text-subtle);
  padding: var(--semantic-size-inset-xl);
  text-align: center;
  border: 2px dashed var(--semantic-color-border-subtle);
  border-radius: var(--semantic-border-radius-surface);
}
.add-block-section {
    text-align: center;
    padding: var(--semantic-size-stack-md) 0;
    border-top: 1px solid var(--semantic-color-border-subtle);
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


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
import ImageLightbox from '@/components/ui/ImageLightbox.vue';

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

// --- Lightbox State & Methods ---
const isLightboxOpen = ref(false);
const lightboxImages = ref([]);
const lightboxCurrentIndex = ref(0);

const openLightbox = ({ images, startIndex }) => {
  lightboxImages.value = images;
  lightboxCurrentIndex.value = startIndex;
  isLightboxOpen.value = true;
};

const closeLightbox = () => {
  isLightboxOpen.value = false;
};

const nextImage = () => {
  lightboxCurrentIndex.value = (lightboxCurrentIndex.value + 1) % lightboxImages.value.length;
};

const prevImage = () => {
  lightboxCurrentIndex.value = (lightboxCurrentIndex.value - 1 + lightboxImages.value.length) % lightboxImages.value.length;
};

const handleCreateBlock = async (blockData) => {
  isModalVisible.value = false;
  if (playbookId.value) {
    uiStore.showLoader();
    try {
      let defaultContent = {};
      if (blockData.block_type === 'RULES') {
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

const handleUpdateBlock = async (blockUpdateData) => {
    if (playbookId.value && blockUpdateData.id) {
        uiStore.showLoader();
        try {
            await playbookStore.updateBlock(playbookId.value, blockUpdateData.id, blockUpdateData);
            // Optionally, instead of a full refetch, you could update the local data.
            // For simplicity and consistency with other methods here, we refetch.
            playbookData.value = await playbookStore.fetchPlaybookDetails(playbookId.value);
        } catch (err) {
            error.value = 'Failed to update the block.';
            console.error("Error updating block:", err);
        } finally {
            uiStore.hideLoader();
        }
    }
};

const getBlockDisplayName = (blockType) => {
  const names = {
    THESIS: 'Model Explanation',
    RULES: 'Model Rules & Conditions',
    GALLERY: 'Model Gallery',
  };
  return names[blockType] || 'Content Block';
};

const groupedBlocks = computed(() => {
  if (!playbookData.value || !playbookData.value.blocks) {
    return [];
  }

  const groups = {
    THESIS: [],
    RULES: [],
    GALLERY: [],
  };

  playbookData.value.blocks.forEach(block => {
    if (groups[block.block_type]) {
      groups[block.block_type].push(block);
    }
  });

  const groupOrder = ['THESIS', 'RULES', 'GALLERY'];

  return groupOrder
    .map(blockType => ({
      blockType,
      displayName: getBlockDisplayName(blockType),
      blocks: groups[blockType],
    }))
    .filter(group => group.blocks.length > 0);
});

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
            <div class="playbook-header-section">
              <div class="title-input-group">
                <label for="playbookTitle" class="input-label">Nome Playbook</label>
                <BaseInput
                  id="playbookTitle"
                  v-model="playbookData.title"
                  @blur="savePlaybookDetails"
                  placeholder="Enter Playbook Title"
                />
              </div>
              <div class="meta-tags">
                  <ColorSelector v-model="playbookData.color" @update:modelValue="savePlaybookDetails" />
                  <IconSelector v-model="playbookData.icon_name" @update:modelValue="savePlaybookDetails" />
              </div>
            </div>

            <!-- Blocks Section -->
            <div class="form-section">
              <h3 class="section-title">Playbook Content</h3>
              <div v-if="groupedBlocks.length > 0">
                <div v-for="group in groupedBlocks" :key="group.blockType" class="block-group">
                  <h4 class="block-category-title">{{ group.displayName }}</h4>
                  <div class="blocks-container">
                    <div v-for="block in group.blocks" :key="block.id" class="block-wrapper">
                      <SmartBlock
                        :block="block"
                        @delete-block="handleDeleteBlock"
                        @update-block="handleUpdateBlock"
                        @open-lightbox="openLightbox"
                      />
                    </div>
                  </div>
                </div>
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

    <ImageLightbox
      v-if="isLightboxOpen"
      :images="lightboxImages"
      :current-index="lightboxCurrentIndex"
      :show="isLightboxOpen"
      @close="closeLightbox"
      @next="nextImage"
      @prev="prevImage"
    />
  </div>
</template>

<style scoped>
/* Global styles for the new design */
:deep(.input-ghost) {
    background: transparent;
    border: none;
    outline: none;
    padding: 0;
    font-size: inherit;
    font-weight: inherit;
    color: inherit;
    width: 100%;
}
:deep(.input-ghost:focus) {
    background-color: var(--semantic-color-surface-subtle);
}

.edit-playbook-view {
  width: 100%;
  min-height: 100vh;
  padding: var(--semantic-size-inset-xl);
  background-color: #0F1115; /* Dark page background */
  color: var(--semantic-color-text-primary);
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
.playbook-header-section {
    padding-bottom: var(--semantic-size-stack-lg);
    border-bottom: 1px solid var(--semantic-color-border-subtle);
}
.title-input-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem; /* 8px */
}
.input-label {
  font-size: 0.875rem; /* 14px */
  font-weight: 500;
  color: var(--semantic-color-text-secondary);
}
.playbook-description-input {
    font: var(--semantic-font-style-body-lg);
    color: var(--semantic-color-text-secondary);
    margin-top: var(--semantic-size-stack-xs);
    resize: none;
}
.meta-tags {
    display: flex;
    align-items: center;
    gap: var(--semantic-size-inline-md);
    margin-top: var(--semantic-size-stack-md);
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
.block-group {
  margin-bottom: 2.5rem; /* 40px */
}
.blocks-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem; /* 24px */
  margin-top: 1rem;
}
.block-wrapper {
  /* No margin needed here now, gap handles it */
}
.block-category-title {
  font-size: 12px;
  font-weight: 600;
  color: #8A91A0;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 1rem;
}
.section-title {
  font: var(--semantic-font-style-headline-xs);
  color: var(--semantic-color-text-primary);
  border-bottom: 1px solid var(--semantic-color-border-subtle);
  padding-bottom: var(--semantic-size-stack-sm);
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

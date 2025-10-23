<template>
  <div class="trade-note-editor-widget">
    <BaseWidget>
      <template #header>
        <span>Trade Note</span>
      </template>
      <div v-if="isLoading" class="loading-state">
        <p>Loading Note...</p>
      </div>
      <div v-else-if="note">
        <NoteEditor
          :key="note.id"
          :show-financial-data="false"
          :show-trade-details-link="false"
        />
      </div>
      <div v-else class="empty-state">
        <p>No note found for this trade.</p>
        <BaseButton @click="createNoteForTrade" :is-loading="isCreating">
          Create Note for this Trade
        </BaseButton>
      </div>
    </BaseWidget>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useNotebookStore } from '../../stores/notebookStore';
import BaseWidget from '../layout/BaseWidget.vue';
import BaseButton from '../ui/BaseButton.vue';
import NoteEditor from '../notebook/NoteEditor.vue';

const props = defineProps({
  tradeId: {
    type: String,
    required: true,
  },
  tradeDetails: {
    type: Object,
    required: true,
  },
  // La nota viene ora passata direttamente come prop
  note: {
    type: Object,
    default: null,
  },
  isLoading: {
    type: Boolean,
    default: false,
  },
});

const store = useNotebookStore();
const isCreating = ref(false);

const createNoteForTrade = async () => {
  isCreating.value = true;
  try {
    const tradeDate = new Date(props.tradeDetails.entry_timestamp).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
    const symbol = props.tradeDetails.asset?.symbol ?? 'N/A';
    const title = `${symbol} : ${tradeDate}`;

    let tradeNotesFolder = store.folders.find(f => f.system_folder_identifier === 'TRADE_NOTES');
    if (!tradeNotesFolder) {
      await store.fetchFolders();
      tradeNotesFolder = store.folders.find(f => f.system_folder_identifier === 'TRADE_NOTES');
      if (!tradeNotesFolder) {
        throw new Error("Critical: Trade Notes system folder not found.");
      }
    }

    await store.createTradeNote({
      folderId: tradeNotesFolder.id,
      title,
      tradeId: props.tradeId,
    });

  } catch (error) {
    console.error("Error creating note for trade:", error);
  } finally {
    isCreating.value = false;
  }
};
</script>

<style lang="scss" scoped>
.loading-state, .empty-state {
  padding: var(--semantic-size-inset-xl);
  text-align: center;
  color: var(--semantic-color-text-secondary);

  p {
    margin-bottom: var(--semantic-size-inset-md);
  }
}
</style>
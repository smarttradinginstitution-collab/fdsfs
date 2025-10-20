<template>
  <div class="trade-note-editor-widget">
    <BaseWidget>
      <template #header>
        <span>Trade Note</span>
      </template>
      <div v-if="currentNote">
        <NoteEditor
          :key="currentNote.id"
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
import { ref, watch, computed } from 'vue';
import { useNotebookStore } from '../../stores/notebookStore';
import BaseWidget from '../layout/BaseWidget.vue';
import BaseButton from '../ui/BaseButton.vue';
import NoteEditor from '../notebook/NoteEditor.vue';

const props = defineProps({
  initialNote: {
    type: Object,
    default: null,
  },
  tradeDetails: {
    type: Object,
    required: true,
  }
});

const store = useNotebookStore();
const isCreating = ref(false);

// The presence of a note is now determined by the prop or if one is selected in the store
// This handles the case where a new note is created and now exists in the store
const currentNote = computed(() => props.initialNote || store.selectedNote);

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

watch(() => props.tradeDetails.id, async (newTradeId, oldTradeId) => {
  if (newTradeId !== oldTradeId) {
    // A new trade is being viewed, so we rely on the parent to pass the new note.
    // The logic inside `selectTradeFromStore` in the parent handles fetching and updating the note.
    if (props.initialNote) {
      store.selectNote(props.initialNote.id);
    } else {
      // If the new trade has no note, deselect the previous one.
      store.deselectNote();
    }
  }
}, { immediate: true });

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
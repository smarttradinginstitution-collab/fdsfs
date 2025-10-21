<template>
  <div class="trade-note-editor-widget">
    <BaseWidget>
      <template #header>
        <span>Trade Note</span>
      </template>
      <!-- The v-if="note" check is now the primary determinant -->
      <div v-if="note">
        <NoteEditor
          :key="note.id"
          :initial-note="note"
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
import { ref, watch, onMounted } from 'vue';
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
  // The note object is now passed as a prop
  note: {
    type: Object,
    default: null,
  }
});

const store = useNotebookStore();
const isCreating = ref(false);

// The logic to create a note remains, as it's an action initiated by the user
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

    // Note: After creating, the parent view (`ReportView`) will receive the updated
    // trade object via the store and pass the new note down as a prop,
    // triggering a re-render automatically.

  } catch (error) {
    console.error("Error creating note for trade:", error);
  } finally {
    isCreating.value = false;
  }
};

// When the note prop changes, we need to inform the store so the editor can react
watch(() => props.note, (newNote) => {
  if (newNote) {
    store.selectNote(newNote.id, newNote);
  } else {
    // If the note is null (e.g., navigating to a trade with no note), deselect it
    store.deselectNote();
  }
}, { immediate: true }); // `immediate: true` ensures this runs on initial component load

// We still need to ensure folders are available for the "Create Note" functionality
onMounted(async () => {
  if (store.folders.length === 0) {
    await store.fetchFolders();
  }
});

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
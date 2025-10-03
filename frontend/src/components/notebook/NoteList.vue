<template>
  <div class="note-list-container">
    <div v-if="store.selectedFolder">
      <div class="header">
        <h2 class="text-lg font-semibold text-white">{{ store.selectedFolder.name }}</h2>
        <button @click="handleCreateNote" class="add-note-button">New Note</button>
      </div>

      <div v-if="store.isLoadingNotes" class="loading-spinner">Loading notes...</div>
      <div v-else-if="store.error" class="error-message">{{ store.error }}</div>

      <ul v-else-if="store.notes.length > 0" class="notes">
        <li
          v-for="note in store.notes"
          :key="note.id"
          @click="selectNote(note.id)"
          class="note-item"
        >
          <h3 class="note-title">{{ note.title }}</h3>
          <p class="note-preview">{{ generatePreview(note.content) }}</p>
          <div class="note-footer">
            <span class="note-date">{{ new Date(note.updated_at).toLocaleDateString() }}</span>
            <button @click.stop="handleDeleteNote(note.id)" class="delete-button">🗑️</button>
          </div>
        </li>
      </ul>
      <div v-else class="empty-state">
        <p>No notes in this folder. Click "New Note" to create one!</p>
      </div>
    </div>
    <div v-else class="empty-state-no-folder">
      <p>Select a folder to see your notes.</p>
    </div>
  </div>
</template>

<script setup>
import { useNotebookStore } from '../../stores/notebookStore';

const store = useNotebookStore();

const selectNote = (noteId) => {
  store.selectNote(noteId);
};

const handleCreateNote = () => {
    const newNoteTitle = prompt("Enter a title for the new note:");
    if (newNoteTitle && newNoteTitle.trim()) {
        store.createNote({
            folder_id: store.selectedFolderId,
            title: newNoteTitle.trim(),
            content: { type: 'doc', content: [{ type: 'paragraph' }] } // Default empty Tiptap content
        });
    }
};

const handleDeleteNote = async (noteId) => {
    if (confirm('Are you sure you want to delete this note?')) {
        try {
            await store.deleteNote(noteId);
        } catch (error) {
            console.error("Failed to delete note:", error);
        }
    }
};

// A simple function to generate a text preview from Tiptap's JSON content
const generatePreview = (content) => {
    if (!content || !content.content) return 'No content';
    let text = '';
    content.content.forEach(node => {
        if (node.type === 'paragraph' && node.content) {
            node.content.forEach(textNode => {
                if (textNode.type === 'text') {
                    text += textNode.text + ' ';
                }
            });
        }
    });
    return text.trim().slice(0, 100) + (text.length > 100 ? '...' : '');
};
</script>

<style lang="scss" scoped>
.note-list-container {
  padding: 1rem;
  height: 100%;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.add-note-button {
  background-color: var(--semantic-color-interactive-primary-default);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: var(--semantic-border-radius-interactive);
  cursor: pointer;
}

.notes {
  list-style: none;
  padding: 0;
}

.note-item {
  padding: 1rem;
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-interactive);
  margin-bottom: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    background-color: var(--semantic-color-surface-secondary);
  }
}

.note-title {
  font-weight: bold;
  color: var(--semantic-color-text-primary);
  margin-bottom: 0.5rem;
}

.note-preview {
  color: var(--semantic-color-text-secondary);
  font-size: 0.9rem;
  margin-bottom: 0.75rem;
}

.note-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.8rem;
    color: var(--semantic-color-text-secondary);
}

.delete-button {
    background: none;
    border: none;
    color: var(--semantic-color-text-danger);
    cursor: pointer;
}

.empty-state, .empty-state-no-folder {
    text-align: center;
    margin-top: 4rem;
    color: var(--semantic-color-text-secondary);
}
</style>
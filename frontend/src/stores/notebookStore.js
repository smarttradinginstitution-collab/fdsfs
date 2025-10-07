// frontend/src/stores/notebookStore.js
import { defineStore } from 'pinia';
import apiClient from '../services/api';

export const useNotebookStore = defineStore('notebook', {
  state: () => ({
    folders: [],
    notes: [],
    recentTrades: [], // To store trades for linking
    selectedFolderId: null,
    selectedNoteId: null,
    isLoadingFolders: false,
    isLoadingNotes: false,
    isLoadingTrades: false, // For loading recent trades
    error: null,
    financialData: null, // To store financial data for the selected note
  }),

  getters: {
    selectedFolder: (state) => {
      return state.folders.find(f => f.id === state.selectedFolderId) || null;
    },
    selectedNote: (state) => {
      return state.notes.find(n => n.id === state.selectedNoteId) || null;
    },
    selectedNoteFolder: (state) => {
      if (!state.selectedNote || !state.folders.length) {
        return null;
      }
      return state.folders.find(f => f.id === state.selectedNote.folder_id) || null;
    },
    systemFolders: (state) => {
      const allNotesFolder = {
        id: 'ALL_NOTES_VIRTUAL_ID',
        name: 'All Notes',
        is_system_folder: true,
        system_folder_identifier: 'ALL_NOTES', // Special identifier
        note_count: state.notes.length, // This might not be accurate until all notes are fetched
      };
      const dbSystemFolders = state.folders.filter(f => f.is_system_folder).sort((a, b) => a.name.localeCompare(b.name));
      return [allNotesFolder, ...dbSystemFolders];
    },
    userFolders: (state) => {
      return state.folders.filter(f => !f.is_system_folder).sort((a, b) => a.name.localeCompare(b.name));
    },
    isSystemFolderSelected() {
      return this.selectedFolder ? this.selectedFolder.is_system_folder : false;
    }
  },

  actions: {
    // --- FOLDER ACTIONS ---

    async fetchFolders() {
      this.isLoadingFolders = true;
      this.error = null;
      try {
        const response = await apiClient.get('/notebook/folders');
        this.folders = response.data;

        // If no folder is selected, or the selected one no longer exists,
        // select the first folder by default.
        const selectedFolderExists = this.folders.some(f => f.id === this.selectedFolderId);
        if (!this.selectedFolderId || !selectedFolderExists) {
          if (this.folders.length > 0) {
            this.selectFolder(this.folders[0].id);
          } else {
            this.notes = []; // No folders, so no notes
          }
        }
      } catch (err) {
        console.error('Error fetching notebook folders:', err);
        this.error = err.response?.data?.detail || 'Failed to fetch folders.';
        this.folders = [];
      } finally {
        this.isLoadingFolders = false;
      }
    },

    async createFolder(folderData) {
      this.isLoadingFolders = true;
      try {
        const response = await apiClient.post('/notebook/folders', folderData);
        this.folders.push(response.data);
        this.selectFolder(response.data.id);
        return response.data;
      } catch (err) {
        console.error('Error creating folder:', err);
        this.error = err.response?.data?.detail || 'Failed to create folder.';
        throw err;
      } finally {
        this.isLoadingFolders = false;
      }
    },

    async deleteFolder(folderId) {
        this.isLoadingFolders = true;
        try {
            await apiClient.delete(`/notebook/folders/${folderId}`);
            // If the deleted folder was the selected one, clear selection
            if (this.selectedFolderId === folderId) {
                this.selectedFolderId = null;
                this.selectedNoteId = null;
            }
            await this.fetchFolders(); // Refetch to update list and select a new default
        } catch (err) {
            console.error('Error deleting folder:', err);
            this.error = err.response?.data?.detail || 'Failed to delete folder.';
            throw err;
        } finally {
            this.isLoadingFolders = false;
        }
    },

    async saveFolderTemplate({ folderId, templateContent }) {
      this.isLoadingFolders = true;
      try {
        await apiClient.put(`/notebook/folders/${folderId}`, {
          template_content: templateContent,
        });
        // No need to update folder object directly, just show success
      } catch (err) {
        console.error('Error saving folder template:', err);
        this.error = err.response?.data?.detail || 'Failed to save template.';
        throw err;
      } finally {
        this.isLoadingFolders = false;
      }
    },

    // --- NOTE ACTIONS ---

    async fetchNotesForFolder(folderId) {
      this.isLoadingNotes = true;
      this.error = null;
      try {
        const response = await apiClient.get(`/notebook/folders/${folderId}/notes`);
        this.notes = response.data;
      } catch (err) {
        console.error(`Error fetching notes for folder ${folderId}:`, err);
        this.error = err.response?.data?.detail || 'Failed to fetch notes.';
        this.notes = [];
      } finally {
        this.isLoadingNotes = false;
      }
    },

    async fetchAllNotes() {
      this.isLoadingNotes = true;
      this.error = null;
      try {
        const response = await apiClient.get('/notebook/notes/all');
        this.notes = response.data;
      } catch (err) {
        console.error('Error fetching all notes:', err);
        this.error = err.response?.data?.detail || 'Failed to fetch all notes.';
        this.notes = [];
      } finally {
        this.isLoadingNotes = false;
      }
    },

    async createNote(noteData) {
        this.isLoadingNotes = true;
        try {
            const response = await apiClient.post('/notebook/notes', noteData);

            // After creating, refetch the notes for the folder to ensure the list is up-to-date.
            await this.fetchNotesForFolder(noteData.folder_id);

            // Also, optimistically update the note count on the folder for immediate feedback.
            const folder = this.folders.find(f => f.id === noteData.folder_id);
            if (folder) {
              folder.note_count += 1;
            }

            return response.data; // Return the created note object
        } catch (err) {
            console.error('Error creating note:', err);
            this.error = err.response?.data?.detail || 'Failed to create note.';
            throw err;
        } finally {
            this.isLoadingNotes = false;
        }
    },

    async updateNote(noteId, noteData) {
      // This action is now "silent" - it doesn't trigger a global loading state.
      // This prevents the entire list from flickering during auto-saves.
      try {
        const response = await apiClient.put(`/notebook/notes/${noteId}`, noteData);
        const updatedNote = response.data;

        // Find the index of the note in our local state.
        const index = this.notes.findIndex(note => note.id === noteId);

        // If the note is found in the current list, update it directly.
        // This is the key change to prevent re-fetching the whole list.
        if (index !== -1) {
          // To ensure reactivity, we replace the item.
          // We merge to preserve any local-only properties if they existed.
          this.notes[index] = { ...this.notes[index], ...updatedNote };
        }

        return updatedNote;
      } catch (err) {
        console.error('Error updating note:', err);
        // Optionally set an error state that a component could display
        this.error = err.response?.data?.detail || 'Failed to update note.';
        throw err; // Re-throw so the component knows the save failed.
      }
    },

    async deleteNote(noteId) {
        this.isLoadingNotes = true;
        try {
            await apiClient.delete(`/notebook/notes/${noteId}`);
            // After deleting, refetch notes for the current folder
            if (this.selectedFolderId) {
              await this.fetchNotesForFolder(this.selectedFolderId);
            }
        } catch (err) {
            console.error('Error deleting note:', err);
            this.error = err.response?.data?.detail || 'Failed to delete note.';
            throw err;
        } finally {
            this.isLoadingNotes = false;
        }
    },

    async logDay(date) {
      if (!this.selectedFolderId) {
        const err = 'No folder selected. Please select a folder first.';
        this.error = err;
        console.error(err);
        throw new Error(err);
      }

      // Format date to a user-friendly title like "October 5, 2025"
      const noteTitle = date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });

      try {
        // Create the note and get the new note object in return
        const newNote = await this.createNote({
          folder_id: this.selectedFolderId,
          title: noteTitle,
          content: { type: 'doc', content: [{ type: 'paragraph' }] }, // Start with an empty paragraph
        });

        // Automatically select the newly created note so it opens in the editor
        if (newNote && newNote.id) {
          this.selectNote(newNote.id);
        }
      } catch (err) {
        this.error = 'Could not create the daily log note.';
        // The error is already logged by createNote, so we just update the message
        throw err;
      }
    },

    async createTradeNote({ title, tradeId = null }) {
      if (!this.selectedFolderId) {
        throw new Error("Cannot create trade note without a selected folder.");
      }
      const newNote = await this.createNote({
        folder_id: this.selectedFolderId,
        title,
        trade_id: tradeId,
        content: { type: 'doc', content: [{ type: 'paragraph' }] },
      });
      if (newNote && newNote.id) {
        this.selectNote(newNote.id);
      }
    },

    async createSessionRecapNote({ startDate, endDate }) {
       if (!this.selectedFolderId) {
        throw new Error("Cannot create session recap without a selected folder.");
      }
      const title = `Session: ${startDate.toLocaleDateString()} - ${endDate.toLocaleDateString()}`;
      const newNote = await this.createNote({
        folder_id: this.selectedFolderId,
        title: title,
        content: { type: 'doc', content: [{ type: 'paragraph' }] },
      });
       if (newNote && newNote.id) {
        this.selectNote(newNote.id);
      }
    },

    // --- OTHER ACTIONS ---

    async fetchRecentTrades() {
      this.isLoadingTrades = true;
      this.error = null;
      try {
        const response = await apiClient.get('/trades/recent');
        this.recentTrades = response.data;
      } catch (err) {
        console.error('Error fetching recent trades:', err);
        this.error = err.response?.data?.detail || 'Failed to fetch recent trades.';
        this.recentTrades = [];
      } finally {
        this.isLoadingTrades = false;
      }
    },

    // --- SELECTION ACTIONS ---

    selectFolder(folderId) {
      if (this.selectedFolderId !== folderId) {
        this.selectedFolderId = folderId;
        this.selectedNoteId = null;

        // Handle the virtual "All Notes" folder
        if (folderId === 'ALL_NOTES_VIRTUAL_ID') {
          this.fetchAllNotes();
        } else {
          this.fetchNotesForFolder(folderId);
        }
      }
    },

    selectNote(noteId) {
      this.selectedNoteId = noteId;
      this.fetchFinancialDataForSelectedNote();
    },

    deselectNote() {
        this.selectedNoteId = null;
        this.financialData = null; // Clear financial data when no note is selected
    },

    async fetchFinancialDataForSelectedNote() {
      this.financialData = null; // Reset on each call
      if (!this.selectedNote) return;

      const folder = this.selectedNoteFolder;
      if (!folder) return;

      // Logic for "Trade Notes"
      if (folder.name === 'Trade Notes' && this.selectedNote.trade_id) {
        try {
          const response = await apiClient.get(`/trades/${this.selectedNote.trade_id}/financial_summary`);
          this.financialData = response.data;
        } catch (err) {
          console.error(`Error fetching financial data for trade ${this.selectedNote.trade_id}:`, err);
          this.financialData = { error: 'Could not load trade data.' };
        }
      }
      // Here you could add more else-if blocks for other special folders like "Daily Journal"
    },
  },
});
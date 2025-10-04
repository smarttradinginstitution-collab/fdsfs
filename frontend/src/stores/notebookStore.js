// frontend/src/stores/notebookStore.js
import { defineStore } from 'pinia';
import apiClient from '../services/api';

export const useNotebookStore = defineStore('notebook', {
  state: () => ({
    folders: [],
    notes: [],
    selectedFolderId: null,
    selectedNoteId: null,
    isLoadingFolders: false,
    isLoadingNotes: false,
    error: null,
  }),

  getters: {
    selectedFolder: (state) => {
      return state.folders.find(f => f.id === state.selectedFolderId) || null;
    },
    selectedNote: (state) => {
      return state.notes.find(n => n.id === state.selectedNoteId) || null;
    },
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

    async createNote(noteData) {
        this.isLoadingNotes = true;
        try {
            const response = await apiClient.post('/notebook/notes', noteData);
            // After creating, refetch the notes for the folder to get the updated list
            await this.fetchNotesForFolder(noteData.folder_id);
            return response.data;
        } catch (err) {
            console.error('Error creating note:', err);
            this.error = err.response?.data?.detail || 'Failed to create note.';
            throw err;
        } finally {
            this.isLoadingNotes = false;
        }
    },

    async updateNote(noteId, noteData) {
        this.isLoadingNotes = true;
        try {
            const response = await apiClient.put(`/notebook/notes/${noteId}`, noteData);
            // After updating, refetch notes for the current folder
            if (this.selectedFolderId) {
              await this.fetchNotesForFolder(this.selectedFolderId);
            }
            return response.data;
        } catch (err) {
            console.error('Error updating note:', err);
            this.error = err.response?.data?.detail || 'Failed to update note.';
            throw err;
        } finally {
            this.isLoadingNotes = false;
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
      const journalFolderName = 'Daily Journal';
      let journalFolder = this.folders.find(f => f.name === journalFolderName);

      if (!journalFolder) {
        try {
          journalFolder = await this.createFolder({ name: journalFolderName, color: '#F5A623' });
        } catch (err) {
          this.error = 'Could not create the Daily Journal folder.';
          return;
        }
      }

      const formattedDate = date.toLocaleDateString('en-CA');
      const noteTitle = `Log: ${formattedDate}`;

      try {
        await this.createNote({
          folder_id: journalFolder.id,
          title: noteTitle,
          content: { type: 'doc', content: [{ type: 'paragraph' }] },
        });
        this.selectFolder(journalFolder.id);
      } catch (err) {
        this.error = 'Could not create the daily log note.';
      }
    },

    // --- SELECTION ACTIONS ---

    selectFolder(folderId) {
      if (this.selectedFolderId !== folderId) {
        this.selectedFolderId = folderId;
        this.selectedNoteId = null;
        this.fetchNotesForFolder(folderId);
      }
    },

    selectNote(noteId) {
      this.selectedNoteId = noteId;
    },

    deselectNote() {
        this.selectedNoteId = null;
    }
  },
});
// frontend/src/stores/journalStore.js
import { defineStore } from 'pinia';
import apiClient from '../services/api';

export const useJournalStore = defineStore('journal', {
  state: () => ({
    journalDay: null,
    isLoading: false,
  }),

  actions: {
    async startDay(day) {
      this.isLoading = true;
      try {
        const response = await apiClient.post('/journal/start-day', { day });
        this.journalDay = response.data;
      } catch (error) {
        console.error('Error starting day:', error);
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    async updateNote(noteId, noteData) {
      try {
        const response = await apiClient.put(`/notebook/notes/${noteId}`, noteData);
        if (this.journalDay && this.journalDay.note.id === noteId) {
          // Only update the note content, not the whole journalDay object
          this.journalDay.note.content = response.data.content;
          this.journalDay.note.title = response.data.title;
          this.journalDay.note.updated_at = response.data.updated_at;
        }
      } catch (error) {
        console.error('Error updating note:', error);
        throw error;
      }
    },

    async getDay(day) {
      this.isLoading = true;
      try {
        const response = await apiClient.get(`/journal/day/${day}`);
        this.journalDay = response.data;
      } catch (error) {
        console.error('Error getting day:', error);
      } finally {
        this.isLoading = false;
      }
    },

    async updateManualRuleStatus(instanceId, status) {
      this.isLoading = true;
      try {
        const response = await apiClient.put(`/journal/rules/${instanceId}`, { status });
        const updatedInstance = response.data;
        const ruleIndex = this.journalDay.rules.findIndex(
          (r) => r.id === updatedInstance.id
        );
        if (ruleIndex !== -1) {
          this.journalDay.rules[ruleIndex] = updatedInstance;
        }
      } catch (error) {
        console.error('Error updating manual rule status:', error);
        throw error;
      } finally {
        this.isLoading = false;
      }
    },
  },
});
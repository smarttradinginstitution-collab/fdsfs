// frontend/src/stores/disciplineStore.js
import { defineStore } from 'pinia';
import apiClient from '../services/api';

export const useDisciplineStore = defineStore('discipline', {
  state: () => ({
    rules: [],
    summary: null,
    isLoading: false,
  }),

  actions: {
    async fetchRules() {
      this.isLoading = true;
      try {
        const response = await apiClient.get('/discipline/rules');
        this.rules = response.data;
      } catch (error) {
        console.error('Error fetching discipline rules:', error);
      } finally {
        this.isLoading = false;
      }
    },

    async createRule(ruleData) {
      this.isLoading = true;
      try {
        const response = await apiClient.post('/discipline/rules', ruleData);
        this.rules.push(response.data);
      } catch (error) {
        console.error('Error creating discipline rule:', error);
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    async updateRule(ruleId, ruleData) {
      this.isLoading = true;
      try {
        const response = await apiClient.put(`/discipline/rules/${ruleId}`, ruleData);
        const index = this.rules.findIndex((r) => r.id === ruleId);
        if (index !== -1) {
          this.rules[index] = response.data;
        }
      } catch (error) {
        console.error('Error updating discipline rule:', error);
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    async deleteRule(ruleId) {
      this.isLoading = true;
      try {
        await apiClient.delete(`/discipline/rules/${ruleId}`);
        this.rules = this.rules.filter((r) => r.id !== ruleId);
      } catch (error) {
        console.error('Error deleting discipline rule:', error);
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    async fetchSummary() {
      this.isLoading = true;
      try {
        const response = await apiClient.get('/discipline/progress-tracker-summary');
        this.summary = response.data;
      } catch (error) {
        console.error('Error fetching progress tracker summary:', error);
      } finally {
        this.isLoading = false;
      }
    },
  },
});
<template>
  <div class="add-account-container">
    <!-- Step 1: Welcome Message -->
    <div v-if="currentStep === 'welcome'" class="step-card">
      <div class="welcome-message">
        <h1>Welcome to TradeVantage!</h1>
        <p>Take control of your trading journey. Let's start by adding your first account.</p>
      </div>
      <div class="add-account-card" @click="startProcess">
        <h2>Add your Account</h2>
        <p>Click here to choose your broker and set up your account.</p>
      </div>
    </div>

    <!-- Step 2: Broker Selection -->
    <div v-if="currentStep === 'select-broker'" class="step-card">
      <h2>Choose your Broker</h2>
      <input type="text" v-model="searchQuery" placeholder="Search for a broker..." class="search-bar" />
      <p v-if="!searchQuery" class="popular-brokers-label">Or Select From The Popular Brokers</p>
      <div class="broker-grid">
        <div v-for="broker in displayBrokers" :key="broker.id" class="broker-item" @click="selectBroker(broker)">
          <span class="broker-icon">🏢</span>
          <span class="broker-name">{{ broker.name }}</span>
        </div>
      </div>
      <p v-if="displayBrokers.length === 0" class="no-results-message">No brokers found.</p>
    </div>

    <!-- Step 3: Account Details Form -->
    <div v-if="currentStep === 'account-details'" class="step-card">
      <h2>Account Details</h2>
      <p class="broker-info">
        <strong>Broker:</strong> {{ selectedBroker.name }}
        <button @click="resetStep" class="change-broker-btn">Change</button>
      </p>
      <form @submit.prevent="submitAccount">
        <div class="form-group">
          <label for="account-label">Account Name</label>
          <input id="account-label" v-model="form.label" type="text" required placeholder="e.g., My Prop Firm Account" />
        </div>
        <div class="form-group">
          <label for="initial-balance">Initial Balance</label>
          <input id="initial-balance" v-model="form.initial_balance" type="number" step="0.01" required placeholder="e.g., 10000" />
        </div>
        <div class="form-group">
          <label for="currency">Currency</label>
          <select id="currency" v-model="form.currency" required>
            <option value="USD">USD</option>
            <option value="EUR">EUR</option>
            <option value="GBP">GBP</option>
          </select>
        </div>
        <button type="submit" class="submit-btn" :disabled="isSubmitting">
          {{ isSubmitting ? 'Creating...' : 'Create Account' }}
        </button>
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import brokerService from '@/services/brokerService';
import { useTradingAccountsStore } from '@/stores/tradingAccounts';

// Component State
const currentStep = ref('welcome'); // 'welcome', 'select-broker', 'account-details'
const brokers = ref([]);
const searchQuery = ref('');
const selectedBroker = ref(null);
const isSubmitting = ref(false);
const errorMessage = ref('');

// Form Data
const form = ref({
  label: '',
  broker_id: null,
  initial_balance: null,
  currency: 'USD',
});

// Dependencies
const router = useRouter();
const tradingAccountsStore = useTradingAccountsStore();

// --- Lifecycle ---
onMounted(async () => {
  try {
    const response = await brokerService.getBrokers();
    brokers.value = response.data;
  } catch (error) {
    console.error('Failed to fetch brokers:', error);
    errorMessage.value = 'Could not load the list of brokers.';
  }
});

// --- Computed Properties ---
const displayBrokers = computed(() => {
  if (!searchQuery.value) {
    // If no search query, show the top 8 as "popular brokers"
    return brokers.value.slice(0, 8);
  }
  // Otherwise, filter the entire list based on the search query
  return brokers.value.filter(broker =>
    broker.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

// --- Methods ---
function startProcess() {
  currentStep.value = 'select-broker';
}

function selectBroker(broker) {
  selectedBroker.value = broker;
  form.value.broker_id = broker.id;
  currentStep.value = 'account-details';
}

function resetStep() {
  currentStep.value = 'select-broker';
  selectedBroker.value = null;
  form.value.broker_id = null;
  errorMessage.value = '';
}

async function submitAccount() {
  isSubmitting.value = true;
  errorMessage.value = '';
  try {
    await tradingAccountsStore.createTradingAccount(form.value);
    // On success, the navigation guard will redirect to the dashboard
    // after the store updates and a selection is made (or to select-account).
    // Forcing a reload or navigation might be necessary if the guard doesn't pick it up automatically.
    router.push({ name: 'dashboard' });
  } catch (error) {
    errorMessage.value = 'Failed to create account. Please check the details and try again.';
    console.error('Account creation error:', error);
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<style scoped>
/* --- Generic Layout --- */
.add-account-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 2rem;
}

.step-card {
  width: 100%;
  max-width: 500px;
  background-color: var(--semantic-color-surface-primary);
  padding: 2.5rem;
  border-radius: var(--semantic-border-radius-lg);
  border: 1px solid var(--semantic-color-border-subtle);
  box-shadow: var(--semantic-effect-shadow-elevation-low);
  text-align: center;
}

/* --- Welcome Step --- */
.welcome-message {
  margin-bottom: 2rem;
}

.welcome-message h1 {
  font-size: 2.2rem;
  color: var(--semantic-color-text-primary);
}

.welcome-message p {
  font-size: 1.1rem;
  color: var(--semantic-color-text-secondary);
}

.add-account-card {
  padding: 1.5rem;
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-md);
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  background-color: var(--semantic-color-surface-secondary);
}

.add-account-card:hover {
  border-color: var(--semantic-color-border-focus);
  background-color: var(--semantic-color-interactive-secondary-hover);
  transform: translateY(-2px);
}

.add-account-card h2 {
  color: var(--semantic-color-text-primary);
  margin-bottom: 0.5rem;
}

.add-account-card p {
  color: var(--semantic-color-text-secondary);
}


/* --- Broker Selection Step --- */
.search-bar {
  width: 100%;
  padding: 0.8rem 1rem;
  margin-bottom: 1.5rem;
  background-color: var(--semantic-color-surface-secondary);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-md);
  color: var(--semantic-color-text-primary);
  font-size: 1rem;
  transition: all 0.2s ease-in-out;
}

.search-bar:focus {
  outline: none;
  border-color: var(--semantic-color-border-focus);
  box-shadow: var(--semantic-effect-shadow-focus-ring);
}

.popular-brokers-label {
  color: var(--semantic-color-text-secondary);
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.broker-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  max-height: 300px;
  overflow-y: auto;
  padding-right: 0.5rem; /* For scrollbar spacing */
}

.broker-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background-color: var(--semantic-color-surface-secondary);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-md);
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}

.broker-item:hover {
  border-color: var(--semantic-color-border-focus);
  background-color: var(--semantic-color-interactive-secondary-hover);
  transform: translateY(-2px);
}

.broker-icon {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 32px;
  height: 32px;
  font-size: 1.25rem;
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-full);
  color: var(--semantic-color-text-secondary);
}

.broker-name {
  color: var(--semantic-color-text-primary);
  font-weight: 500;
}

.no-results-message {
  color: var(--semantic-color-text-secondary);
  margin-top: 1.5rem;
}

/* --- Account Details Step --- */
.broker-info {
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
  color: var(--semantic-color-text-secondary);
}

.change-broker-btn {
  background: none;
  border: none;
  color: var(--semantic-color-text-interactive);
  cursor: pointer;
  margin-left: 0.5rem;
  font-size: 0.9rem;
}

.change-broker-btn:hover {
  text-decoration: underline;
}

.form-group {
  margin-bottom: 1.2rem;
  text-align: left;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--semantic-color-text-secondary);
}

.form-group input, .form-group select {
  width: 100%;
  padding: 0.8rem 1rem;
  background-color: var(--semantic-color-surface-secondary);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-md);
  color: var(--semantic-color-text-primary);
  font-size: 1rem;
  transition: all 0.2s ease-in-out;
}

.form-group input:focus, .form-group select:focus {
  outline: none;
  border-color: var(--semantic-color-border-focus);
  box-shadow: var(--semantic-effect-shadow-focus-ring);
}

.submit-btn {
  width: 100%;
  padding: 0.9rem;
  background-color: var(--semantic-color-interactive-primary-default);
  color: var(--semantic-color-text-on-brand);
  border: none;
  border-radius: var(--semantic-border-radius-md);
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease-in-out;
}

.submit-btn:disabled {
  background-color: var(--semantic-color-surface-disabled);
  color: var(--semantic-color-text-disabled);
  cursor: not-allowed;
}

.submit-btn:hover:not(:disabled) {
  background-color: var(--semantic-color-interactive-primary-hover);
}

.error-message {
  color: var(--semantic-color-feedback-negative-text);
  margin-top: 1rem;
}
</style>
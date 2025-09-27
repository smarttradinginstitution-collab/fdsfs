<template>
  <div class="add-account-container">
    <!-- Step 1: Welcome Message -->
    <div v-if="currentStep === 'welcome'" class="welcome-card">
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
    <div v-if="currentStep === 'select-broker'" class="broker-selection-card">
      <h2>Choose your Broker</h2>
      <input type="text" v-model="searchQuery" placeholder="Search for a broker..." class="search-bar" />
      <div class="broker-list">
        <div v-for="broker in filteredBrokers" :key="broker.id" class="broker-item" @click="selectBroker(broker)">
          <span class="broker-icon">🏢</span> <!-- Placeholder Icon -->
          <span class="broker-name">{{ broker.name }}</span>
        </div>
        <p v-if="filteredBrokers.length === 0">No brokers found.</p>
      </div>
    </div>

    <!-- Step 3: Account Details Form -->
    <div v-if="currentStep === 'account-details'" class="account-details-card">
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
const filteredBrokers = computed(() => {
  if (!searchQuery.value) {
    return brokers.value;
  }
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
.add-account-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f0f2f5;
  padding: 2rem;
}

.welcome-card, .broker-selection-card, .account-details-card {
  width: 100%;
  max-width: 500px;
  background-color: white;
  padding: 2rem 2.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.welcome-message {
  margin-bottom: 2rem;
}

.welcome-message h1 {
  font-size: 2.2rem;
  color: #333;
}

.welcome-message p {
  font-size: 1.1rem;
  color: #666;
}

.add-account-card {
  padding: 1.5rem;
  border: 2px dashed #ccc;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.add-account-card:hover {
  border-color: #007bff;
  background-color: #f8f9fa;
}

.search-bar {
  width: 100%;
  padding: 0.8rem;
  margin-bottom: 1.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
}

.broker-list {
  max-height: 250px;
  overflow-y: auto;
}

.broker-item {
  display: flex;
  align-items: center;
  padding: 0.8rem;
  cursor: pointer;
  border-radius: 4px;
}

.broker-item:hover {
  background-color: #f0f2f5;
}

.broker-icon {
  font-size: 1.5rem;
  margin-right: 1rem;
}

.broker-name {
  font-size: 1.1rem;
}

.broker-info {
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
}

.change-broker-btn {
  background: none;
  border: none;
  color: #007bff;
  cursor: pointer;
  margin-left: 0.5rem;
  font-size: 0.9rem;
}

.form-group {
  margin-bottom: 1.2rem;
  text-align: left;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.form-group input, .form-group select {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
}

.submit-btn {
  width: 100%;
  padding: 0.9rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1.1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-btn:disabled {
  background-color: #aaa;
  cursor: not-allowed;
}

.submit-btn:hover:not(:disabled) {
  background-color: #0056b3;
}

.error-message {
  color: #dc3545;
  margin-top: 1rem;
}
</style>
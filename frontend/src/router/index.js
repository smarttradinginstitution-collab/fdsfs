import { createRouter, createWebHistory } from 'vue-router';
import DashboardView from '../views/DashboardView.vue';
import AddTradeView from '../views/AddTradeView.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { title: 'Login', public: true }
    },
    {
      path: '/select-account',
      name: 'select-account',
      component: () => import('../views/SelectAccountView.vue'),
      meta: { title: 'Select Account' }, // Protected by default
    },
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView,
      meta: { title: 'Dashboard' },
    },
    {
      path: '/add-trade',
      name: 'add-trade',
      component: AddTradeView,
      meta: { title: 'Add Trade' },
    },
    {
      path: '/trades',
      name: 'trades',
      component: () => import('../views/TradesView.vue'),
      meta: { title: 'Trades' },
    },
    {
      path: '/analytics',
      name: 'analytics',
      component: () => import('../views/AnalyticsView.vue'),
      meta: { title: 'Analytics' },
    },
    {
      path: '/component-test',
      name: 'component-test',
      component: () => import('../views/ComponentTestView.vue'),
      meta: { title: 'Component Test' },
    }
  ],
});

// --- NAVIGATION GUARD ---
import { useAuthStore } from '../stores/auth';
import { useTradingAccountsStore } from '../stores/tradingAccounts';

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();
  const tradingAccountsStore = useTradingAccountsStore();

  // Initialize auth store to ensure token is loaded from localStorage
  if (!authStore.token && localStorage.getItem('token')) {
    await authStore.initAuth(); // Ensures we have user and generalAccount info
  }

  // If user is authenticated but the list of trading accounts is empty, fetch them.
  // This handles page reloads on any protected route.
  if (authStore.isAuthenticated && tradingAccountsStore.tradingAccounts.length === 0) {
      await tradingAccountsStore.fetchTradingAccounts();
  }

  const isAuthenticated = authStore.isAuthenticated;
  // Re-evaluate after fetching, in case fetchTradingAccounts cleared the selection
  const hasSelectedTradingAccount = !!tradingAccountsStore.selectedTradingAccount;
  const authRequired = !to.meta.public;

  if (authRequired && !isAuthenticated) {
    // If a protected route is accessed without authentication (no token/GA), redirect to login.
    return next('/login');
  }

  if (isAuthenticated) {
    // If the user is authenticated (has token and GA)
    if (to.path === '/login') {
      // and tries to access the login page, redirect them away.
      return next(hasSelectedTradingAccount ? '/' : '/select-account');
    }

    // For any other protected route
    if (authRequired) {
      if (!hasSelectedTradingAccount && to.path !== '/select-account') {
        // If the user hasn't selected a trading account yet, force them to the selection page.
        return next('/select-account');
      }
      if (hasSelectedTradingAccount && to.path === '/select-account') {
        // If user has an account and tries to go to selection, redirect to dashboard.
        return next('/');
      }
    }
  }

  // Otherwise, allow navigation.
  next();
});


export default router;
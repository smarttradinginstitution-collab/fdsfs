import { createRouter, createWebHistory } from 'vue-router';
import DashboardView from '../views/DashboardView.vue';
import AddTradeView from '../views/AddTradeView.vue';
import AddAccountView from '../views/AddAccountView.vue';

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
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
      meta: { title: 'Registrati', public: true }
    },
    {
      path: '/add-account',
      name: 'add-account',
      component: AddAccountView,
      meta: { title: 'Add Account', fullScreen: true },
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
      path: '/report/:id',
      name: 'report-detail',
      component: () => import('../views/ReportView.vue'),
      meta: { title: 'Report Detail' },
    },
    {
      path: '/playbooks',
      name: 'playbooks',
      component: () => import('../views/PlaybooksView.vue'),
      meta: { title: 'Playbooks' },
    },
    {
      path: '/playbooks/new',
      name: 'playbook-create',
      component: () => import('../views/CreatePlaybookView.vue'),
      meta: { title: 'Create Playbook' },
    },
    {
      path: '/playbooks/:id',
      name: 'playbook-detail',
      component: () => import('../views/PlaybookDetailView.vue'),
      meta: { title: 'Playbook Detail' },
    },
    {
      path: '/analytics',
      name: 'analytics',
      component: () => import('../views/AnalyticsView.vue'),
      meta: { title: 'Analytics' },
    },
    {
      path: '/notebook',
      name: 'notebook',
      component: () => import('../views/NotebookView.vue'),
      meta: { title: 'Notebook' },
    },
    {
      path: '/component-test',
      name: 'component-test',
      component: () => import('../views/ComponentTestView.vue'),
      meta: { title: 'Component Test' },
    },
    {
      path: '/library',
      name: 'library',
      component: () => import('../views/LibraryView.vue'),
      meta: { title: 'Library' },
    },
    {
      path: '/progress-tracker',
      name: 'progress-tracker',
      component: () => import('../views/ProgressTrackerView.vue'),
      meta: { title: 'Progress Tracker' },
    },
  ],
});

// --- NAVIGATION GUARD ---
import { useAuthStore } from '../stores/auth';
import { useTradingAccountsStore } from '../stores/tradingAccounts';

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();
  const tradingAccountsStore = useTradingAccountsStore();

  // Ensure auth status is loaded from token
  if (!authStore.token && localStorage.getItem('token')) {
    await authStore.initAuth();
  }

  const isAuthenticated = authStore.isAuthenticated;
  const authRequired = !to.meta.public;

  // 1. Handle unauthenticated users trying to access protected routes
  if (authRequired && !isAuthenticated) {
    return next({ name: 'login', query: { redirect: to.fullPath } });
  }

  // 2. Handle authenticated users
  if (isAuthenticated) {
    // Redirect away from login/register page if already authenticated
    if (to.name === 'login' || to.name === 'register') {
      return next({ name: 'dashboard' });
    }

    // Fetch accounts if not already loaded.
    if (tradingAccountsStore.tradingAccounts.length === 0) {
      await tradingAccountsStore.fetchTradingAccounts();
    }

    const hasAccounts = tradingAccountsStore.hasTradingAccounts;
    const accountsCount = tradingAccountsStore.tradingAccounts.length;
    let hasSelectedAccount = !!tradingAccountsStore.selectedTradingAccount;

    // --- FINAL, EXPLICIT REDIRECTION LOGIC ---

    // CASE 1: User has no accounts. They must create one.
    if (!hasAccounts) {
      if (to.name !== 'add-account') {
        return next({ name: 'add-account' });
      }
      return next();
    }

    // CASE 2: User has accounts, but none selected in the store/localStorage.
    if (!hasSelectedAccount) {
      // Subcase 2a: Auto-select the single account.
      if (accountsCount === 1) {
        const singleAccount = tradingAccountsStore.tradingAccounts[0];
        tradingAccountsStore.selectTradingAccount(singleAccount);
        // Re-check selection status, as it has just been updated.
        hasSelectedAccount = !!tradingAccountsStore.selectedTradingAccount;
        // Now, we can proceed as if an account was already selected.
      } else {
        // Subcase 2b: Multiple accounts, user must choose.
        if (to.name !== 'select-account') {
          return next({ name: 'select-account' });
        }
        return next();
      }
    }

    // CASE 3: User has a selected account.
    if (hasSelectedAccount) {
      // Prevent access to setup pages.
      if (to.name === 'add-account' || to.name === 'select-account') {
        return next({ name: 'dashboard' });
      }
      // Otherwise, allow navigation.
      return next();
    }
  }

  // 3. If not authenticated and no auth is required, or any other case, proceed.
  next();
});


export default router;
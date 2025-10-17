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

    // Fetch trading accounts if they haven't been loaded yet.
    // This is crucial for users who reload the page or login.
    if (tradingAccountsStore.tradingAccounts.length === 0) {
      await tradingAccountsStore.fetchTradingAccounts();
    }

    const hasAccounts = tradingAccountsStore.hasTradingAccounts;
    const hasSelectedAccounts = tradingAccountsStore.hasSelectedAccounts;

    // Handle routing based on account status for authenticated users.
    // This logic defines the setup flow for new users or users without selections.
    if (authRequired) {
      // If the user is trying to access any protected page...
      if (!hasAccounts) {
        // ...but has no accounts, force them to the account creation page.
        // Allow navigation only if the target is 'add-account'.
        if (to.name !== 'add-account') return next({ name: 'add-account' });
      } else if (!hasSelectedAccounts) {
        // ...or has accounts but none are selected, force them to the selection page.
        // Allow navigation only if the target is 'select-account'.
        if (to.name !== 'select-account') return next({ name: 'select-account' });
      }
    }

    // Additional guardrails for specific pages
    if (to.name === 'select-account') {
      // If the user has no accounts, they must create one first.
      if (!hasAccounts) return next({ name: 'add-account' });
      // If they already have a selection, they should be on the dashboard.
      if (hasSelectedAccounts) return next({ name: 'dashboard' });
    } else if (to.name === 'add-account') {
      // If user already has accounts, they shouldn't be on the 'add-account' page.
      // Redirect them to select one or to the dashboard.
      if (hasAccounts) {
        return next({ name: hasSelectedAccounts ? 'dashboard' : 'select-account' });
      }
    }
  }

  // 3. If none of the above conditions apply, proceed with navigation
  next();
});


export default router;
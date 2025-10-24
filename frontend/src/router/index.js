import { createRouter, createWebHistory } from 'vue-router';

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
      component: () => import('../views/AddAccountView.vue'),
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
      component: () => import('../views/DashboardView.vue'),
      meta: { title: 'Dashboard' },
    },
    {
      path: '/add-trade',
      name: 'add-trade',
      component: () => import('../views/AddTradeView.vue'),
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
      path: '/playbooks/:id/edit',
      name: 'playbook-edit',
      component: () => import('../views/EditPlaybookView.vue'),
      meta: { title: 'Edit Playbook' },
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

    // Fetch trading accounts if they haven't been loaded yet.
    // This is crucial for users who reload the page on a protected route.
    if (tradingAccountsStore.tradingAccounts.length === 0) {
      await tradingAccountsStore.fetchTradingAccounts();
    }

    const hasAccounts = tradingAccountsStore.hasTradingAccounts;
    const hasSelectedAccounts = tradingAccountsStore.tradingAccounts.some(acc => acc.is_selected);

    // New, more robust routing logic to prevent redirect loops.
    // The logic is now based on the user's setup status.

    // STATUS 1: Setup is complete (user has accounts and a selection)
    if (hasAccounts && hasSelectedAccounts) {
      // If setup is complete, prevent access to setup pages.
      if (to.name === 'add-account' || to.name === 'select-account') {
        return next({ name: 'dashboard' });
      }
    }
    // STATUS 2: User has accounts but no selection
    else if (hasAccounts && !hasSelectedAccounts) {
      // They must select an account, unless they are already on the selection page.
      if (to.name !== 'select-account') {
        return next({ name: 'select-account' });
      }
    }
    // STATUS 3: User has no accounts at all
    else if (!hasAccounts) {
      // They must create an account, unless they are already on the creation page.
      if (to.name !== 'add-account') {
        return next({ name: 'add-account' });
      }
    }
  }

  // 3. If none of the above conditions apply, proceed with navigation
  next();
});


export default router;
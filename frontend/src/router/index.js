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
      path: '/settings/tags',
      name: 'tags-settings',
      component: () => import('../views/TagsSettingsView.vue'),
      meta: { title: 'Tags Settings' },
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
    // Redirect away from login page if already authenticated
    if (to.name === 'login') {
      return next({ name: 'dashboard' });
    }

    // Fetch trading accounts if they haven't been loaded yet.
    // This is crucial for users who reload the page on a protected route.
    if (tradingAccountsStore.tradingAccounts.length === 0) {
      await tradingAccountsStore.fetchTradingAccounts();
    }

    const hasAccounts = tradingAccountsStore.hasTradingAccounts;
    const hasSelectedAccount = !!tradingAccountsStore.selectedTradingAccount;

    // Handle routing based on account status
    if (to.name === 'add-account') {
      // If user has accounts, they shouldn't be on the 'add-account' page
      if (hasAccounts) return next({ name: 'dashboard' });
    } else if (to.name === 'select-account') {
      // If user has NO accounts, they must go to the 'add-account' page first
      if (!hasAccounts) return next({ name: 'add-account' });
      // If user has already selected an account, send them to the dashboard
      if (hasSelectedAccount) return next({ name: 'dashboard' });
    } else if (authRequired) {
      // For any other protected page, enforce the setup flow
      if (!hasAccounts) return next({ name: 'add-account' });
      if (!hasSelectedAccount) return next({ name: 'select-account' });
    }
  }

  // 3. If none of the above conditions apply, proceed with navigation
  next();
});


export default router;
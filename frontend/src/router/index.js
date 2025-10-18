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
import { useInitStore } from '../stores/init'; // Importa il nuovo store

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();
  const tradingAccountsStore = useTradingAccountsStore();
  const initStore = useInitStore(); // Usa il nuovo store

  // Assicura che lo stato di autenticazione sia caricato dal token
  if (!authStore.token && localStorage.getItem('token')) {
    await authStore.initAuth();
  }

  const isAuthenticated = authStore.isAuthenticated;
  const authRequired = !to.meta.public;

  // 1. Gestisce gli utenti non autenticati che cercano di accedere a route protette
  if (authRequired && !isAuthenticated) {
    return next({ name: 'login', query: { redirect: to.fullPath } });
  }

  // 2. Gestisce gli utenti autenticati
  if (isAuthenticated) {
    // Reindirizza lontano dalla pagina di login/registrazione se già autenticato
    if (to.name === 'login' || to.name === 'register') {
      return next({ name: 'dashboard' });
    }

    // Carica i dati della sessione in modo orchestrato se non è già stato fatto.
    // Questo sostituisce la vecchia logica di caricamento a cascata.
    if (!initStore.isInitialized) {
      await initStore.initSessionData();
    }

    // La logica di reindirizzamento si basa sullo stato caricato dall'initStore.
    const hasAccounts = tradingAccountsStore.hasTradingAccounts;
    const hasSelectedAccount = !!tradingAccountsStore.selectedTradingAccount;

    // Gestisce il routing basato sullo stato dell'account
    if (to.name === 'add-account') {
      if (hasAccounts) return next({ name: 'dashboard' });
    } else if (to.name === 'select-account') {
      if (!hasAccounts) return next({ name: 'add-account' });
      if (hasSelectedAccount) return next({ name: 'dashboard' });
    } else if (authRequired) {
      // Per qualsiasi altra pagina protetta, impone il flusso di setup
      if (!hasAccounts) return next({ name: 'add-account' });
      if (!hasSelectedAccount) return next({ name: 'select-account' });
    }
  }

  // 3. Se nessuna delle condizioni precedenti si applica, procedi con la navigazione
  next();
});


export default router;
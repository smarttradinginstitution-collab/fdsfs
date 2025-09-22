import { createRouter, createWebHistory } from 'vue-router';
import DashboardView from '../views/DashboardView.vue';
import AddTradeView from '../views/AddTradeView.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      // I'm not using MainLayout for the login page
      component: () => import('../views/LoginView.vue'),
      meta: { title: 'Login', public: true }
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

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();

  // Initialize auth store to ensure token is loaded from localStorage
  // if the app is reloaded.
  if (!authStore.token) {
    authStore.initAuth();
  }

  const isAuthenticated = authStore.isAuthenticated;

  // A route is considered protected if it's not marked as public in its meta field.
  const authRequired = !to.meta.public;

  if (authRequired && !isAuthenticated) {
    // Se la pagina richiede autenticazione e l'utente non è loggato,
    // reindirizza alla pagina di login.
    return next('/login');
  }

  if (to.path === '/login' && isAuthenticated) {
    // Se l'utente è già loggato e cerca di andare alla pagina di login,
    // reindirizzalo alla dashboard.
    return next('/');
  }

  // Altrimenti, procedi con la navigazione.
  next();
});


export default router;

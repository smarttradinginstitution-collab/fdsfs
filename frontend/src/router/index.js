import { createRouter, createWebHistory } from 'vue-router';
import DashboardView from '../views/DashboardView.vue';
import { useAuthStore } from '../stores/auth';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { title: 'Login', public: true, layout: 'AuthLayout' },
    },
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView,
      meta: { title: 'Dashboard' },
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

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();
  const isAuthenticated = authStore.isAuthenticated;

  // If the auth store hasn't been checked yet, do it now
  if (!authStore.user && authStore.token) {
    await authStore.checkAuth();
  }

  const isPublic = to.matched.some(record => record.meta.public);

  if (!isPublic && !isAuthenticated) {
    next({ name: 'login' });
  } else if (isPublic && isAuthenticated && to.name === 'login') {
    next({ name: 'dashboard' });
  } else {
    next();
  }
});

export default router;

import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('../views/index.vue'),
    },
    {
      path: '/auth',
      name: 'Auth',
      component: () => import('../views/auth/Auth.vue'),
      children: [
        {
          path: 'login',
          name: 'Login',
          component: () => import('../views/auth/Login.vue'),
        },
        {
          path: 'register',
          name: 'Register',
          component: () => import('../views/auth/Register.vue'),
        },
        {
          path: 'forgot-password',
          name: 'ForgotPassword',
          component: () => import('../views/auth/ForgetPassword.vue'),
        },
      ],
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('../views/dashboard/Dashboard.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: 'chat',
          name: 'DashboardChat',
          component: () => import('../views/dashboard/Chat.vue'),
          meta: { requiresAuth: true },
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('../views/NotFound.vue'),
    },
  ],
})

// Navigation guard for authentication
router.beforeEach((to, _from, next) => {
  const userStore = useUserStore()
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)

  if (requiresAuth && !userStore.user.token) {
    // Redirect to home (which has login modal)
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router

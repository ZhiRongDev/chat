import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login',
    },
    {
      path: '/',
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
          path: 'forget-password',
          name: 'ForgetPassword',
          component: () => import('../views/auth/ForgetPassword.vue'),
        },
      ],
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('../views/dashboard/Dashboard.vue'),
      children: [
        {
          path: 'chat',
          name: 'Chat',
          component: () => import('../views/dashboard/Chat.vue'),
        },
      ],
    },
  ],
})

export default router

import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/auth/login',
    },
    {
      path: '/auth',
      name: 'Auth',
      redirect: '/auth/login',
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
      path: '/chat',
      name: 'Chat',
      component: () => import('../views/Chat.vue'),
    },
  ],
})

export default router

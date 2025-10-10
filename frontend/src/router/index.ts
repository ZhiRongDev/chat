import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('../views/index.vue'),
    },
    {
      path: '/chat',
      name: 'Chat',
      component: () => import('../views/Chat.vue'),
    },
  ],
})

export default router

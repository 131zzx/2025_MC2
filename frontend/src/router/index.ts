import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/bias',
    },
    {
      path: '/bias',
      name: 'Bias',
      component: () => import('../views/BiasView.vue'),
      meta: { title: '偏见全景' },
    },
    {
      path: '/member',
      name: 'Member',
      component: () => import('../views/MemberView.vue'),
      meta: { title: '委员行为' },
    },
    {
      path: '/trip',
      name: 'Trip',
      component: () => import('../views/TripView.vue'),
      meta: { title: '行程地图' },
    },
  ],
})

export default router

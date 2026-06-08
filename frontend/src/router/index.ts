import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/q1',
    },
    {
      path: '/q1',
      name: 'Q1',
      component: () => import('../views/Q1View.vue'),
      meta: { title: 'Q1 · 各方数据集自证分析' },
    },
    {
      path: '/q2',
      name: 'Q2',
      component: () => import('../views/Q2View.vue'),
      meta: { title: 'Q2 · 委员会时间分配与偏袒判断' },
    },
    {
      path: '/q3',
      name: 'Q3',
      component: () => import('../views/Q3View.vue'),
      meta: { title: 'Q3 · 不完整数据 vs 全量对比' },
    },
    {
      path: '/q4',
      name: 'Q4',
      component: () => import('../views/Q4View.vue'),
      meta: { title: 'Q4 · 人物级对比分析' },
    },
  ],
})

export default router

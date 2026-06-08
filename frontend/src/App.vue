<template>
  <div class="layout">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="logo">
        <span class="logo-icon">MC2</span>
        <div>
          <div class="logo-title">COOTEFOO</div>
          <div class="logo-sub">偏见可视化分析 · VAST 2025 MC2</div>
        </div>
      </div>

      <nav class="nav">
        <router-link
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="nav-item"
          active-class="nav-item--active"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="data-badge" :class="statusClass">
          {{ statusText }}
        </div>
        <div class="dataset-legend">
          <span class="leg filah">■ FILAH</span>
          <span class="leg trout">■ TROUT</span>
          <span class="leg journalist">■ journalist</span>
        </div>
      </div>
    </aside>

    <!-- 主区域 -->
    <div class="main">
      <header class="topbar">
        <h1 class="page-title">{{ currentTitle }}</h1>
      </header>
      <main class="content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useDataStore } from './stores/dataStore'

const route     = useRoute()
const dataStore = useDataStore()

const navItems = [
  { to: '/q1', icon: 'Q1', label: '数据集自证分析' },
  { to: '/q2', icon: 'Q2', label: '时间分配与偏袒' },
  { to: '/q3', icon: 'Q3', label: '不完整 vs 全量' },
  { to: '/q4', icon: 'Q4', label: '人物级对比' },
]

const currentTitle = computed(() => (route.meta as any).title ?? 'COOTEFOO 可视化分析')

const statusClass = computed(() => ({
  'badge--loading': dataStore.loading,
  'badge--error':   !!dataStore.error,
  'badge--ok':      dataStore.loaded,
}))

const statusText = computed(() => {
  if (dataStore.loading) return '加载数据中...'
  if (dataStore.error)   return '数据加载失败'
  if (dataStore.loaded)  return '数据已就绪'
  return '待加载'
})

onMounted(() => dataStore.loadAll())
</script>

<style scoped>
.layout { display: flex; height: 100vh; overflow: hidden; background: #f8fafc; }

/* ── 侧边栏 ── */
.sidebar {
  width: 220px; flex-shrink: 0;
  background: #ffffff;
  border-right: 1px solid #e2e8f0;
  display: flex; flex-direction: column; overflow: hidden;
}
.logo {
  display: flex; align-items: center; gap: 10px;
  padding: 20px 16px 16px;
  border-bottom: 1px solid #e2e8f0;
}
.logo-icon {
  font-size: 11px; font-weight: 800; letter-spacing: .04em;
  background: #1e293b; color: #fff;
  padding: 4px 6px; border-radius: 6px;
}
.logo-title { font-size: 13px; font-weight: 700; color: #1e293b; }
.logo-sub   { font-size: 10px; color: #94a3b8; line-height: 1.4; }

.nav { flex: 1; padding: 12px 8px; display: flex; flex-direction: column; gap: 2px; }
.nav-item {
  display: flex; align-items: center; gap: 10px;
  padding: 9px 12px; border-radius: 8px;
  text-decoration: none; color: #64748b;
  font-size: 13px; transition: all 0.15s;
}
.nav-item:hover { background: #f1f5f9; color: #1e293b; }
.nav-item--active { background: #eff6ff; color: #2563eb; font-weight: 700; }
.nav-icon {
  font-size: 10px; font-weight: 800;
  width: 22px; height: 22px; border-radius: 5px;
  display: flex; align-items: center; justify-content: center;
  background: #e2e8f0; color: #475569; flex-shrink: 0;
}
.nav-item--active .nav-icon { background: #dbeafe; color: #2563eb; }

.sidebar-footer { padding: 12px 16px; border-top: 1px solid #e2e8f0; }
.data-badge {
  font-size: 11px; padding: 4px 8px; border-radius: 4px;
  margin-bottom: 10px; background: #f1f5f9; color: #64748b;
  font-weight: 500;
}
.badge--loading { background: #fffbeb; color: #b45309; }
.badge--error   { background: #fef2f2; color: #b91c1c; }
.badge--ok      { background: #f0fdf4; color: #15803d; }

.dataset-legend { display: flex; flex-direction: column; gap: 4px; }
.leg { font-size: 11px; color: #94a3b8; display: flex; align-items: center; gap: 5px; }
.leg::before { content: ''; width: 8px; height: 8px; border-radius: 50%; }
.leg.filah::before      { background: #d97706; }
.leg.trout::before      { background: #2563eb; }
.leg.journalist::before { background: #059669; }

/* ── 主区域 ── */
.main { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.topbar {
  height: 52px; flex-shrink: 0;
  background: #ffffff; border-bottom: 1px solid #e2e8f0;
  padding: 0 24px; display: flex; align-items: center;
  box-shadow: 0 1px 0 #e2e8f0;
}
.page-title { font-size: 15px; font-weight: 700; color: #1e293b; margin: 0; }
.content { flex: 1; overflow-y: auto; padding: 24px; background: #f8fafc; }

/* 路由动画 */
.fade-enter-active, .fade-leave-active { transition: opacity 0.15s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>

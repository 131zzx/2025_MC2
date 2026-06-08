<template>
  <div class="layout">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="logo">
        <span class="logo-icon">⚖</span>
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
  { to: '/q1', icon: '📊', label: 'Q1 · 数据集自证分析' },
  { to: '/q2', icon: '⏱', label: 'Q2 · 时间分配与偏袒' },
  { to: '/q3', icon: '⇄',  label: 'Q3 · 不完整 vs 全量' },
  { to: '/q4', icon: '👤', label: 'Q4 · 人物级对比' },
]

const currentTitle = computed(() => (route.meta as any).title ?? 'COOTEFOO 可视化分析')

const statusClass = computed(() => ({
  'badge--loading': dataStore.loading,
  'badge--error':   !!dataStore.error,
  'badge--ok':      dataStore.loaded,
}))

const statusText = computed(() => {
  if (dataStore.loading) return '⏳ 加载数据中…'
  if (dataStore.error)   return '✗ 数据加载失败'
  if (dataStore.loaded)  return '✓ 数据已就绪'
  return '待加载'
})

onMounted(() => dataStore.loadAll())
</script>

<style scoped>
.layout { display: flex; height: 100vh; overflow: hidden; }

/* ── 侧边栏 ── */
.sidebar {
  width: 220px;
  flex-shrink: 0;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 16px 16px;
  border-bottom: 1px solid var(--color-border);
}
.logo-icon { font-size: 22px; }
.logo-title { font-size: 13px; font-weight: 700; color: var(--color-text); }
.logo-sub   { font-size: 10px; color: var(--color-text-muted); line-height: 1.4; }

.nav { flex: 1; padding: 12px 8px; display: flex; flex-direction: column; gap: 2px; }
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  text-decoration: none;
  color: var(--color-text-muted);
  font-size: 13px;
  transition: all 0.15s;
}
.nav-item:hover { background: rgba(255,255,255,0.06); color: var(--color-text); }
.nav-item--active { background: rgba(59,130,246,0.15); color: #60a5fa; font-weight: 600; }
.nav-icon { font-size: 15px; width: 20px; text-align: center; }

.sidebar-footer { padding: 12px 16px; border-top: 1px solid var(--color-border); }
.data-badge {
  font-size: 11px;
  padding: 4px 8px;
  border-radius: 4px;
  margin-bottom: 10px;
  background: rgba(255,255,255,0.05);
  color: var(--color-text-muted);
}
.badge--loading { color: #f59e0b; }
.badge--error   { color: #ef4444; }
.badge--ok      { color: #10b981; }

.dataset-legend { display: flex; flex-direction: column; gap: 3px; }
.leg { font-size: 11px; color: var(--color-text-muted); }
.leg.filah      { color: #f59e0b; }
.leg.trout      { color: #3b82f6; }
.leg.journalist { color: #10b981; }

/* ── 主区域 ── */
.main { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.topbar {
  height: 52px;
  flex-shrink: 0;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  padding: 0 24px;
  display: flex;
  align-items: center;
}
.page-title { font-size: 15px; font-weight: 600; color: var(--color-text); margin: 0; }
.content { flex: 1; overflow-y: auto; padding: 24px; }

/* 路由动画 */
.fade-enter-active, .fade-leave-active { transition: opacity 0.18s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>

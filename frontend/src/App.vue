<template>
  <div class="layout">
    <!-- 侧边栏：仅导航 -->
    <aside class="sidebar">
      <div class="logo">
        <div class="logo-badge">MC2</div>
        <div>
          <div class="logo-title">COOTEFOO 偏见分析</div>
          <div class="logo-sub">VAST 2025 · Mini-Challenge 2</div>
        </div>
      </div>

      <nav class="nav">
        <button
          v-for="tab in tabs" :key="tab.id"
          class="nav-item" :class="{ 'nav-item--active': activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          <div class="nav-icon">{{ tab.icon }}</div>
          <div class="nav-text">
            <span class="nav-label">{{ tab.label }}</span>
            <span class="nav-desc">{{ tab.desc }}</span>
          </div>
        </button>
      </nav>

      <!-- 数据状态 -->
      <div class="sidebar-footer">
        <div class="data-badge" :class="statusClass">{{ statusText }}</div>
      </div>
    </aside>

    <!-- 主内容区 -->
    <div class="main">
      <main class="content">
        <div v-if="dataStore.loading" class="spinner-wrap">
          <div class="spinner" /><span>数据加载中...</span>
        </div>
        <div v-else-if="dataStore.error" class="alert-error">{{ dataStore.error }}</div>
        <template v-else>
          <transition name="tab-fade" mode="out-in">
            <component :is="currentTabComponent" :key="activeTab" />
          </transition>
        </template>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, defineAsyncComponent } from 'vue'
import { useDataStore } from './stores/dataStore'

const dataStore = useDataStore()
onMounted(() => dataStore.loadAll())

const tabs = [
  { id: 'bias',   icon: '⊖', label: '偏见全景', desc: '采样偏见与数据集对比' },
  { id: 'member', icon: '◈', label: '委员行为', desc: '个体活动与情感分析' },
  { id: 'trip',   icon: '◎', label: '行程地图', desc: '时空分布与地域关联' },
]

const activeTab = ref('bias')

const tabComponents: Record<string, any> = {
  bias:   defineAsyncComponent(() => import('./views/BiasView.vue')),
  member: defineAsyncComponent(() => import('./views/MemberView.vue')),
  trip:   defineAsyncComponent(() => import('./views/TripView.vue')),
}
const currentTabComponent = computed(() => tabComponents[activeTab.value])

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
</script>

<style scoped>
.layout { display: flex; height: 100vh; overflow: hidden; background: #f1f5f9; }

.sidebar {
  width: 200px; flex-shrink: 0;
  background: #ffffff; border-right: 1px solid #e2e8f0;
  display: flex; flex-direction: column;
}

.logo {
  display: flex; align-items: center; gap: 10px;
  padding: 16px 14px 12px; border-bottom: 1px solid #f1f5f9;
}
.logo-badge {
  font-size: 10px; font-weight: 800; letter-spacing: .06em;
  background: #1e293b; color: #fff; padding: 5px 6px; border-radius: 6px; flex-shrink: 0;
}
.logo-title { font-size: 11.5px; font-weight: 700; color: #1e293b; line-height: 1.3; }
.logo-sub   { font-size: 9px; color: #94a3b8; margin-top: 1px; }

.nav { padding: 10px 8px; display: flex; flex-direction: column; gap: 3px; flex: 1; }
.nav-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border-radius: 10px;
  border: none; background: transparent; cursor: pointer;
  text-align: left; transition: all .12s; width: 100%;
}
.nav-item:hover { background: #f8fafc; }
.nav-item--active { background: #eff6ff; }
.nav-icon {
  font-size: 14px; width: 28px; height: 28px; border-radius: 7px;
  display: flex; align-items: center; justify-content: center;
  background: #f1f5f9; flex-shrink: 0;
}
.nav-item--active .nav-icon { background: #dbeafe; color: #2563eb; }
.nav-text { display: flex; flex-direction: column; }
.nav-label { font-size: 13px; font-weight: 600; color: #374151; }
.nav-item--active .nav-label { color: #2563eb; }
.nav-desc { font-size: 10px; color: #94a3b8; margin-top: 1px; }

.sidebar-footer { padding: 12px; border-top: 1px solid #f1f5f9; }
.data-badge { font-size: 11px; padding: 5px 8px; border-radius: 5px; background: #f1f5f9; color: #64748b; }
.badge--loading { background: #fffbeb; color: #b45309; }
.badge--error   { background: #fef2f2; color: #b91c1c; }
.badge--ok      { background: #f0fdf4; color: #15803d; }

.main { flex: 1; overflow: hidden; display: flex; flex-direction: column; min-width: 0; }
.content { flex: 1; overflow-y: auto; }

.spinner-wrap {
  display: flex; align-items: center; justify-content: center; gap: 10px;
  height: 100%; font-size: 13px; color: #64748b;
}
.alert-error {
  margin: 24px; padding: 14px; background: #fef2f2; border: 1px solid #fecaca;
  border-radius: 8px; color: #b91c1c; font-size: 13px;
}

.tab-fade-enter-active, .tab-fade-leave-active { transition: opacity .12s; }
.tab-fade-enter-from, .tab-fade-leave-to { opacity: 0; }
</style>

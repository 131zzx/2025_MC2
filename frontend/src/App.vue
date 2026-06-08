<template>
  <a-layout style="min-height: 100vh">
    <!-- 侧边导航 -->
    <a-layout-sider :width="220" style="position: fixed; height: 100vh; overflow: auto; left: 0; top: 0; z-index: 100">
      <div class="logo">
        <div class="logo-icon">⚖</div>
        <div class="logo-text">
          <div class="logo-title">COOTEFOO</div>
          <div class="logo-sub">偏见可视化分析</div>
        </div>
      </div>

      <a-menu
        v-model:selectedKeys="selectedKeys"
        mode="inline"
        :items="menuItems"
        @click="handleMenuClick"
      />

      <!-- 数据加载状态 -->
      <div class="data-status">
        <template v-if="dataStore.loading.value">
          <a-spin size="small" />
          <span>加载数据中...</span>
        </template>
        <template v-else-if="dataStore.error.value">
          <span style="color: #ef4444">数据加载失败</span>
        </template>
        <template v-else-if="dataStore.loaded.value">
          <span style="color: #10b981">✓ 数据已就绪</span>
        </template>
      </div>
    </a-layout-sider>

    <!-- 主内容区 -->
    <a-layout style="margin-left: 220px">
      <!-- 顶部栏 -->
      <a-layout-header class="top-header">
        <span class="page-title">{{ currentTitle }}</span>
        <div class="header-tags">
          <a-tag color="#f59e0b">FILAH</a-tag>
          <a-tag color="#3b82f6">TROUT</a-tag>
          <a-tag color="#10b981">journalist</a-tag>
        </div>
      </a-layout-header>

      <!-- 路由视图 -->
      <a-layout-content class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useDataStore } from './stores/dataStore'
import {
  BarChartOutlined,
  ClockCircleOutlined,
  SwapOutlined,
  UserOutlined,
} from '@ant-design/icons-vue'
import { h } from 'vue'

const router = useRouter()
const route  = useRoute()
const dataStore = useDataStore()

const selectedKeys = ref<string[]>(['Q1'])

const menuItems = [
  {
    key: 'Q1',
    icon: () => h(BarChartOutlined),
    label: 'Q1 · 数据集自证分析',
    title: 'Q1',
  },
  {
    key: 'Q2',
    icon: () => h(ClockCircleOutlined),
    label: 'Q2 · 时间分配与偏袒',
    title: 'Q2',
  },
  {
    key: 'Q3',
    icon: () => h(SwapOutlined),
    label: 'Q3 · 不完整 vs 全量',
    title: 'Q3',
  },
  {
    key: 'Q4',
    icon: () => h(UserOutlined),
    label: 'Q4 · 人物级对比',
    title: 'Q4',
  },
]

const currentTitle = computed(() => {
  const meta = route.meta as { title?: string }
  return meta.title ?? 'COOTEFOO 可视化分析'
})

function handleMenuClick({ key }: { key: string }) {
  router.push(`/${key.toLowerCase()}`)
}

// 路由变化时同步菜单高亮
watch(() => route.name, (name) => {
  if (name) selectedKeys.value = [String(name)]
}, { immediate: true })

// 应用启动时加载数据
onMounted(() => {
  dataStore.loadAll()
})
</script>

<style scoped>
.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 16px 16px;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 8px;
}
.logo-icon {
  font-size: 24px;
}
.logo-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: 0.05em;
}
.logo-sub {
  font-size: 11px;
  color: var(--color-text-muted);
}
.data-status {
  position: absolute;
  bottom: 16px;
  left: 0;
  width: 100%;
  padding: 0 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--color-text-muted);
}
.top-header {
  background: var(--color-surface) !important;
  border-bottom: 1px solid var(--color-border);
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  position: sticky;
  top: 0;
  z-index: 10;
}
.page-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text);
}
.header-tags {
  display: flex;
  gap: 8px;
}
.main-content {
  padding: 24px;
  min-height: calc(100vh - 56px);
}
/* 路由切换动画 */
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>

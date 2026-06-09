<template>
  <div class="layout">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="logo">
        <span class="logo-icon">MC2</span>
        <div>
          <div class="logo-title">COOTEFOO 偏见分析</div>
          <div class="logo-sub">VAST 2025 · Mini-Challenge 2</div>
        </div>
      </div>

      <!-- 主导航 -->
      <nav class="nav">
        <button
          v-for="tab in tabs" :key="tab.id"
          class="nav-item" :class="activeTab === tab.id && 'nav-item--active'"
          @click="activeTab = tab.id"
        >
          <span class="nav-icon">{{ tab.icon }}</span>
          <div class="nav-text">
            <span class="nav-label">{{ tab.label }}</span>
            <span class="nav-desc">{{ tab.desc }}</span>
          </div>
        </button>
      </nav>

      <!-- 全局过滤面板 -->
      <div class="filter-panel" v-if="dataStore.loaded">
        <!-- 数据集切换 -->
        <div class="filter-section">
          <div class="filter-title">数据集</div>
          <div class="ds-toggles">
            <button
              v-for="ds in allDatasets" :key="ds.key"
              class="ds-btn" :class="[`ds-btn--${ds.key}`, linking.isDatasetActive(ds.key) && 'ds-btn--on']"
              @click="linking.toggleDataset(ds.key)"
            >
              <span class="ds-dot" :style="{ background: ds.color }" />
              {{ ds.label }}
            </button>
          </div>
        </div>

        <!-- 成员过滤 -->
        <div class="filter-section">
          <div class="filter-title">
            委员会成员
            <button v-if="linking.selectedMember" class="clear-btn" @click="linking.selectMember(null)">清除</button>
          </div>
          <div class="member-list">
            <button
              v-for="m in COMMITTEE_MEMBERS" :key="m"
              class="member-btn"
              :class="{
                'member-btn--selected': linking.selectedMember === m,
                'member-btn--dimmed': linking.isMemberDimmed(m),
              }"
              @click="linking.selectMember(m)"
              @mouseenter="linking.setHoveredMember(m)"
              @mouseleave="linking.setHoveredMember(null)"
            >{{ shortName(m) }}</button>
          </div>
        </div>

        <!-- 行业过滤 -->
        <div class="filter-section">
          <div class="filter-title">
            行业
            <button v-if="linking.selectedIndustry" class="clear-btn" @click="linking.selectIndustry(null)">清除</button>
          </div>
          <div class="ind-toggles">
            <button
              v-for="ind in industries" :key="ind.key"
              class="ind-btn" :class="linking.selectedIndustry === ind.key && 'ind-btn--on'"
              :style="{ '--ind-color': ind.color }"
              @click="linking.selectIndustry(ind.key)"
            >{{ ind.label }}</button>
          </div>
        </div>
      </div>

      <!-- 数据状态 -->
      <div class="sidebar-footer">
        <div class="data-badge" :class="statusClass">{{ statusText }}</div>
        <button v-if="linking.selectedMember || linking.selectedIndustry" class="reset-btn" @click="linking.clearAll()">
          重置所有过滤
        </button>
      </div>
    </aside>

    <!-- 主内容区 -->
    <div class="main">
      <header class="topbar">
        <div class="tab-breadcrumb">
          <span class="breadcrumb-icon">{{ currentTab.icon }}</span>
          <span class="breadcrumb-title">{{ currentTab.label }}</span>
          <span class="breadcrumb-sep">—</span>
          <span class="breadcrumb-desc">{{ currentTab.fullDesc }}</span>
        </div>
        <div class="topbar-filters" v-if="linking.selectedMember || linking.selectedIndustry">
          <span class="active-filter" v-if="linking.selectedMember">
            成员：{{ linking.selectedMember }}
            <button @click="linking.selectMember(null)">×</button>
          </span>
          <span class="active-filter" v-if="linking.selectedIndustry">
            行业：{{ linking.selectedIndustry }}
            <button @click="linking.selectIndustry(null)">×</button>
          </span>
        </div>
      </header>

      <main class="content">
        <div v-if="dataStore.loading" class="spinner-wrap">
          <div class="spinner" /><span>数据加载中...</span>
        </div>
        <div v-else-if="dataStore.error" class="alert alert-danger">{{ dataStore.error }}</div>
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
import { uselinkingStore } from './stores/linkingStore'
import { COMMITTEE_MEMBERS, DATASET_COLORS, INDUSTRY_COLORS, INDUSTRY_LABELS } from './types'

const dataStore = useDataStore()
const linking   = uselinkingStore()

onMounted(() => dataStore.loadAll())

// ── Tab 定义 ──────────────────────────────────────────────
const tabs = [
  {
    id: 'bias',
    icon: '⊖',
    label: '偏见全景',
    desc: '数据集采样偏见分析',
    fullDesc: '对比三个数据集的采样偏见与话题行业构成，评估各方数据的可靠性',
  },
  {
    id: 'member',
    icon: '◈',
    label: '委员行为',
    desc: '个体活动与情感分析',
    fullDesc: '分析每位委员会成员的活动模式、情感倾向与跨数据集表现差异',
  },
  {
    id: 'trip',
    icon: '◎',
    label: '行程地图',
    desc: '时空分布与地域关联',
    fullDesc: '可视化委员会成员的行程轨迹与地域偏好，结合时间轴分析旅行规律',
  },
]

const activeTab = ref('bias')
const currentTab = computed(() => tabs.find(t => t.id === activeTab.value) ?? tabs[0])

const tabComponents: Record<string, any> = {
  bias:   defineAsyncComponent(() => import('./views/BiasView.vue')),
  member: defineAsyncComponent(() => import('./views/MemberView.vue')),
  trip:   defineAsyncComponent(() => import('./views/TripView.vue')),
}
const currentTabComponent = computed(() => tabComponents[activeTab.value])

// ── 数据集定义 ────────────────────────────────────────────
const allDatasets = [
  { key: 'filah'      as const, label: 'FILAH',    color: DATASET_COLORS.filah },
  { key: 'trout'      as const, label: 'TROUT',    color: DATASET_COLORS.trout },
  { key: 'journalist' as const, label: '记者',     color: DATASET_COLORS.journalist },
]

// ── 行业定义 ──────────────────────────────────────────────
const industries = [
  { key: 'fishing', label: '渔业',   color: INDUSTRY_COLORS.fishing },
  { key: 'tourism', label: '旅游',   color: INDUSTRY_COLORS.tourism },
  { key: 'mixed',   label: '混合',   color: INDUSTRY_COLORS.mixed },
  { key: 'neutral', label: '中立',   color: INDUSTRY_COLORS.neutral },
]

// ── 状态显示 ──────────────────────────────────────────────
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

function shortName(name: string): string {
  // 姓名缩短显示
  const parts = name.split(' ')
  if (parts.length >= 2) return parts[0][0] + '. ' + parts[parts.length - 1]
  return name
}
</script>

<style scoped>
.layout { display: flex; height: 100vh; overflow: hidden; background: #f8fafc; }

/* ── 侧边栏 ── */
.sidebar {
  width: 240px; flex-shrink: 0;
  background: #ffffff; border-right: 1px solid #e2e8f0;
  display: flex; flex-direction: column; overflow-y: auto; overflow-x: hidden;
}

.logo {
  display: flex; align-items: center; gap: 10px;
  padding: 18px 16px 14px; border-bottom: 1px solid #e2e8f0; flex-shrink: 0;
}
.logo-icon {
  font-size: 10px; font-weight: 800; letter-spacing: .04em;
  background: #1e293b; color: #fff; padding: 5px 6px; border-radius: 6px; flex-shrink: 0;
}
.logo-title { font-size: 12px; font-weight: 700; color: #1e293b; }
.logo-sub   { font-size: 9px; color: #94a3b8; margin-top: 1px; }

/* 导航 */
.nav { padding: 10px 8px; display: flex; flex-direction: column; gap: 3px; flex-shrink: 0; }
.nav-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border-radius: 10px;
  border: none; background: transparent; cursor: pointer;
  text-align: left; transition: all .15s; width: 100%;
}
.nav-item:hover { background: #f1f5f9; }
.nav-item--active { background: #eff6ff; }
.nav-icon {
  font-size: 16px; width: 28px; height: 28px; border-radius: 7px;
  display: flex; align-items: center; justify-content: center;
  background: #f1f5f9; color: #64748b; flex-shrink: 0; font-style: normal;
}
.nav-item--active .nav-icon { background: #dbeafe; color: #2563eb; }
.nav-text { display: flex; flex-direction: column; gap: 1px; }
.nav-label { font-size: 13px; font-weight: 600; color: #374151; }
.nav-item--active .nav-label { color: #2563eb; }
.nav-desc { font-size: 10px; color: #94a3b8; }

/* 过滤面板 */
.filter-panel {
  flex: 1; padding: 0 12px 12px; overflow-y: auto;
  border-top: 1px solid #f1f5f9;
}
.filter-section { padding: 10px 0; border-bottom: 1px solid #f1f5f9; }
.filter-section:last-child { border-bottom: none; }
.filter-title {
  font-size: 10px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase;
  color: #94a3b8; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between;
}
.clear-btn {
  font-size: 10px; color: #64748b; background: none; border: none; cursor: pointer;
  padding: 1px 4px; border-radius: 3px; text-transform: none; letter-spacing: 0;
}
.clear-btn:hover { background: #fee2e2; color: #dc2626; }

/* 数据集切换 */
.ds-toggles { display: flex; flex-direction: column; gap: 4px; }
.ds-btn {
  display: flex; align-items: center; gap: 8px; padding: 6px 10px; border-radius: 7px;
  border: 1px solid #e2e8f0; background: #f8fafc; cursor: pointer;
  font-size: 12px; font-weight: 500; color: #64748b; transition: all .15s;
}
.ds-btn:hover { border-color: #cbd5e1; background: #f1f5f9; }
.ds-btn--on { border-color: transparent; background: #f0f9ff; color: #1e293b; font-weight: 600; }
.ds-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }

/* 成员列表 */
.member-list { display: flex; flex-wrap: wrap; gap: 4px; }
.member-btn {
  padding: 4px 8px; border-radius: 5px; border: 1px solid #e2e8f0;
  background: #f8fafc; cursor: pointer; font-size: 11px; color: #475569;
  transition: all .15s; font-weight: 500;
}
.member-btn:hover { border-color: #2563eb; background: #eff6ff; color: #2563eb; }
.member-btn--selected { border-color: #2563eb; background: #dbeafe; color: #1d4ed8; font-weight: 700; }
.member-btn--dimmed { opacity: .4; }

/* 行业切换 */
.ind-toggles { display: flex; flex-wrap: wrap; gap: 4px; }
.ind-btn {
  padding: 4px 9px; border-radius: 5px; border: 1px solid #e2e8f0;
  background: #f8fafc; cursor: pointer; font-size: 11px; color: #475569;
  transition: all .15s;
}
.ind-btn:hover { border-color: var(--ind-color); color: var(--ind-color); background: #fafafa; }
.ind-btn--on { border-color: var(--ind-color); background: color-mix(in srgb, var(--ind-color) 12%, white); color: var(--ind-color); font-weight: 700; }

/* 底部 */
.sidebar-footer {
  padding: 10px 12px; border-top: 1px solid #e2e8f0; flex-shrink: 0;
  display: flex; flex-direction: column; gap: 6px;
}
.data-badge {
  font-size: 11px; padding: 4px 8px; border-radius: 4px;
  background: #f1f5f9; color: #64748b; font-weight: 500;
}
.badge--loading { background: #fffbeb; color: #b45309; }
.badge--error   { background: #fef2f2; color: #b91c1c; }
.badge--ok      { background: #f0fdf4; color: #15803d; }
.reset-btn {
  font-size: 11px; padding: 5px 8px; border-radius: 5px;
  background: #fef2f2; border: 1px solid #fecaca; color: #dc2626;
  cursor: pointer; font-weight: 500;
}
.reset-btn:hover { background: #fee2e2; }

/* ── 主区域 ── */
.main { flex: 1; display: flex; flex-direction: column; overflow: hidden; min-width: 0; }

.topbar {
  height: 50px; flex-shrink: 0; background: #fff;
  border-bottom: 1px solid #e2e8f0; padding: 0 24px;
  display: flex; align-items: center; justify-content: space-between; gap: 16px;
}
.tab-breadcrumb { display: flex; align-items: center; gap: 8px; }
.breadcrumb-icon { font-size: 16px; color: #2563eb; }
.breadcrumb-title { font-size: 14px; font-weight: 700; color: #1e293b; }
.breadcrumb-sep { color: #cbd5e1; }
.breadcrumb-desc { font-size: 12px; color: #64748b; }

.topbar-filters { display: flex; gap: 6px; align-items: center; }
.active-filter {
  display: flex; align-items: center; gap: 4px;
  padding: 3px 8px; border-radius: 5px;
  background: #eff6ff; border: 1px solid #bfdbfe;
  font-size: 11px; color: #1d4ed8; font-weight: 600;
}
.active-filter button {
  background: none; border: none; color: #93c5fd; cursor: pointer;
  font-size: 13px; line-height: 1; padding: 0;
}
.active-filter button:hover { color: #1d4ed8; }

.content { flex: 1; overflow-y: auto; background: #f8fafc; }

/* 切换动画 */
.tab-fade-enter-active, .tab-fade-leave-active { transition: opacity .15s, transform .15s; }
.tab-fade-enter-from { opacity: 0; transform: translateY(8px); }
.tab-fade-leave-to   { opacity: 0; transform: translateY(-4px); }
</style>

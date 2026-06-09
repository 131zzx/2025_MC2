<template>
  <div class="cards-row">
    <div
      v-for="ds in datasets"
      :key="ds.key"
      class="stat-card"
      :class="'stat-card--' + ds.key"
    >
      <div class="card-header">
        <span class="ds-dot" :style="{ background: ds.color }" />
        <span class="ds-name">{{ ds.label }}</span>
        <span class="ds-tag">{{ ds.tag }}</span>
      </div>

      <div class="metrics">
        <div class="metric">
          <div class="m-value">{{ ds.nodes }}</div>
          <div class="m-label">节点总数</div>
        </div>
        <div class="metric">
          <div class="m-value">{{ ds.edges }}</div>
          <div class="m-label">边总数</div>
        </div>
        <div class="metric">
          <div class="m-value" :class="ds.tripHighlight">{{ ds.trips }}</div>
          <div class="m-label">行程记录</div>
        </div>
        <div class="metric">
          <div class="m-value">{{ ds.members }}</div>
          <div class="m-label">覆盖成员</div>
        </div>
      </div>

      <!-- 完整度进度条 -->
      <div class="completeness">
        <div class="c-label">
          <span>相对完整度</span>
          <span class="c-pct">{{ ds.completeness }}%</span>
        </div>
        <div class="c-bar">
          <div
            class="c-fill"
            :style="{ width: ds.completeness + '%', background: ds.color }"
          />
        </div>
      </div>

      <!-- 偏向标签 -->
      <div class="bias-tag" :style="{ borderColor: ds.biasColor, color: ds.biasColor }">
        {{ ds.biasLabel }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { NodeTypeCountItem } from '../../types'

const props = defineProps<{ nodeTypes: NodeTypeCountItem[] }>()

function getCount(ds: string, type: string) {
  return props.nodeTypes.find(d => d.dataset === ds && d.node_type === type)?.count ?? 0
}

const datasets = [
  {
    key: 'filah', label: 'FILAH', tag: '渔业方',
    color: '#f59e0b',
    nodes: 396, edges: 765,
    trips: 189, tripHighlight: 'highlight-high',
    members: '3 / 6', completeness: 54,
    biasLabel: '⚠ 采样偏向：选择性收录行程，成员覆盖不足',
    biasColor: '#f59e0b',
  },
  {
    key: 'trout', label: 'TROUT', tag: '旅游方',
    color: '#3b82f6',
    nodes: 164, edges: 378,
    trips: 18,  tripHighlight: 'highlight-low',
    members: '6 / 6', completeness: 22,
    biasLabel: '⚠ 采样偏向：节点极少，行程记录严重缺失',
    biasColor: '#3b82f6',
  },
  {
    key: 'journalist', label: '记者数据集', tag: '全量基准',
    color: '#10b981',
    nodes: 740, edges: 2436,
    trips: 342, tripHighlight: '',
    members: '6 / 6', completeness: 100,
    biasLabel: '✓ 最接近完整事实，作为对比基准',
    biasColor: '#10b981',
  },
]
</script>

<style scoped>
.cards-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }

.stat-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 18px;
  position: relative;
  transition: transform .15s, box-shadow .15s;
  box-shadow: 0 1px 4px rgba(0,0,0,.06);
}
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,.1); }
.stat-card--filah      { border-top: 3px solid #d97706; }
.stat-card--trout      { border-top: 3px solid #2563eb; }
.stat-card--journalist { border-top: 3px solid #059669; }

.card-header { display: flex; align-items: center; gap: 8px; margin-bottom: 16px; }
.ds-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.ds-name { font-size: 14px; font-weight: 700; color: #1e293b; }
.ds-tag  { font-size: 10px; padding: 2px 6px; border-radius: 4px; background: #f1f5f9; color: #64748b; margin-left: auto; }

.metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 16px; }
.metric { text-align: center; }
.m-value { font-size: 22px; font-weight: 700; color: #1e293b; }
.m-label { font-size: 10px; color: #94a3b8; margin-top: 2px; }
.highlight-high { color: #d97706; }
.highlight-low  { color: #2563eb; }

.completeness { margin-bottom: 12px; }
.c-label { display: flex; justify-content: space-between; font-size: 11px; color: #64748b; margin-bottom: 5px; }
.c-pct { color: #475569; font-weight: 600; }
.c-bar { height: 6px; background: #f1f5f9; border-radius: 3px; overflow: hidden; }
.c-fill { height: 100%; border-radius: 3px; transition: width .6s ease; }

.bias-tag {
  font-size: 10px; padding: 6px 8px; border-radius: 6px; border: 1px solid;
  background: #f8fafc; line-height: 1.5;
}
</style>

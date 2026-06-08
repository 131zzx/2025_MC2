<template>
  <div>
    <div class="filter-row">
      <span class="hint">仅显示与 <strong>{{ member }}</strong> 相关的缺失证据（旅游类优先）</span>
    </div>
    <div class="table-wrap">
      <table v-if="topItems.length">
        <thead>
          <tr>
            <th>#</th>
            <th>节点 ID</th>
            <th>类型</th>
            <th>产业</th>
            <th>影响</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, i) in topItems" :key="item.id" :class="'ind-' + item.topic_industry">
            <td>{{ i + 1 }}</td>
            <td class="mono">{{ item.id }}</td>
            <td>{{ item.type }}</td>
            <td :style="{ color: INDUSTRY_COLORS[item.topic_industry as keyof typeof INDUSTRY_COLORS] }">
              {{ INDUSTRY_LABELS[item.topic_industry as keyof typeof INDUSTRY_LABELS] ?? item.topic_industry }}
            </td>
            <td class="impact">
              {{ getImpact(item) }}
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty">该成员在 TROUT 中无明显缺失证据</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { MissingNode } from '../../types'
import { INDUSTRY_COLORS, INDUSTRY_LABELS } from '../../types'

const props = defineProps<{
  missing: MissingNode[]
  member:  string
}>()

// 旅游 > 渔业 > 混合 > 其他，取前10
const topItems = computed(() => {
  const order: Record<string, number> = { tourism: 0, fishing: 1, mixed: 2, neutral: 3, unknown: 4 }
  return [...props.missing]
    .filter(d => d.type === 'trip' || d.type === 'discussion' || d.type === 'plan')
    .sort((a, b) => (order[a.topic_industry] ?? 5) - (order[b.topic_industry] ?? 5))
    .slice(0, 10)
})

function getImpact(item: MissingNode): string {
  if (item.type === 'trip' && item.topic_industry === 'tourism') return '遗漏旅游实地调研'
  if (item.type === 'trip' && item.topic_industry === 'fishing') return '遗漏渔业实地调研'
  if (item.type === 'discussion') return '遗漏议题讨论参与'
  if (item.type === 'plan') return '遗漏行动计划参与'
  return '节点缺失'
}
</script>

<style scoped>
.filter-row { margin-bottom: 8px; font-size: 12px; color: var(--color-text-muted); }
.filter-row strong { color: var(--color-text); }
.table-wrap { overflow-y: auto; max-height: 220px; }
table { width: 100%; border-collapse: collapse; font-size: 11px; }
th { position: sticky; top: 0; background: var(--color-surface); color: var(--color-text-muted); padding: 5px 6px; text-align: left; border-bottom: 1px solid var(--color-border); font-weight: 600; }
td { padding: 4px 6px; border-bottom: 1px solid rgba(51,65,85,0.3); color: var(--color-text-muted); }
.mono { font-family: monospace; font-size: 10px; max-width: 160px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.impact { font-size: 11px; color: var(--color-text); }
.ind-tourism td:first-child { border-left: 3px solid #16a34a; }
.ind-fishing td:first-child { border-left: 3px solid #0369a1; }
.empty { font-size: 13px; color: var(--color-text-muted); text-align: center; padding: 20px; }
</style>

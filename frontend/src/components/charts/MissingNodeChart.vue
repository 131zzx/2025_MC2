<template>
  <div>
    <div ref="chartEl" style="width: 100%; height: 180px" />
    <div class="summary">
      <span>共 <strong>{{ data.length }}</strong> 个缺失节点</span>
      <span v-for="(cnt, ind) in industryCount" :key="ind" class="ind-tag" :style="{ color: INDUSTRY_COLORS[ind as keyof typeof INDUSTRY_COLORS] }">
        {{ INDUSTRY_LABELS[ind as keyof typeof INDUSTRY_LABELS] }}: {{ cnt }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import type { MissingNode } from '../../types'
import { INDUSTRY_COLORS, INDUSTRY_LABELS } from '../../types'

const props = defineProps<{
  data: MissingNode[]
  dataset: 'filah' | 'trout'
}>()

const chartEl = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

const industryCount = computed(() => {
  const cnt: Record<string, number> = {}
  props.data.forEach(d => {
    const ind = d.topic_industry || 'unknown'
    cnt[ind] = (cnt[ind] ?? 0) + 1
  })
  return cnt
})

function render() {
  if (!chart) return
  const entries = Object.entries(industryCount.value)
  const pieData = entries.map(([ind, cnt]) => ({
    name: INDUSTRY_LABELS[ind as keyof typeof INDUSTRY_LABELS] ?? ind,
    value: cnt,
    itemStyle: { color: INDUSTRY_COLORS[ind as keyof typeof INDUSTRY_COLORS] ?? '#888' },
  }))

  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    series: [{
      type: 'pie',
      radius: ['35%', '65%'],
      center: ['50%', '50%'],
      data: pieData,
      label: { color: '#94a3b8', fontSize: 11 },
      labelLine: { lineStyle: { color: '#334155' } },
    }],
  })
}

onMounted(() => {
  chart = echarts.init(chartEl.value!, 'dark')
  render()
  window.addEventListener('resize', () => chart?.resize())
})
watch(() => props.data, render, { deep: true })
</script>

<style scoped>
.summary {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 12px;
  color: var(--color-text-muted);
  margin-top: 8px;
}
.summary strong { color: var(--color-text); }
.ind-tag { font-weight: 600; }
</style>

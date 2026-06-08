<template>
  <div ref="chartEl" style="width: 100%; height: 260px" />
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import type { NodeTypeCountItem } from '../../types'
import { DATASET_COLORS, DATASET_LABELS } from '../../types'

const props = defineProps<{ data: NodeTypeCountItem[] }>()
const chartEl = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

const NODE_COLORS: Record<string, string> = {
  trip:                '#f59e0b',
  meeting:             '#3b82f6',
  discussion:          '#8b5cf6',
  plan:                '#06b6d4',
  topic:               '#10b981',
  place:               '#64748b',
  'entity.person':     '#ec4899',
  'entity.organization':'#f97316',
}

function render() {
  if (!chart || !props.data.length) return

  const nodeTypes = [...new Set(props.data.map(d => d.node_type))]
  const datasets  = [...new Set(props.data.map(d => d.dataset))]

  const series = nodeTypes.map(nt => ({
    name: nt,
    type: 'bar',
    stack: 'total',
    barMaxWidth: 50,
    itemStyle: { color: NODE_COLORS[nt] ?? '#888' },
    data: datasets.map(ds => {
      const item = props.data.find(d => d.dataset === ds && d.node_type === nt)
      return item?.count ?? 0
    }),
  }))

  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: {
      top: 0, textStyle: { color: '#94a3b8', fontSize: 10 },
      itemWidth: 10, itemHeight: 8,
    },
    grid: { left: 16, right: 16, top: 36, bottom: 8, containLabel: true },
    xAxis: {
      type: 'category',
      data: datasets.map(d => DATASET_LABELS[d as keyof typeof DATASET_LABELS] ?? d),
      axisLabel: { color: '#94a3b8' },
      axisLine: { lineStyle: { color: '#334155' } },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#1e293b' } },
      axisLabel: { color: '#94a3b8', fontSize: 10 },
    },
    series,
  })
}

onMounted(() => {
  chart = echarts.init(chartEl.value!, 'dark')
  render()
  window.addEventListener('resize', () => chart?.resize())
})
watch(() => props.data, render, { deep: true })
</script>

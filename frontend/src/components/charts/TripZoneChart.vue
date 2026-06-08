<template>
  <div ref="chartEl" style="width: 100%; height: 260px" />
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import type { TripZoneItem } from '../../types'
import { DATASET_LABELS, DATASET_COLORS } from '../../types'

const props = defineProps<{ data: TripZoneItem[] }>()
const chartEl = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

const ZONE_COLORS: Record<string, string> = {
  tourism:     '#16a34a',
  industrial:  '#0369a1',
  commercial:  '#9333ea',
  residential: '#64748b',
  government:  '#f59e0b',
  unknown:     '#374151',
}

function render() {
  if (!chart || !props.data.length) return

  const zones    = [...new Set(props.data.map(d => d.zone || 'unknown'))]
  const datasets = [...new Set(props.data.map(d => d.dataset))]

  const series = zones.map(z => ({
    name: z,
    type: 'bar',
    stack: 'total',
    barMaxWidth: 50,
    itemStyle: { color: ZONE_COLORS[z] ?? '#888' },
    data: datasets.map(ds => {
      const item = props.data.find(d => d.dataset === ds && (d.zone || 'unknown') === z)
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

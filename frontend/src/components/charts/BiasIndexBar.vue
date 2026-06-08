<template>
  <div ref="chartEl" style="width: 100%; height: 260px" />
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import type { BiasIndexItem } from '../../types'
import { DATASET_COLORS, DATASET_LABELS } from '../../types'

const props = defineProps<{
  data: BiasIndexItem[]
  showAll?: boolean
}>()

const chartEl = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

function render() {
  if (!chart || !props.data.length) return

  // 按成员分组，每个成员一组条形
  const members = [...new Set(props.data.map(d => d.member))]
  const datasets = [...new Set(props.data.map(d => d.dataset))]

  const series = datasets.map(ds => ({
    name: DATASET_LABELS[ds as keyof typeof DATASET_LABELS] ?? ds,
    type: 'bar',
    barMaxWidth: 30,
    itemStyle: { color: DATASET_COLORS[ds as keyof typeof DATASET_COLORS] ?? '#888' },
    data: members.map(m => {
      const item = props.data.find(d => d.dataset === ds && d.member === m)
      return item ? +item.bias_index.toFixed(3) : null
    }),
    label: {
      show: true,
      position: 'top',
      formatter: (p: any) => p.value != null ? (p.value >= 0 ? `+${p.value}` : `${p.value}`) : '',
      fontSize: 10,
      color: '#94a3b8',
    },
  }))

  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      formatter: (params: any[]) =>
        params.map(p => `${p.seriesName}: <b>${p.value >= 0 ? '+' : ''}${p.value}</b>`).join('<br/>'),
    },
    legend: {
      top: 0,
      textStyle: { color: '#94a3b8', fontSize: 11 },
      itemWidth: 12, itemHeight: 8,
    },
    grid: { left: 16, right: 16, top: 36, bottom: 40, containLabel: true },
    xAxis: {
      type: 'category',
      data: members,
      axisLabel: { color: '#94a3b8', fontSize: 11, rotate: members.length > 4 ? 20 : 0 },
      axisLine: { lineStyle: { color: '#334155' } },
    },
    yAxis: {
      type: 'value',
      min: -1, max: 1,
      splitLine: { lineStyle: { color: '#1e293b' } },
      axisLabel: { color: '#94a3b8', fontSize: 10,
        formatter: (v: number) => v === 0 ? '均衡' : (v > 0 ? `旅游+${v}` : `渔业${v}`) },
    },
    markLine: { data: [{ yAxis: 0 }] },
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

<template>
  <div ref="chartEl" style="width: 100%; height: 260px" />
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import type { SentimentAggItem } from '../../types'
import { COMMITTEE_MEMBERS, INDUSTRY_LABELS } from '../../types'

const props = defineProps<{ data: SentimentAggItem[] }>()
const chartEl = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

function render() {
  if (!chart || !props.data.length) return

  const industries = ['fishing', 'tourism', 'mixed']
  const members    = [...COMMITTEE_MEMBERS]

  // 构建热力图数据 [xIdx, yIdx, value]
  const heatData: [number, number, number | '-'][] = []
  industries.forEach((ind, yi) => {
    members.forEach((m, xi) => {
      const item = props.data.find(d => d.member === m && d.industry === ind)
      heatData.push([xi, yi, item ? +item.sentiment_mean.toFixed(2) : '-'])
    })
  })

  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      formatter: (p: any) => {
        if (p.data[2] === '-') return `${members[p.data[0]]} × ${INDUSTRY_LABELS[industries[p.data[1]] as keyof typeof INDUSTRY_LABELS]}: 无数据`
        return `${members[p.data[0]]} × ${INDUSTRY_LABELS[industries[p.data[1]] as keyof typeof INDUSTRY_LABELS]}: <b>${p.data[2]}</b>`
      },
    },
    grid: { left: 80, right: 80, top: 16, bottom: 40 },
    xAxis: {
      type: 'category',
      data: members,
      splitArea: { show: true },
      axisLabel: { color: '#94a3b8', fontSize: 10, rotate: 15 },
      axisLine: { lineStyle: { color: '#334155' } },
    },
    yAxis: {
      type: 'category',
      data: industries.map(i => INDUSTRY_LABELS[i as keyof typeof INDUSTRY_LABELS] ?? i),
      splitArea: { show: true },
      axisLabel: { color: '#94a3b8', fontSize: 11 },
      axisLine: { lineStyle: { color: '#334155' } },
    },
    visualMap: {
      min: -1, max: 1,
      calculable: true,
      orient: 'horizontal',
      left: 'center', bottom: 0,
      textStyle: { color: '#94a3b8', fontSize: 10 },
      inRange: { color: ['#0369a1', '#1e293b', '#16a34a'] },
      text: ['旅游偏正', '渔业偏正'],
    },
    series: [{
      type: 'heatmap',
      data: heatData,
      label: { show: true, formatter: (p: any) => p.data[2] === '-' ? '—' : p.data[2], fontSize: 11 },
      emphasis: { itemStyle: { shadowBlur: 10 } },
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

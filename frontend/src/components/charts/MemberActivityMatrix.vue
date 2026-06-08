<template>
  <div ref="chartEl" style="width: 100%; height: 260px" />
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import type { MemberActivityItem } from '../../types'
import { DATASET_COLORS, DATASET_LABELS, COMMITTEE_MEMBERS } from '../../types'

const props = defineProps<{ data: MemberActivityItem[] }>()
const chartEl = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

function render() {
  if (!chart || !props.data.length) return

  const datasets = [...new Set(props.data.map(d => d.dataset))]
  const members  = [...COMMITTEE_MEMBERS]

  const series = datasets.map(ds => ({
    name: DATASET_LABELS[ds as keyof typeof DATASET_LABELS] ?? ds,
    type: 'bar',
    barMaxWidth: 24,
    itemStyle: {
      color: DATASET_COLORS[ds as keyof typeof DATASET_COLORS] ?? '#888',
      opacity: 0.85,
    },
    data: members.map(m => {
      const item = props.data.find(d => d.dataset === ds && d.member === m)
      // 未出现在数据集中的成员显示为灰色条
      if (!item || !item.in_dataset) return { value: 0, itemStyle: { color: '#1e293b', borderColor: '#334155', borderWidth: 1 } }
      return item.total_activity
    }),
  }))

  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any[]) => {
        const member = members[params[0].dataIndex]
        const lines = [`<b>${member}</b>`]
        params.forEach(p => {
          const item = props.data.find(d => d.dataset === p.seriesId && d.member === member)
          if (!item || !item.in_dataset) {
            lines.push(`${p.seriesName}: <span style="color:#ef4444">无记录</span>`)
          } else {
            lines.push(`${p.seriesName}: ${p.value} 条活动`)
          }
        })
        return lines.join('<br/>')
      },
    },
    legend: {
      top: 0, textStyle: { color: '#94a3b8', fontSize: 11 },
      itemWidth: 12, itemHeight: 8,
    },
    grid: { left: 16, right: 16, top: 36, bottom: 8, containLabel: true },
    xAxis: {
      type: 'category',
      data: members,
      axisLabel: { color: '#94a3b8', fontSize: 10, rotate: 15 },
      axisLine: { lineStyle: { color: '#334155' } },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#1e293b' } },
      axisLabel: { color: '#94a3b8', fontSize: 10 },
    },
    series: series.map(s => ({ ...s, id: s.name })),
  })
}

onMounted(() => {
  chart = echarts.init(chartEl.value!, 'dark')
  render()
  window.addEventListener('resize', () => chart?.resize())
})
watch(() => props.data, render, { deep: true })
</script>

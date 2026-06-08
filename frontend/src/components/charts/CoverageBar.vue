<template>
  <div ref="chartEl" style="width: 100%; height: 260px" />
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import type { CoverageItem } from '../../types'
import { COMMITTEE_MEMBERS, DATASET_COLORS } from '../../types'

const props = defineProps<{
  data: CoverageItem[]
  dataset: 'filah' | 'trout'
}>()

const chartEl = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

const filtered = computed(() =>
  props.data.filter(d => d.dataset === props.dataset)
)

function render() {
  if (!chart || !filtered.value.length) return

  // 按覆盖率升序排列（受影响最大的排前面）
  const sorted = [...filtered.value].sort((a, b) => a.coverage - b.coverage)
  const members = sorted.map(d => d.member)
  const values  = sorted.map(d => Math.round(d.coverage * 100))
  const color   = DATASET_COLORS[props.dataset]

  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      formatter: (params: any[]) => {
        const p = params[0]
        const item = sorted[p.dataIndex]
        return `<b>${item.member}</b><br/>覆盖率: ${p.value}%<br/>有记录活动: ${item.overlap_cnt} / ${item.jo_activity_cnt}`
      },
    },
    grid: { left: 16, right: 60, top: 8, bottom: 8, containLabel: true },
    xAxis: {
      type: 'value', max: 100,
      axisLabel: { color: '#94a3b8', formatter: '{value}%' },
      splitLine: { lineStyle: { color: '#1e293b' } },
    },
    yAxis: {
      type: 'category', data: members,
      axisLabel: { color: '#94a3b8', fontSize: 11 },
      axisLine: { lineStyle: { color: '#334155' } },
    },
    series: [{
      type: 'bar',
      barMaxWidth: 22,
      data: values.map(v => ({
        value: v,
        itemStyle: {
          color: v === 0 ? '#ef4444' : v < 20 ? '#f97316' : color,
        },
      })),
      label: {
        show: true, position: 'right',
        formatter: '{c}%',
        color: '#94a3b8', fontSize: 11,
      },
      markLine: {
        data: [{ xAxis: 50, label: { formatter: '50%', color: '#94a3b8' }, lineStyle: { color: '#334155', type: 'dashed' } }],
        symbol: 'none',
      },
    }],
  })
}

onMounted(() => {
  chart = echarts.init(chartEl.value!, 'dark')
  render()
  window.addEventListener('resize', () => chart?.resize())
})
watch([() => props.data, () => props.dataset], render, { deep: true })
</script>

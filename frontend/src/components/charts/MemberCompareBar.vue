<!--
  单个成员跨数据集活动量对比（participant / trip / meeting）
-->
<template>
  <div ref="el" class="d3-chart" />
</template>

<script lang="ts">
export default {}
</script>
<script setup lang="ts">
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import * as d3 from 'd3'
import type { MemberActivityItem } from '../../types'
import { DATASET_COLORS, DATASET_LABELS } from '../../types'

const props = defineProps<{
  data: MemberActivityItem[]
  member: string
}>()

const el = ref<HTMLElement>()

const filtered = computed(() =>
  ['filah', 'trout', 'journalist'].map(ds => {
    const row = props.data.find(d => d.member === props.member && d.dataset === ds)
    return {
      ds,
      label:       DATASET_LABELS[ds as keyof typeof DATASET_LABELS] ?? ds,
      color:       DATASET_COLORS[ds as keyof typeof DATASET_COLORS] ?? '#888',
      participant: row?.participant_cnt  ?? 0,
      trip:        row?.trip_cnt        ?? 0,
      meeting:     row?.meeting_cnt     ?? 0,
      total:       row?.total_activity  ?? 0,
    }
  })
)

const metrics = ['participant', 'trip', 'meeting'] as const
const metricLabels = { participant: '参与讨论', trip: '行程', meeting: '会议' }
const metricColors = { participant: '#8b5cf6', trip: '#f59e0b', meeting: '#3b82f6' }

function draw() {
  if (!el.value) return
  el.value.innerHTML = ''

  const W = el.value.clientWidth || 400
  const H = 220
  const margin = { top: 20, right: 16, bottom: 40, left: 46 }
  const iw = W - margin.left - margin.right
  const ih = H - margin.top - margin.bottom

  const svg = d3.select(el.value).append('svg').attr('width', W).attr('height', H)
  const g   = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

  const datasets = filtered.value.map(d => d.ds)

  // 外层 scale（数据集分组）
  const x0 = d3.scaleBand().domain(datasets).range([0, iw]).padding(0.28)
  // 内层 scale（指标）
  const x1 = d3.scaleBand().domain(metrics).rangeRound([0, x0.bandwidth()]).padding(0.08)

  const maxVal = d3.max(filtered.value, d =>
    Math.max(d.participant, d.trip, d.meeting)
  ) ?? 1
  const y = d3.scaleLinear().domain([0, maxVal * 1.15]).range([ih, 0])

  // 网格线
  g.append('g').attr('class', 'grid')
    .call(d3.axisLeft(y).tickSize(-iw).ticks(4).tickFormat(() => ''))
    .call(ax => ax.select('.domain').remove())
    .call(ax => ax.selectAll('line').attr('stroke', '#f1f5f9'))

  // 每个数据集的组
  const dsGroup = g.selectAll('.ds-group').data(filtered.value).join('g')
    .attr('class', 'ds-group')
    .attr('transform', d => `translate(${x0(d.ds)},0)`)

  // 数据集颜色竖条（背景）
  dsGroup.append('rect')
    .attr('x', 0).attr('y', 0)
    .attr('width', x0.bandwidth()).attr('height', ih)
    .attr('fill', d => d.color).attr('opacity', 0.04).attr('rx', 4)

  // 各指标条
  metrics.forEach(metric => {
    dsGroup.append('rect')
      .attr('x', x1(metric)!)
      .attr('y', d => y(d[metric]))
      .attr('width', x1.bandwidth())
      .attr('height', d => ih - y(d[metric]))
      .attr('fill', metricColors[metric])
      .attr('rx', 3)
      .append('title')
      .text(d => `${d.label} · ${metricLabels[metric]}: ${d[metric]}`)

    // 数值标签
    dsGroup.append('text')
      .attr('x', x1(metric)! + x1.bandwidth() / 2)
      .attr('y', d => y(d[metric]) - 3)
      .attr('text-anchor', 'middle').attr('font-size', 9).attr('fill', '#94a3b8')
      .text(d => d[metric] > 0 ? d[metric] : '')
  })

  // X 轴（数据集名）
  g.append('g').attr('transform', `translate(0,${ih})`)
    .call(d3.axisBottom(x0).tickSize(0)
      .tickFormat(d => DATASET_LABELS[d as keyof typeof DATASET_LABELS] ?? d)
    )
    .call(ax => ax.select('.domain').remove())
    .call(ax => ax.selectAll('text').attr('fill', d => DATASET_COLORS[d as keyof typeof DATASET_COLORS] ?? '#94a3b8')
      .attr('font-size', 11).attr('font-weight', 600).attr('dy', '1.4em'))

  // Y 轴
  g.append('g').call(d3.axisLeft(y).ticks(4))
    .call(ax => ax.select('.domain').remove())
    .call(ax => ax.selectAll('text').attr('fill', '#64748b').attr('font-size', 10))

  // 图例
  const legend = svg.append('g').attr('transform', `translate(${margin.left},${H - 12})`)
  metrics.forEach((m, i) => {
    const lg = legend.append('g').attr('transform', `translate(${i * 80},0)`)
    lg.append('rect').attr('width', 8).attr('height', 8).attr('rx', 2).attr('fill', metricColors[m])
    lg.append('text').attr('x', 11).attr('y', 7).attr('font-size', 9).attr('fill', '#64748b')
      .text(metricLabels[m])
  })
}

const ro = new ResizeObserver(draw)
onMounted(() => { ro.observe(el.value!); draw() })
watch([() => props.data, () => props.member], draw, { deep: true })
onUnmounted(() => ro.disconnect())
</script>

<style scoped>
.d3-chart { width: 100%; }
</style>

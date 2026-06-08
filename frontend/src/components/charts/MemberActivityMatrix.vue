<template>
  <div ref="el" class="d3-chart" />
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as d3 from 'd3'
import type { MemberActivityItem } from '../../types'
import { COMMITTEE_MEMBERS, DATASET_COLORS, DATASET_LABELS } from '../../types'

const props = defineProps<{ data: MemberActivityItem[] }>()
const el = ref<HTMLElement>()

function draw() {
  if (!el.value || !props.data.length) return
  el.value.innerHTML = ''
  const W = el.value.clientWidth || 500
  const H = 240
  const margin = { top: 36, right: 16, bottom: 50, left: 16 }
  const iw = W - margin.left - margin.right
  const ih = H - margin.top - margin.bottom

  const svg = d3.select(el.value).append('svg').attr('width', W).attr('height', H)
  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

  const members  = [...COMMITTEE_MEMBERS]
  const datasets = [...new Set(props.data.map(d => d.dataset))]

  const x0 = d3.scaleBand().domain(members).range([0, iw]).padding(0.2)
  const x1 = d3.scaleBand().domain(datasets).range([0, x0.bandwidth()]).padding(0.08)
  const y  = d3.scaleLinear()
    .domain([0, d3.max(props.data, d => d.total_activity) ?? 10]).nice().range([ih, 0])

  const gMember = g.selectAll('.gm').data(members).join('g')
    .attr('class', 'gm').attr('transform', m => `translate(${x0(m)},0)`)

  datasets.forEach(ds => {
    gMember.append('rect')
      .attr('x', x1(ds)!).attr('width', x1.bandwidth())
      .attr('y', m => {
        const item = props.data.find(d => d.member === m && d.dataset === ds)
        if (!item || !item.in_dataset) return ih - 2
        return y(item.total_activity)
      })
      .attr('height', m => {
        const item = props.data.find(d => d.member === m && d.dataset === ds)
        if (!item || !item.in_dataset) return 2
        return ih - y(item.total_activity)
      })
      .attr('fill', m => {
        const item = props.data.find(d => d.member === m && d.dataset === ds)
        if (!item || !item.in_dataset) return '#ef4444'
        return DATASET_COLORS[ds as keyof typeof DATASET_COLORS] ?? '#888'
      })
      .attr('rx', 2)
      .append('title').text(m => {
        const item = props.data.find(d => d.member === m && d.dataset === ds)
        if (!item || !item.in_dataset) return `${m} / ${DATASET_LABELS[ds as keyof typeof DATASET_LABELS]}: 无记录`
        return `${m} / ${DATASET_LABELS[ds as keyof typeof DATASET_LABELS]}: ${item.total_activity} 条`
      })
  })

  g.append('g').attr('transform', `translate(0,${ih})`)
    .call(d3.axisBottom(x0).tickSize(0))
    .call(ax => ax.select('.domain').attr('stroke', '#334155'))
    .call(ax => ax.selectAll('text').attr('fill', '#94a3b8').attr('font-size', 10).attr('transform', 'rotate(-12)').style('text-anchor', 'end'))

  g.append('g').call(d3.axisLeft(y).ticks(4))
    .call(ax => ax.select('.domain').remove())
    .call(ax => ax.selectAll('line').attr('stroke', '#f1f5f9'))
    .call(ax => ax.selectAll('text').attr('fill', '#94a3b8').attr('font-size', 10))

  // 图例
  const leg = svg.append('g').attr('transform', `translate(${margin.left}, 6)`)
  datasets.forEach((ds, i) => {
    leg.append('rect').attr('x', i * 100).attr('width', 8).attr('height', 8)
      .attr('fill', DATASET_COLORS[ds as keyof typeof DATASET_COLORS]).attr('rx', 1)
    leg.append('text').attr('x', i * 100 + 12).attr('y', 8)
      .attr('fill', '#94a3b8').attr('font-size', 10).text(DATASET_LABELS[ds as keyof typeof DATASET_LABELS] ?? ds)
  })
  // 红色说明
  leg.append('rect').attr('x', datasets.length * 100).attr('width', 8).attr('height', 8).attr('fill', '#ef4444').attr('rx', 1)
  leg.append('text').attr('x', datasets.length * 100 + 12).attr('y', 8).attr('fill', '#94a3b8').attr('font-size', 10).text('无记录')
}

const ro = new ResizeObserver(draw)
onMounted(() => { ro.observe(el.value!); draw() })
watch(() => props.data, draw, { deep: true })
onUnmounted(() => ro.disconnect())
</script>
<style scoped>.d3-chart { width: 100%; }</style>

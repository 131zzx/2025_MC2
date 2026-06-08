<template>
  <div ref="el" class="d3-chart" />
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as d3 from 'd3'
import type { BiasIndexItem } from '../../types'
import { DATASET_COLORS, DATASET_LABELS } from '../../types'

const props = defineProps<{ data: BiasIndexItem[] }>()
const el = ref<HTMLElement>()
let svg: d3.Selection<SVGSVGElement, unknown, null, undefined> | null = null

function draw() {
  if (!el.value || !props.data.length) return
  el.value.innerHTML = ''

  const W = el.value.clientWidth || 500
  const H = 240
  const margin = { top: 30, right: 16, bottom: 50, left: 90 }
  const iw = W - margin.left - margin.right
  const ih = H - margin.top - margin.bottom

  svg = d3.select(el.value).append('svg')
    .attr('width', W).attr('height', H)

  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

  const members  = [...new Set(props.data.map(d => d.member))]
  const datasets = [...new Set(props.data.map(d => d.dataset))]

  const x0 = d3.scaleBand().domain(members).range([0, iw]).padding(0.25)
  const x1 = d3.scaleBand().domain(datasets).range([0, x0.bandwidth()]).padding(0.1)
  const y  = d3.scaleLinear().domain([-1, 1]).range([ih, 0])

  // 零线
  g.append('line').attr('x1', 0).attr('x2', iw)
    .attr('y1', y(0)).attr('y2', y(0))
    .attr('stroke', '#475569').attr('stroke-dasharray', '4 3')

  // 条形
  const gMember = g.selectAll('.gm').data(members).join('g')
    .attr('class', 'gm')
    .attr('transform', m => `translate(${x0(m)},0)`)

  datasets.forEach(ds => {
    gMember.append('rect')
      .attr('x', x1(ds)!)
      .attr('width', x1.bandwidth())
      .attr('y', d => {
        const item = props.data.find(i => i.member === d && i.dataset === ds)
        const v = item?.bias_index ?? 0
        return v >= 0 ? y(v) : y(0)
      })
      .attr('height', d => {
        const item = props.data.find(i => i.member === d && i.dataset === ds)
        const v = item?.bias_index ?? 0
        return Math.abs(y(v) - y(0))
      })
      .attr('fill', DATASET_COLORS[ds as keyof typeof DATASET_COLORS] ?? '#888')
      .attr('rx', 2)
      .append('title').text(d => {
        const item = props.data.find(i => i.member === d && i.dataset === ds)
        return `${d} / ${DATASET_LABELS[ds as keyof typeof DATASET_LABELS]}: ${item?.bias_index.toFixed(3) ?? 'N/A'}`
      })
  })

  // X 轴
  g.append('g').attr('transform', `translate(0,${ih})`)
    .call(d3.axisBottom(x0).tickSize(0))
    .call(ax => ax.select('.domain').attr('stroke', '#334155'))
    .call(ax => ax.selectAll('text')
      .attr('fill', '#94a3b8').attr('font-size', 11)
      .attr('transform', members.length > 4 ? 'rotate(-15)' : '')
      .style('text-anchor', members.length > 4 ? 'end' : 'middle'))

  // Y 轴
  g.append('g')
    .call(d3.axisLeft(y).ticks(5)
      .tickFormat(v => v === 0 ? '均衡' : (Number(v) > 0 ? `旅游 +${v}` : `渔业 ${v}`)))
    .call(ax => ax.select('.domain').remove())
    .call(ax => ax.selectAll('line').attr('stroke', '#1e293b'))
    .call(ax => ax.selectAll('text').attr('fill', '#94a3b8').attr('font-size', 10))

  // 图例
  const leg = svg.append('g').attr('transform', `translate(${margin.left}, 8)`)
  datasets.forEach((ds, i) => {
    leg.append('rect').attr('x', i * 100).attr('width', 10).attr('height', 10)
      .attr('fill', DATASET_COLORS[ds as keyof typeof DATASET_COLORS] ?? '#888').attr('rx', 2)
    leg.append('text').attr('x', i * 100 + 14).attr('y', 9)
      .attr('fill', '#94a3b8').attr('font-size', 11)
      .text(DATASET_LABELS[ds as keyof typeof DATASET_LABELS] ?? ds)
  })
}

const ro = new ResizeObserver(draw)
onMounted(() => { ro.observe(el.value!); draw() })
watch(() => props.data, draw, { deep: true })
onUnmounted(() => ro.disconnect())
</script>

<style scoped>
.d3-chart { width: 100%; }
</style>

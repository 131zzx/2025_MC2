<template>
  <div ref="el" class="d3-chart" />
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as d3 from 'd3'
import type { TripZoneItem } from '../../types'
import { DATASET_LABELS } from '../../types'

const props = defineProps<{ data: TripZoneItem[] }>()
const el = ref<HTMLElement>()
const ZONES = ['tourism', 'commercial', 'residential', 'government', 'industrial', 'unknown']
const ZONE_COLORS: Record<string, string> = {
  tourism: '#16a34a', commercial: '#9333ea', residential: '#64748b',
  government: '#f59e0b', industrial: '#0369a1', unknown: '#374151',
}

function draw() {
  if (!el.value || !props.data.length) return
  el.value.innerHTML = ''
  const W = el.value.clientWidth || 500, H = 240
  const margin = { top: 36, right: 16, bottom: 30, left: 40 }
  const iw = W - margin.left - margin.right, ih = H - margin.top - margin.bottom
  const svg = d3.select(el.value).append('svg').attr('width', W).attr('height', H)
  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

  const datasets = [...new Set(props.data.map(d => d.dataset))]
  const stackData = datasets.map(ds => {
    const row: any = { ds }
    ZONES.forEach(z => { row[z] = props.data.find(d => d.dataset === ds && (d.zone || 'unknown') === z)?.count ?? 0 })
    return row
  })
  const stack = d3.stack<any>().keys(ZONES)
  const series = stack(stackData)
  const x = d3.scaleBand().domain(datasets).range([0, iw]).padding(0.3)
  const y = d3.scaleLinear().domain([0, d3.max(series, s => d3.max(s, d => d[1])) ?? 10]).nice().range([ih, 0])

  series.forEach(s => {
    g.selectAll('rect').data(s).join('rect')
      .attr('x', d => x(d.data.ds)!).attr('y', d => y(d[1]))
      .attr('height', d => Math.max(0, y(d[0]) - y(d[1])))
      .attr('width', x.bandwidth()).attr('fill', ZONE_COLORS[s.key] ?? '#888').attr('rx', 2)
      .append('title').text(d => `${s.key}: ${d[1] - d[0]}`)
  })

  g.append('g').attr('transform', `translate(0,${ih})`)
    .call(d3.axisBottom(x).tickFormat(d => DATASET_LABELS[d as keyof typeof DATASET_LABELS] ?? d).tickSize(0))
    .call(ax => ax.select('.domain').attr('stroke', '#334155'))
    .call(ax => ax.selectAll('text').attr('fill', '#94a3b8').attr('font-size', 12))

  g.append('g').call(d3.axisLeft(y).ticks(5))
    .call(ax => ax.select('.domain').remove())
    .call(ax => ax.selectAll('line').attr('stroke', '#f1f5f9'))
    .call(ax => ax.selectAll('text').attr('fill', '#94a3b8').attr('font-size', 10))

  const leg = svg.append('g').attr('transform', `translate(${margin.left}, 6)`)
  ZONES.forEach((z, i) => {
    leg.append('rect').attr('x', i * 88).attr('width', 8).attr('height', 8).attr('fill', ZONE_COLORS[z]).attr('rx', 1)
    leg.append('text').attr('x', i * 88 + 12).attr('y', 8).attr('fill', '#94a3b8').attr('font-size', 10).text(z)
  })
}

const ro = new ResizeObserver(draw)
onMounted(() => { ro.observe(el.value!); draw() })
watch(() => props.data, draw, { deep: true })
onUnmounted(() => ro.disconnect())
</script>
<style scoped>.d3-chart { width: 100%; }</style>

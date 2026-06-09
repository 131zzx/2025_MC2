<template>
  <div ref="el" class="d3-chart" />
</template>

<script lang="ts">
import { defineComponent } from 'vue'
export default defineComponent({ name: 'TripZoneChart' })
</script>
<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as d3 from 'd3'
import type { TripZoneItem, DatasetKey } from '../../types'
import { DATASET_LABELS } from '../../types'

const props = defineProps<{ data: TripZoneItem[] }>()
const el = ref<HTMLElement>()

const ZONE_LABELS: Record<string, string> = {
  tourism: '旅游', commercial: '商业', residential: '居住',
  government: '政府', industrial: '工业', fishing: '渔业',
  nature: '自然', connector: '连接', unknown: '其他',
}
const ZONE_COLORS: Record<string, string> = {
  tourism: '#16a34a', commercial: '#9333ea', residential: '#64748b',
  government: '#f59e0b', industrial: '#0369a1', fishing: '#0d9488',
  nature: '#22c55e', connector: '#94a3b8', unknown: '#374151',
}

interface StackRow { ds: string; [zone: string]: string | number }

function draw() {
  if (!el.value) return
  el.value.innerHTML = ''

  if (!props.data.length) {
    el.value.innerHTML = '<div class="empty">暂无区域分布数据</div>'
    return
  }

  const W = el.value.clientWidth || 260
  const H = 220
  const margin = { top: 28, right: 8, bottom: 36, left: 36 }
  const iw = W - margin.left - margin.right
  const ih = H - margin.top - margin.bottom

  const svg = d3.select(el.value).append('svg').attr('width', W).attr('height', H)
  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

  const zones = [...new Set(props.data.map(d => d.zone || 'unknown'))]
  const datasets = [...new Set(props.data.map(d => d.dataset))]

  const stackData: StackRow[] = datasets.map(ds => {
    const row: StackRow = { ds }
    zones.forEach(z => {
      row[z] = props.data.find(d => d.dataset === ds && (d.zone || 'unknown') === z)?.count ?? 0
    })
    return row
  })

  const stack = d3.stack<StackRow>().keys(zones)
  const series = stack(stackData)
  const x = d3.scaleBand().domain(datasets).range([0, iw]).padding(0.35)
  const yMax = d3.max(series, s => d3.max(s, d => d[1])) ?? 10
  const y = d3.scaleLinear().domain([0, yMax]).nice().range([ih, 0])

  series.forEach(s => {
    g.selectAll<SVGRectElement, d3.SeriesPoint<StackRow>>(`rect.zone-${s.key}`)
      .data(s)
      .join('rect')
      .attr('class', `zone-${s.key}`)
      .attr('x', d => x(d.data.ds)!)
      .attr('y', d => y(d[1]))
      .attr('height', d => Math.max(0, y(d[0]) - y(d[1])))
      .attr('width', x.bandwidth())
      .attr('fill', ZONE_COLORS[s.key] ?? '#888')
      .attr('rx', 2)
      .append('title')
      .text(d => `${ZONE_LABELS[s.key] ?? s.key}: ${d[1] - d[0]}`)
  })

  const xAxisG = g.append('g').attr('transform', `translate(0,${ih})`)
  xAxisG.call(
    d3.axisBottom(x)
      .tickFormat((d: d3.AxisDomain) => {
        const key = String(d) as DatasetKey
        const label = DATASET_LABELS[key] ?? key
        return label.length > 8 ? label.slice(0, 6) + '…' : label
      })
      .tickSize(0),
  )
  xAxisG.select('.domain')?.attr('stroke', '#e2e8f0')
  xAxisG.selectAll<SVGTextElement, string>('text')
    .attr('fill', '#64748b').attr('font-size', 10)

  const yAxisG = g.append('g')
  yAxisG.call(d3.axisLeft(y).ticks(4).tickSize(-iw))
  yAxisG.select('.domain')?.remove()
  yAxisG.selectAll('.tick line').attr('stroke', '#f1f5f9')
  yAxisG.selectAll<SVGTextElement, number>('text')
    .attr('fill', '#94a3b8').attr('font-size', 9)

  const leg = svg.append('g').attr('transform', `translate(${margin.left}, 4)`)
  zones.slice(0, 4).forEach((z, i) => {
    leg.append('rect').attr('x', i * 52).attr('width', 8).attr('height', 8)
      .attr('fill', ZONE_COLORS[z] ?? '#888').attr('rx', 1)
    leg.append('text').attr('x', i * 52 + 11).attr('y', 8)
      .attr('fill', '#94a3b8').attr('font-size', 9)
      .text(ZONE_LABELS[z] ?? z)
  })
}

const ro = new ResizeObserver(draw)
onMounted(() => { ro.observe(el.value!); draw() })
watch(() => props.data, draw, { deep: true })
onUnmounted(() => ro.disconnect())
</script>
<style scoped>
.d3-chart { width: 100%; min-height: 220px; }
.empty { padding: 40px; text-align: center; color: #94a3b8; font-size: 12px; }
</style>

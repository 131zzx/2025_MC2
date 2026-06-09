<template>
  <div ref="el" class="d3-chart" />
</template>

<script lang="ts">
export default {}
</script>
<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as d3 from 'd3'
import type { SentimentAggItem, Industry } from '../../types'
import { COMMITTEE_MEMBERS, INDUSTRY_LABELS } from '../../types'

const props = defineProps<{
  data: SentimentAggItem[]
  dataset: string
  highlightedMember?: string
}>()

const emit = defineEmits<{
  (e: 'member-click', name: string): void
  (e: 'member-hover', name: string | null): void
}>()

const el = ref<HTMLElement>()

const INDS = ['fishing', 'tourism', 'mixed'] as const

const color = d3.scaleDiverging(d3.interpolateRdBu).domain([-1, 0, 1])

function textColor(val: number): string {
  const rgb = d3.rgb(color(val))
  const lum = (rgb.r * 299 + rgb.g * 587 + rgb.b * 114) / 1000
  return lum > 160 ? '#1e293b' : '#ffffff'
}

function styleXAxisText(
  selection: d3.Selection<SVGTextElement, string, SVGGElement, unknown>,
) {
  selection
    .attr('fill', (member: string) => member === props.highlightedMember ? '#2563eb' : '#475569')
    .attr('font-size', 10)
    .attr('font-weight', (member: string) => member === props.highlightedMember ? 800 : 500)
    .attr('transform', 'rotate(-18)')
    .style('text-anchor', 'end')
    .attr('dy', '0.5em')
    .attr('cursor', 'pointer')
    .on('click', (_ev: MouseEvent, member: string) => emit('member-click', member))
    .on('mouseenter', (_ev: MouseEvent, member: string) => emit('member-hover', member))
    .on('mouseleave', () => emit('member-hover', null))
}

function styleYAxisText(
  selection: d3.Selection<SVGTextElement, string, SVGGElement, unknown>,
) {
  selection
    .attr('fill', '#475569')
    .attr('font-size', 11)
    .attr('font-weight', 600)
}

function draw() {
  if (!el.value) return
  el.value.innerHTML = ''

  const filtered = props.data.filter(d => d.dataset === props.dataset)
  const W = el.value.clientWidth || 560
  const H = 220
  const margin = { top: 20, right: 90, bottom: 64, left: 60 }
  const iw = W - margin.left - margin.right
  const ih = H - margin.top - margin.bottom

  const svg = d3.select(el.value).append('svg').attr('width', W).attr('height', H)
  const g   = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

  const members = [...COMMITTEE_MEMBERS]
  const xScale  = d3.scaleBand().domain(members).range([0, iw]).padding(0.06)
  const yScale  = d3.scaleBand().domain([...INDS]).range([0, ih]).padding(0.06)

  if (!filtered.length) {
    g.append('text').attr('x', iw / 2).attr('y', ih / 2)
      .attr('text-anchor', 'middle').attr('fill', '#94a3b8').attr('font-size', 13)
      .text('该数据集无情感数据')
    return
  }

  INDS.forEach(ind => {
    members.forEach(m => {
      const item = filtered.find(d => d.member === m && d.industry === ind)
      const val  = item?.sentiment_mean ?? null
      const cell = g.append('g')

      cell.append('rect')
        .attr('x', xScale(m)!).attr('y', yScale(ind)!)
        .attr('width', xScale.bandwidth()).attr('height', yScale.bandwidth())
        .attr('fill', val !== null ? color(val) : '#f1f5f9')
        .attr('stroke', '#ffffff').attr('stroke-width', 3)
        .attr('rx', 5)
        .append('title')
        .text(val !== null
          ? `${m}\n${INDUSTRY_LABELS[ind as Industry]}: ${val.toFixed(3)} (n=${item!.count})`
          : `${m} / ${INDUSTRY_LABELS[ind as Industry]}: 无记录`)

      if (val !== null) {
        cell.append('text')
          .attr('x', xScale(m)! + xScale.bandwidth() / 2)
          .attr('y', yScale(ind)! + yScale.bandwidth() / 2 + 4)
          .attr('text-anchor', 'middle')
          .attr('font-size', 11).attr('font-weight', 600)
          .attr('fill', textColor(val))
          .text(val.toFixed(2))
      } else {
        cell.append('text')
          .attr('x', xScale(m)! + xScale.bandwidth() / 2)
          .attr('y', yScale(ind)! + yScale.bandwidth() / 2 + 4)
          .attr('text-anchor', 'middle').attr('font-size', 11).attr('fill', '#cbd5e1')
          .text('—')
      }
    })
  })

  const xAxisG = g.append('g').attr('transform', `translate(0,${ih})`)
  xAxisG.call(d3.axisBottom(xScale).tickSize(0))
  xAxisG.select('.domain')?.remove()
  styleXAxisText(xAxisG.selectAll<SVGTextElement, string>('text'))

  if (props.highlightedMember && xScale(props.highlightedMember) != null) {
    const colX = xScale(props.highlightedMember)!
    g.append('rect')
      .attr('x', colX).attr('y', ih + 1)
      .attr('width', xScale.bandwidth()).attr('height', 3)
      .attr('fill', '#2563eb').attr('rx', 1.5)
  }

  const yAxisG = g.append('g')
  yAxisG.call(
    d3.axisLeft(yScale)
      .tickFormat((d: d3.AxisDomain) => INDUSTRY_LABELS[d as Industry] ?? String(d))
      .tickSize(0),
  )
  yAxisG.select('.domain')?.remove()
  styleYAxisText(yAxisG.selectAll<SVGTextElement, string>('text'))

  const defs = svg.append('defs')
  const grad = defs.append('linearGradient').attr('id', 'hm-grad-v')
    .attr('x1', '0%').attr('x2', '0%').attr('y1', '0%').attr('y2', '100%')
  d3.range(0, 1.01, 0.1).forEach((t: number) => {
    grad.append('stop')
      .attr('offset', `${t * 100}%`)
      .attr('stop-color', color(1 - t * 2))
  })

  const lx = W - margin.right + 12
  const ly = margin.top
  svg.append('rect').attr('x', lx).attr('y', ly).attr('width', 12).attr('height', ih)
    .attr('fill', 'url(#hm-grad-v)').attr('rx', 3)
    .attr('stroke', '#e2e8f0').attr('stroke-width', 1)

  svg.append('text').attr('x', lx + 16).attr('y', ly + 8)
    .attr('fill', '#2563eb').attr('font-size', 9).attr('font-weight', 600).text('+1')
  svg.append('text').attr('x', lx + 16).attr('y', ly + ih / 2 + 4)
    .attr('fill', '#94a3b8').attr('font-size', 9).text('0')
  svg.append('text').attr('x', lx + 16).attr('y', ly + ih - 2)
    .attr('fill', '#dc2626').attr('font-size', 9).attr('font-weight', 600).text('-1')
  svg.append('text').attr('x', lx).attr('y', ly + ih + 14)
    .attr('fill', '#94a3b8').attr('font-size', 8).text('蓝=正向')
  svg.append('text').attr('x', lx).attr('y', ly + ih + 24)
    .attr('fill', '#94a3b8').attr('font-size', 8).text('红=负向')
}

const ro = new ResizeObserver(draw)
onMounted(() => { ro.observe(el.value!); draw() })
watch([() => props.data, () => props.dataset, () => props.highlightedMember], draw, { deep: true })
onUnmounted(() => ro.disconnect())
</script>
<style scoped>.d3-chart { width: 100%; }</style>

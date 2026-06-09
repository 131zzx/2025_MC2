<!--
  所有成员在记者数据集下各行业情感均值汇总条形图
  横向分组条：每位成员一行，渔业/旅游/混合三段
-->
<template>
  <div ref="el" class="summary-chart" />
</template>

<script lang="ts">
export default {}
</script>
<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as d3 from 'd3'
import type { SentimentAggItem } from '../../types'
import { COMMITTEE_MEMBERS, INDUSTRY_COLORS, INDUSTRY_LABELS } from '../../types'

const props = defineProps<{ data: SentimentAggItem[] }>()
const el = ref<HTMLElement>()

const INDS = [
  { key: 'fishing', label: INDUSTRY_LABELS.fishing, color: INDUSTRY_COLORS.fishing },
  { key: 'tourism', label: INDUSTRY_LABELS.tourism, color: INDUSTRY_COLORS.tourism },
  { key: 'mixed',   label: INDUSTRY_LABELS.mixed,   color: INDUSTRY_COLORS.mixed },
]

function draw() {
  if (!el.value) return
  el.value.innerHTML = ''

  const joData = props.data.filter(d => d.dataset === 'journalist')
  const members = [...COMMITTEE_MEMBERS] as string[]

  const W = el.value.clientWidth || 300
  const rowH = 42
  const H = members.length * rowH + 40
  const m = { top: 24, right: 20, bottom: 12, left: 86 }
  const iw = W - m.left - m.right

  const svg = d3.select(el.value).append('svg').attr('width', W).attr('height', H)
  const g = svg.append('g').attr('transform', `translate(${m.left},${m.top})`)

  const xScale = d3.scaleLinear().domain([-1, 1]).range([0, iw]).clamp(true)
  const cx = xScale(0)

  // 列标题
  INDS.forEach((ind, i) => {
    const tickX = xScale(0.33 * (i - 1))
    svg.append('text')
      .attr('x', m.left + tickX).attr('y', m.top - 8)
      .attr('text-anchor', 'middle').attr('font-size', 9).attr('fill', ind.color).attr('font-weight', 700)
      .text(ind.label)
  })

  // 中轴线
  g.append('line').attr('x1', cx).attr('x2', cx).attr('y1', -4).attr('y2', members.length * rowH)
    .attr('stroke', '#e2e8f0').attr('stroke-width', 1)

  members.forEach((member, mi) => {
    const baseY = mi * rowH
    const subH = (rowH - 8) / INDS.length - 2

    // 交替行背景
    g.append('rect').attr('x', -m.left).attr('y', baseY)
      .attr('width', W).attr('height', rowH)
      .attr('fill', mi % 2 === 0 ? '#f8fafc' : '#fff')

    // 成员名
    g.append('text').attr('x', -8).attr('y', baseY + rowH / 2)
      .attr('text-anchor', 'end').attr('dominant-baseline', 'middle')
      .attr('font-size', 11).attr('font-weight', 600).attr('fill', '#374151')
      .text(member.split(' ').slice(-1)[0])

    INDS.forEach((ind, ii) => {
      const item = joData.find(d => d.member === member && d.industry === ind.key)
      if (!item) return
      const v = item.sentiment_mean
      const barX  = v >= 0 ? cx : xScale(v)
      const barW  = Math.abs(xScale(v) - cx)
      const subY  = baseY + 3 + ii * (subH + 2)
      const color = v >= 0 ? '#3b82f6' : '#ef4444'

      g.append('rect')
        .attr('x', barX).attr('y', subY)
        .attr('width', barW).attr('height', subH)
        .attr('fill', ind.color).attr('opacity', 0.7).attr('rx', 2)
        .append('title')
        .text(`${member} · ${ind.label}：${(v > 0 ? '+' : '') + v.toFixed(2)} (n=${item.count})`)
    })
  })

  // X 轴
  g.append('g').attr('transform', `translate(0,${members.length * rowH})`).call(
    d3.axisBottom(xScale).ticks(4).tickFormat(d => (Number(d) > 0 ? '+' : '') + Number(d).toFixed(1))
  )
    .call(ax => ax.select('.domain').attr('stroke', '#e2e8f0'))
    .call(ax => ax.selectAll('text').attr('font-size', 9).attr('fill', '#94a3b8'))
    .call(ax => ax.selectAll('.tick line').attr('stroke', '#e2e8f0'))
}

const ro = new ResizeObserver(draw)
onMounted(() => { ro.observe(el.value!); draw() })
onUnmounted(() => ro.disconnect())
watch(() => props.data, draw, { deep: true })
</script>
<style scoped>.summary-chart { width: 100%; }</style>

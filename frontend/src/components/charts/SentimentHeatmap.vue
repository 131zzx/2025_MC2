<template>
  <div ref="el" class="d3-chart" />
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as d3 from 'd3'
import type { SentimentAggItem } from '../../types'
import { COMMITTEE_MEMBERS, INDUSTRY_LABELS } from '../../types'

const props = defineProps<{
  data: SentimentAggItem[]
  dataset: string
}>()

const el = ref<HTMLElement>()

const INDS = ['fishing', 'tourism', 'mixed']

// 蓝(正向) → 白(中立) → 红(负向) 的发散色阶，白底清晰可读
const color = d3.scaleDiverging(d3.interpolateRdBu).domain([-1, 0, 1])

// 根据背景色亮度决定文字颜色
function textColor(val: number): string {
  const bg = color(val)
  const rgb = d3.rgb(bg)
  // 亮度公式 (sRGB luminance)
  const lum = (rgb.r * 299 + rgb.g * 587 + rgb.b * 114) / 1000
  return lum > 160 ? '#1e293b' : '#ffffff'
}

function draw() {
  if (!el.value) return
  el.value.innerHTML = ''

  // 按当前数据集过滤
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
  const yScale  = d3.scaleBand().domain(INDS).range([0, ih]).padding(0.06)

  // 无数据提示
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

      // 格子背景（无数据用浅灰）
      cell.append('rect')
        .attr('x', xScale(m)!).attr('y', yScale(ind)!)
        .attr('width', xScale.bandwidth()).attr('height', yScale.bandwidth())
        .attr('fill', val !== null ? color(val) : '#f1f5f9')
        .attr('stroke', '#ffffff').attr('stroke-width', 3)
        .attr('rx', 5)
        .append('title')
        .text(val !== null
          ? `${m}\n${INDUSTRY_LABELS[ind as keyof typeof INDUSTRY_LABELS]}: ${val.toFixed(3)} (n=${item!.count})`
          : `${m} / ${INDUSTRY_LABELS[ind as keyof typeof INDUSTRY_LABELS]}: 无记录`)

      // 数值文字
      if (val !== null) {
        cell.append('text')
          .attr('x', xScale(m)! + xScale.bandwidth() / 2)
          .attr('y', yScale(ind)! + yScale.bandwidth() / 2 + 4)
          .attr('text-anchor', 'middle')
          .attr('font-size', 11).attr('font-weight', 600)
          .attr('fill', textColor(val))
          .text(val.toFixed(2))
      } else {
        // 无数据用 "—"
        cell.append('text')
          .attr('x', xScale(m)! + xScale.bandwidth() / 2)
          .attr('y', yScale(ind)! + yScale.bandwidth() / 2 + 4)
          .attr('text-anchor', 'middle').attr('font-size', 11).attr('fill', '#cbd5e1')
          .text('—')
      }
    })
  })

  // X 轴（成员名，斜体避免重叠）
  g.append('g').attr('transform', `translate(0,${ih})`)
    .call(d3.axisBottom(xScale).tickSize(0))
    .call(ax => ax.select('.domain').remove())
    .call(ax => ax.selectAll('text')
      .attr('fill', '#475569').attr('font-size', 10).attr('font-weight', 500)
      .attr('transform', 'rotate(-18)').style('text-anchor', 'end').attr('dy', '0.5em'))

  // Y 轴（行业）
  g.append('g').call(
    d3.axisLeft(yScale)
      .tickFormat(d => INDUSTRY_LABELS[d as keyof typeof INDUSTRY_LABELS] ?? d)
      .tickSize(0)
  )
    .call(ax => ax.select('.domain').remove())
    .call(ax => ax.selectAll('text').attr('fill', '#475569').attr('font-size', 11).attr('font-weight', 600))

  // 色条图例
  const defs = svg.append('defs')
  const grad = defs.append('linearGradient').attr('id', 'hm-grad-v')
    .attr('x1', '0%').attr('x2', '0%').attr('y1', '0%').attr('y2', '100%')
  const stops = d3.range(0, 1.01, 0.1)
  stops.forEach(t => {
    grad.append('stop')
      .attr('offset', `${t * 100}%`)
      .attr('stop-color', color(1 - t * 2))  // +1 → 0 → -1
  })

  const lx = W - margin.right + 12
  const ly = margin.top
  svg.append('rect').attr('x', lx).attr('y', ly).attr('width', 12).attr('height', ih)
    .attr('fill', 'url(#hm-grad-v)').attr('rx', 3)
    .attr('stroke', '#e2e8f0').attr('stroke-width', 1)

  const lStyle = { fill: '#64748b', 'font-size': 9 }
  svg.append('text').attr('x', lx + 16).attr('y', ly + 8)
    .attr('fill', '#2563eb').attr('font-size', 9).attr('font-weight', 600).text('+1')
  svg.append('text').attr('x', lx + 16).attr('y', ly + ih / 2 + 4)
    .attr('fill', '#94a3b8').attr('font-size', 9).text('0')
  svg.append('text').attr('x', lx + 16).attr('y', ly + ih - 2)
    .attr('fill', '#dc2626').attr('font-size', 9).attr('font-weight', 600).text('-1')

  // 图例说明
  svg.append('text').attr('x', lx).attr('y', ly + ih + 14)
    .attr('fill', '#94a3b8').attr('font-size', 8).text('蓝=正向')
  svg.append('text').attr('x', lx).attr('y', ly + ih + 24)
    .attr('fill', '#94a3b8').attr('font-size', 8).text('红=负向')
}

const ro = new ResizeObserver(draw)
onMounted(() => { ro.observe(el.value!); draw() })
watch([() => props.data, () => props.dataset], draw, { deep: true })
onUnmounted(() => ro.disconnect())
</script>
<style scoped>.d3-chart { width: 100%; }</style>

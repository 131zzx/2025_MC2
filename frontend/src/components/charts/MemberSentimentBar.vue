<!--
  单个成员在记者数据集中各行业的情感均值（横向条形图）
-->
<template>
  <div ref="el" class="d3-chart" />
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import * as d3 from 'd3'
import type { SentimentAggItem } from '../../types'
import { INDUSTRY_COLORS, INDUSTRY_LABELS } from '../../types'

const props = defineProps<{
  data: SentimentAggItem[]
  member: string
  dataset?: string
}>()

const el = ref<HTMLElement>()

const filtered = computed(() =>
  props.data.filter(d =>
    d.member === props.member &&
    d.dataset === (props.dataset ?? 'journalist')
  ).sort((a, b) => b.sentiment_mean - a.sentiment_mean)
)

function draw() {
  if (!el.value) return
  el.value.innerHTML = ''

  const rows = filtered.value
  if (!rows.length) {
    el.value.innerHTML = '<div style="color:#475569;font-size:12px;padding:24px;text-align:center">该成员在此数据集中无情感记录</div>'
    return
  }

  const W = el.value.clientWidth || 340
  const H = Math.max(160, rows.length * 44 + 40)
  const margin = { top: 16, right: 56, bottom: 12, left: 90 }
  const iw = W - margin.left - margin.right
  const ih = H - margin.top - margin.bottom

  const svg = d3.select(el.value).append('svg').attr('width', W).attr('height', H)
  const g   = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

  const industries = rows.map(d => d.industry)
  const y = d3.scaleBand().domain(industries).range([0, ih]).padding(0.28)
  const x = d3.scaleLinear().domain([-1, 1]).range([0, iw])

  // 零线
  g.append('line')
    .attr('x1', x(0)).attr('x2', x(0))
    .attr('y1', 0).attr('y2', ih)
    .attr('stroke', '#334155').attr('stroke-width', 1.5)

  // 渐变定义
  const defs = svg.append('defs')
  const gPos = defs.append('linearGradient').attr('id', 'sentPos')
    .attr('x1', '0%').attr('x2', '100%')
  gPos.append('stop').attr('offset', '0%').attr('stop-color', '#10b981').attr('stop-opacity', .3)
  gPos.append('stop').attr('offset', '100%').attr('stop-color', '#10b981').attr('stop-opacity', .9)

  const gNeg = defs.append('linearGradient').attr('id', 'sentNeg')
    .attr('x1', '100%').attr('x2', '0%')
  gNeg.append('stop').attr('offset', '0%').attr('stop-color', '#ef4444').attr('stop-opacity', .3)
  gNeg.append('stop').attr('offset', '100%').attr('stop-color', '#ef4444').attr('stop-opacity', .9)

  // 条形
  g.selectAll('.bar').data(rows).join('rect').attr('class', 'bar')
    .attr('x', d => d.sentiment_mean >= 0 ? x(0) : x(d.sentiment_mean))
    .attr('y', d => y(d.industry)!)
    .attr('width', d => Math.abs(x(d.sentiment_mean) - x(0)))
    .attr('height', y.bandwidth())
    .attr('fill', d => d.sentiment_mean >= 0 ? 'url(#sentPos)' : 'url(#sentNeg)')
    .attr('rx', 4)
    .append('title')
    .text(d => `${INDUSTRY_LABELS[d.industry as keyof typeof INDUSTRY_LABELS] ?? d.industry}: ${d.sentiment_mean.toFixed(3)} (n=${d.count})`)

  // 行业标签（Y 轴）
  g.append('g').call(d3.axisLeft(y).tickSize(0)
    .tickFormat(d => INDUSTRY_LABELS[d as keyof typeof INDUSTRY_LABELS] ?? d)
  )
    .call(ax => ax.select('.domain').remove())
    .call(ax => ax.selectAll('text')
      .attr('fill', d => INDUSTRY_COLORS[d as keyof typeof INDUSTRY_COLORS] ?? '#94a3b8')
      .attr('font-size', 11).attr('font-weight', 600).attr('x', -8)
    )

  // 数值标签
  g.selectAll('.val').data(rows).join('text').attr('class', 'val')
    .attr('x', d => d.sentiment_mean >= 0 ? x(d.sentiment_mean) + 5 : x(d.sentiment_mean) - 5)
    .attr('y', d => y(d.industry)! + y.bandwidth() / 2 + 4)
    .attr('text-anchor', d => d.sentiment_mean >= 0 ? 'start' : 'end')
    .attr('font-size', 10).attr('fill', '#94a3b8')
    .text(d => d.sentiment_mean.toFixed(2))

  // 正负标注
  svg.append('text').attr('x', margin.left + x(0) + 6).attr('y', margin.top - 4)
    .attr('font-size', 9).attr('fill', '#10b981').text('正向 +')
  svg.append('text').attr('x', margin.left + x(-0.95)).attr('y', margin.top - 4)
    .attr('font-size', 9).attr('fill', '#ef4444').text('- 负向')
}

const ro = new ResizeObserver(draw)
onMounted(() => { ro.observe(el.value!); draw() })
watch([() => props.data, () => props.member, () => props.dataset], draw, { deep: true })
onUnmounted(() => ro.disconnect())
</script>

<style scoped>
.d3-chart { width: 100%; }
</style>

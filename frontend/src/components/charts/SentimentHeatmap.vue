<template>
  <div ref="el" class="d3-chart" />
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as d3 from 'd3'
import type { SentimentAggItem } from '../../types'
import { COMMITTEE_MEMBERS, INDUSTRY_LABELS } from '../../types'

const props = defineProps<{ data: SentimentAggItem[] }>()
const el = ref<HTMLElement>()

const INDS = ['fishing', 'tourism', 'mixed']

function draw() {
  if (!el.value || !props.data.length) return
  el.value.innerHTML = ''
  const W = el.value.clientWidth || 500
  const H = 240
  const margin = { top: 16, right: 80, bottom: 60, left: 56 }
  const iw = W - margin.left - margin.right
  const ih = H - margin.top - margin.bottom

  const svg = d3.select(el.value).append('svg').attr('width', W).attr('height', H)
  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

  const members = [...COMMITTEE_MEMBERS]
  const xScale  = d3.scaleBand().domain(members).range([0, iw]).padding(0.05)
  const yScale  = d3.scaleBand().domain(INDS).range([0, ih]).padding(0.05)
  const color   = d3.scaleSequential(d3.interpolateRdYlGn).domain([-1, 1])

  INDS.forEach(ind => {
    members.forEach(m => {
      const item = props.data.find(d => d.member === m && d.industry === ind)
      const val  = item?.sentiment_mean ?? null

      g.append('rect')
        .attr('x', xScale(m)!).attr('y', yScale(ind)!)
        .attr('width', xScale.bandwidth()).attr('height', yScale.bandwidth())
        .attr('fill', val !== null ? color(val) : '#1e293b')
        .attr('stroke', '#0f172a').attr('stroke-width', 2).attr('rx', 3)
        .append('title').text(val !== null ? `${m} / ${ind}: ${val.toFixed(2)}` : '无数据')

      if (val !== null) {
        g.append('text')
          .attr('x', xScale(m)! + xScale.bandwidth() / 2)
          .attr('y', yScale(ind)! + yScale.bandwidth() / 2 + 4)
          .attr('text-anchor', 'middle').attr('font-size', 10)
          .attr('fill', Math.abs(val) > 0.4 ? '#fff' : '#1e293b')
          .text(val.toFixed(2))
      }
    })
  })

  g.append('g').attr('transform', `translate(0,${ih})`)
    .call(d3.axisBottom(xScale).tickSize(0))
    .call(ax => ax.select('.domain').remove())
    .call(ax => ax.selectAll('text').attr('fill', '#94a3b8').attr('font-size', 10).attr('transform', 'rotate(-15)').style('text-anchor', 'end'))

  g.append('g').call(d3.axisLeft(yScale).tickFormat(d => INDUSTRY_LABELS[d as keyof typeof INDUSTRY_LABELS] ?? d).tickSize(0))
    .call(ax => ax.select('.domain').remove())
    .call(ax => ax.selectAll('text').attr('fill', '#94a3b8').attr('font-size', 11))

  // 色条图例
  const defs = svg.append('defs')
  const grad = defs.append('linearGradient').attr('id', 'hm-grad').attr('x1', '0%').attr('x2', '100%')
  grad.append('stop').attr('offset', '0%').attr('stop-color', color(-1))
  grad.append('stop').attr('offset', '50%').attr('stop-color', color(0))
  grad.append('stop').attr('offset', '100%').attr('stop-color', color(1))

  const legendG = svg.append('g').attr('transform', `translate(${W - margin.right + 8}, ${margin.top})`)
  legendG.append('rect').attr('width', 12).attr('height', ih).attr('fill', 'url(#hm-grad)').attr('rx', 3)
  legendG.append('text').attr('x', 16).attr('y', 8).attr('fill', '#94a3b8').attr('font-size', 9).text('+1 旅游')
  legendG.append('text').attr('x', 16).attr('y', ih / 2 + 4).attr('fill', '#94a3b8').attr('font-size', 9).text('0')
  legendG.append('text').attr('x', 16).attr('y', ih).attr('fill', '#94a3b8').attr('font-size', 9).text('-1 渔业')
}

const ro = new ResizeObserver(draw)
onMounted(() => { ro.observe(el.value!); draw() })
watch(() => props.data, draw, { deep: true })
onUnmounted(() => ro.disconnect())
</script>
<style scoped>.d3-chart { width: 100%; }</style>

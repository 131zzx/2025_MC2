<template>
  <div ref="el" class="d3-chart" />
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import * as d3 from 'd3'
import type { CoverageItem } from '../../types'
import { DATASET_COLORS } from '../../types'

const props = defineProps<{ data: CoverageItem[], dataset: 'filah' | 'trout' }>()
const el = ref<HTMLElement>()

const sorted = computed(() =>
  [...props.data.filter(d => d.dataset === props.dataset)]
    .sort((a, b) => a.coverage - b.coverage)
)

function draw() {
  if (!el.value || !sorted.value.length) return
  el.value.innerHTML = ''
  const W = el.value.clientWidth || 400, H = 240
  const margin = { top: 8, right: 60, bottom: 8, left: 110 }
  const iw = W - margin.left - margin.right
  const ih = H - margin.top - margin.bottom

  const svg = d3.select(el.value).append('svg').attr('width', W).attr('height', H)
  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

  const members = sorted.value.map(d => d.member)
  const y = d3.scaleBand().domain(members).range([0, ih]).padding(0.25)
  const x = d3.scaleLinear().domain([0, 1]).range([0, iw])

  // 背景轨道
  g.selectAll('.track').data(sorted.value).join('rect').attr('class', 'track')
    .attr('x', 0).attr('y', d => y(d.member)!).attr('width', iw).attr('height', y.bandwidth())
    .attr('fill', '#f1f5f9').attr('rx', 4)

  // 覆盖率条
  g.selectAll('.bar').data(sorted.value).join('rect').attr('class', 'bar')
    .attr('x', 0).attr('y', d => y(d.member)!)
    .attr('width', d => x(d.coverage))
    .attr('height', y.bandwidth())
    .attr('fill', d => d.coverage === 0 ? '#ef4444' : d.coverage < 0.2 ? '#f97316' : DATASET_COLORS[props.dataset])
    .attr('rx', 4)
    .append('title').text(d => `${d.member}: ${(d.coverage * 100).toFixed(1)}% (${d.overlap_cnt}/${d.jo_activity_cnt})`)

  // 百分比标签
  g.selectAll('.pct').data(sorted.value).join('text').attr('class', 'pct')
    .attr('x', d => x(d.coverage) + 6)
    .attr('y', d => y(d.member)! + y.bandwidth() / 2 + 4)
    .attr('font-size', 11).attr('fill', '#94a3b8')
    .text(d => `${(d.coverage * 100).toFixed(0)}%`)

  // Y 轴成员名
  g.append('g').call(d3.axisLeft(y).tickSize(0))
    .call(ax => ax.select('.domain').remove())
    .call(ax => ax.selectAll('text').attr('fill', d => {
      const item = sorted.value.find(s => s.member === d)
      return item?.coverage === 0 ? '#ef4444' : '#94a3b8'
    }).attr('font-size', 11))

  // 50% 参考线
  g.append('line').attr('x1', x(0.5)).attr('x2', x(0.5)).attr('y1', 0).attr('y2', ih)
    .attr('stroke', '#475569').attr('stroke-dasharray', '4 3')
  g.append('text').attr('x', x(0.5) + 3).attr('y', -4)
    .attr('fill', '#475569').attr('font-size', 9).text('50%')
}

const ro = new ResizeObserver(draw)
onMounted(() => { ro.observe(el.value!); draw() })
watch([() => props.data, () => props.dataset], draw, { deep: true })
onUnmounted(() => ro.disconnect())
</script>
<style scoped>.d3-chart { width: 100%; }</style>

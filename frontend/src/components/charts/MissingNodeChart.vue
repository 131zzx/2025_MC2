<template>
  <div>
    <div ref="el" class="d3-chart" />
    <div class="summary">
      共 <strong>{{ data.length }}</strong> 个缺失节点 ·
      <span v-for="(cnt, ind) in industryCount" :key="ind"
        :style="{ color: INDUSTRY_COLORS[ind as keyof typeof INDUSTRY_COLORS] }">
        {{ INDUSTRY_LABELS[ind as keyof typeof INDUSTRY_LABELS] ?? ind }}: {{ cnt }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import * as d3 from 'd3'
import type { MissingNode } from '../../types'
import { INDUSTRY_COLORS, INDUSTRY_LABELS } from '../../types'

const props = defineProps<{ data: MissingNode[], dataset: string }>()
const el = ref<HTMLElement>()

const industryCount = computed(() => {
  const cnt: Record<string, number> = {}
  props.data.forEach(d => { const k = d.topic_industry || 'unknown'; cnt[k] = (cnt[k] ?? 0) + 1 })
  return cnt
})

function draw() {
  if (!el.value) return
  el.value.innerHTML = ''
  const W = el.value.clientWidth || 300, H = 160
  const svg = d3.select(el.value).append('svg').attr('width', W).attr('height', H)
  const r = Math.min(W, H) / 2 - 10
  const g = svg.append('g').attr('transform', `translate(${W / 2},${H / 2})`)

  const pieData = Object.entries(industryCount.value).map(([ind, cnt]) => ({ ind, cnt }))
  const pie = d3.pie<{ ind: string; cnt: number }>().value(d => d.cnt)
  const arc = d3.arc<d3.PieArcDatum<{ ind: string; cnt: number }>>().innerRadius(r * 0.5).outerRadius(r)

  g.selectAll('path').data(pie(pieData)).join('path')
    .attr('d', arc)
    .attr('fill', d => INDUSTRY_COLORS[d.data.ind as keyof typeof INDUSTRY_COLORS] ?? '#888')
    .attr('stroke', '#0f172a').attr('stroke-width', 2)
    .append('title').text(d => `${INDUSTRY_LABELS[d.data.ind as keyof typeof INDUSTRY_LABELS] ?? d.data.ind}: ${d.data.cnt}`)

  g.selectAll('text').data(pie(pieData)).join('text')
    .attr('transform', d => `translate(${arc.centroid(d)})`)
    .attr('text-anchor', 'middle').attr('font-size', 10).attr('fill', '#fff')
    .text(d => d.data.cnt > 5 ? d.data.cnt : '')
}

const ro = new ResizeObserver(draw)
onMounted(() => { ro.observe(el.value!); draw() })
watch(() => props.data, draw, { deep: true })
onUnmounted(() => ro.disconnect())
</script>

<style scoped>
.d3-chart { width: 100%; }
.summary { font-size: 11px; color: var(--color-text-muted); margin-top: 6px; display: flex; flex-wrap: wrap; gap: 8px; }
.summary strong { color: var(--color-text); }
</style>

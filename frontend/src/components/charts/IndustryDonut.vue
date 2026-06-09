<template>
  <div class="donut-wrap">
    <svg ref="svgEl" :width="SIZE" :height="SIZE" />
    <div class="legend">
      <div v-for="item in legendItems" :key="item.ind" class="leg-item">
        <span class="leg-dot" :style="{ background: item.color }" />
        <span class="leg-label">{{ item.label }}</span>
        <span class="leg-pct">{{ item.pct }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import * as d3 from 'd3'
import type { TopicDistItem } from '../../types'
import { INDUSTRY_COLORS, INDUSTRY_LABELS } from '../../types'

const props = defineProps<{
  data: TopicDistItem[]
  dataset: string
}>()

const SIZE = 180
const svgEl = ref<SVGElement>()

const filtered = computed(() =>
  props.data.filter(d => d.dataset === props.dataset)
)

const total = computed(() => filtered.value.reduce((s, d) => s + d.count, 0))

const legendItems = computed(() =>
  filtered.value.map(d => ({
    ind:   d.industry,
    color: INDUSTRY_COLORS[d.industry as keyof typeof INDUSTRY_COLORS] ?? '#888',
    label: INDUSTRY_LABELS[d.industry as keyof typeof INDUSTRY_LABELS] ?? d.industry,
    pct:   total.value ? Math.round(d.count / total.value * 100) : 0,
    count: d.count,
  })).sort((a, b) => b.count - a.count)
)

function draw() {
  if (!svgEl.value || !filtered.value.length) return
  const svg = d3.select(svgEl.value)
  svg.selectAll('*').remove()

  const cx = SIZE / 2, cy = SIZE / 2
  const outerR = SIZE / 2 - 8, innerR = outerR * 0.55

  const pie = d3.pie<(typeof legendItems.value)[0]>().value(d => d.count).sort(null)
  const arc = d3.arc<d3.PieArcDatum<(typeof legendItems.value)[0]>>()
    .innerRadius(innerR).outerRadius(outerR)
  const arcHover = d3.arc<d3.PieArcDatum<(typeof legendItems.value)[0]>>()
    .innerRadius(innerR).outerRadius(outerR + 5)

  const g = svg.append('g').attr('transform', `translate(${cx},${cy})`)

  const arcs = g.selectAll('path').data(pie(legendItems.value)).join('path')
    .attr('d', arc as any)
    .attr('fill', d => d.data.color)
    .attr('stroke', '#ffffff')
    .attr('stroke-width', 2)
    .style('cursor', 'pointer')
    .on('mouseover', function(_, d) {
      d3.select(this).attr('d', (arcHover as any)(d))
    })
    .on('mouseout', function(_, d) {
      d3.select(this).attr('d', (arc as any)(d))
    })

  arcs.append('title').text(d => `${d.data.label}: ${d.data.count} (${d.data.pct}%)`)

  // 中心文字
  g.append('text').attr('text-anchor', 'middle').attr('dy', '-0.3em')
    .attr('font-size', 18).attr('font-weight', 700).attr('fill', '#e2e8f0')
    .text(total.value)
  g.append('text').attr('text-anchor', 'middle').attr('dy', '1.1em')
    .attr('font-size', 9).attr('fill', '#64748b').text('话题节点')
}

onMounted(draw)
watch([() => props.data, () => props.dataset], draw, { deep: true })
</script>

<style scoped>
.donut-wrap { display: flex; flex-direction: column; align-items: center; }
.legend { display: flex; flex-wrap: wrap; gap: 6px 12px; justify-content: center; margin-top: 8px; }
.leg-item { display: flex; align-items: center; gap: 5px; font-size: 11px; }
.leg-dot  { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.leg-label { color: #94a3b8; }
.leg-pct   { color: #cbd5e1; font-weight: 600; }
</style>

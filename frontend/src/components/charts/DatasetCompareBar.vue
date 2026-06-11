<!--
  数据集关键指标横向对比条形图
  展示三个数据集在节点数/边数/行程数/会议数四个维度的差异
-->
<template>
  <div ref="el" class="compare-chart" />
</template>

<script lang="ts">
import { defineComponent } from 'vue'
export default defineComponent({ name: 'DatasetCompareBar' })
</script>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as d3 from 'd3'
import type { OverviewItem } from '../../types'
import { DATASET_COLORS, DATASET_LABELS } from '../../types'

const props = defineProps<{ data: OverviewItem[] }>()
const el = ref<HTMLElement>()

const METRICS = [
  { key: 'node_count',    label: '节点总数' },
  { key: 'edge_count',    label: '边总数' },
  { key: 'trip_count',    label: '行程记录' },
  { key: 'meeting_count', label: '会议数' },
]
const DS = ['filah', 'trout', 'journalist'] as const

function draw() {
  if (!el.value || !props.data.length) return
  el.value.innerHTML = ''

  const W = el.value.clientWidth || 500
  const rowH = 56
  const legendH = 22
  const H = legendH + METRICS.length * rowH + 16
  const m = { top: legendH + 6, right: 52, bottom: 8, left: 72 }
  const iw = W - m.left - m.right

  const svg = d3.select(el.value).append('svg').attr('width', W).attr('height', H)
  const g = svg.append('g').attr('transform', `translate(${m.left},${m.top})`)

  // 顶部图例
  const legend = g.append('g').attr('transform', `translate(0,${-legendH - 2})`)
  DS.forEach((ds, i) => {
    const lx = i * 88
    legend.append('rect').attr('x', lx).attr('y', 0)
      .attr('width', 10).attr('height', 10).attr('rx', 2)
      .attr('fill', DATASET_COLORS[ds]).attr('opacity', 0.85)
    legend.append('text').attr('x', lx + 14).attr('y', 9)
      .attr('font-size', 10).attr('fill', '#64748b')
      .text(DATASET_LABELS[ds])
  })

  METRICS.forEach((metric, mi) => {
    const vals = DS.map(ds => {
      const item = props.data.find(d => d.dataset === ds)
      return { ds, v: (item as Record<string, number | undefined>)?.[metric.key] ?? 0 }
    })
    const maxV = d3.max(vals, d => d.v) || 1
    const xScale = d3.scaleLinear().domain([0, maxV]).range([0, iw])
    const baseY = mi * rowH

    g.append('text').attr('x', -6).attr('y', baseY + rowH / 2)
      .attr('text-anchor', 'end').attr('dominant-baseline', 'middle')
      .attr('font-size', 11).attr('font-weight', 700).attr('fill', '#374151')
      .text(metric.label)

    g.append('rect').attr('x', 0).attr('y', baseY + 4)
      .attr('width', iw).attr('height', rowH - 8)
      .attr('fill', '#f8fafc').attr('rx', 4)

    const subH = (rowH - 8) / 3 - 2
    vals.forEach(({ ds, v }, di) => {
      const barW = xScale(v)
      const subY = baseY + 4 + di * (subH + 2)
      const color = DATASET_COLORS[ds]

      g.append('rect').attr('x', 0).attr('y', subY)
        .attr('width', Math.max(barW, v > 0 ? 2 : 0))
        .attr('height', subH)
        .attr('fill', color).attr('opacity', 0.82).attr('rx', 2)

      // 数值固定在右侧列，避免与条形末端重叠
      g.append('text').attr('x', iw + 6).attr('y', subY + subH / 2)
        .attr('dominant-baseline', 'middle').attr('text-anchor', 'start')
        .attr('font-size', 9.5).attr('fill', '#475569').attr('font-weight', 600)
        .text(v)
    })

    if (mi < METRICS.length - 1) {
      g.append('line').attr('x1', -m.left + 4).attr('x2', iw)
        .attr('y1', baseY + rowH).attr('y2', baseY + rowH)
        .attr('stroke', '#f1f5f9').attr('stroke-width', 1)
    }
  })
}

const ro = new ResizeObserver(draw)
onMounted(() => { ro.observe(el.value!); draw() })
onUnmounted(() => ro.disconnect())
watch(() => props.data, draw, { deep: true })
</script>
<style scoped>.compare-chart { width: 100%; }</style>

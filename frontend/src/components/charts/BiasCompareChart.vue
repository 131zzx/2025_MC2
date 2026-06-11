<!--
  偏见指数对比图
  三个数据集在同一轴上显示：水平发散条形图
  bias_index = (旅游 − 渔业) / (旅游 + 渔业)
  正值 → 旅游偏向（右侧），负值 → 渔业偏向（左侧）
-->
<template>
  <div ref="el" class="bias-chart" />
</template>

<script lang="ts">
import { defineComponent } from 'vue'
export default defineComponent({ name: 'BiasCompareChart' })
</script>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as d3 from 'd3'
import type { BiasIndexItem } from '../../types'
import { DATASET_COLORS, INDUSTRY_COLORS } from '../../types'

const props = defineProps<{
  data: BiasIndexItem[]
}>()

const el = ref<HTMLElement>()

function draw() {
  if (!el.value) return
  el.value.innerHTML = ''

  // 取整体偏见（member === 'ALL'）
  const overall = ['filah', 'trout', 'journalist'].map(ds => {
    const item = props.data.find(d => d.dataset === ds && d.member === 'ALL')
    return { ds, value: item?.bias_index ?? 0 }
  })

  const W = el.value.clientWidth || 500
  const H = 160
  const m = { top: 20, right: 80, bottom: 36, left: 90 }
  const iw = W - m.left - m.right
  const ih = H - m.top - m.bottom

  const svg = d3.select(el.value).append('svg')
    .attr('width', W).attr('height', H)

  const g = svg.append('g').attr('transform', `translate(${m.left},${m.top})`)

  const xScale = d3.scaleLinear().domain([-1, 1]).range([0, iw]).clamp(true)
  const yScale = d3.scaleBand()
    .domain(['filah', 'trout', 'journalist'])
    .range([0, ih]).padding(0.35)

  const cx = xScale(0)

  // 背景渐变 + 中轴线
  const grad = svg.append('defs').append('linearGradient').attr('id', 'bias-bg')
    .attr('x1', '0%').attr('x2', '100%')
  grad.append('stop').attr('offset', '0%').attr('stop-color', '#eff6ff').attr('stop-opacity', 0.8)
  grad.append('stop').attr('offset', '50%').attr('stop-color', '#f8fafc').attr('stop-opacity', 0.4)
  grad.append('stop').attr('offset', '100%').attr('stop-color', '#ecfdf5').attr('stop-opacity', 0.8)

  g.append('rect').attr('width', iw).attr('height', ih).attr('fill', 'url(#bias-bg)').attr('rx', 4)

  // 参考线
  g.append('line')
    .attr('x1', cx).attr('x2', cx).attr('y1', -8).attr('y2', ih + 4)
    .attr('stroke', '#94a3b8').attr('stroke-width', 1.5).attr('stroke-dasharray', '4,3')

  // 刻度线 ±0.25 ±0.5 ±0.75
  ;[-0.75, -0.5, -0.25, 0.25, 0.5, 0.75].forEach(v => {
    g.append('line')
      .attr('x1', xScale(v)).attr('x2', xScale(v)).attr('y1', 0).attr('y2', ih)
      .attr('stroke', '#e2e8f0').attr('stroke-width', 1)
  })

  // 条形
  overall.forEach(({ ds, value }) => {
    const y = yScale(ds)!
    const bw = yScale.bandwidth()
    const barX  = value >= 0 ? cx : xScale(value)
    const barW  = Math.abs(xScale(value) - cx)
    const color = DATASET_COLORS[ds as keyof typeof DATASET_COLORS] || '#94a3b8'
    const posColor = value >= 0 ? INDUSTRY_COLORS.tourism : INDUSTRY_COLORS.fishing

    // 条形本体
    g.append('rect')
      .attr('x', barX).attr('y', y)
      .attr('width', barW).attr('height', bw)
      .attr('fill', posColor)
      .attr('opacity', 0.75)
      .attr('rx', 3)

    // 数据集名称（左侧）
    g.append('text')
      .attr('x', -8).attr('y', y + bw / 2)
      .attr('text-anchor', 'end').attr('dominant-baseline', 'middle')
      .attr('font-size', 12).attr('font-weight', 700)
      .attr('fill', color)
      .text(ds === 'journalist' ? '记者' : ds.toUpperCase())

    // 数值标签（条形右端或左端）
    const labelX = value >= 0 ? barX + barW + 5 : barX - 5
    const anchor = value >= 0 ? 'start' : 'end'
    g.append('text')
      .attr('x', labelX).attr('y', y + bw / 2)
      .attr('text-anchor', anchor).attr('dominant-baseline', 'middle')
      .attr('font-size', 11).attr('font-weight', 600)
      .attr('fill', posColor)
      .text((value > 0 ? '+' : '') + value.toFixed(3))
  })

  // X轴
  g.append('g').attr('transform', `translate(0,${ih})`).call(
    d3.axisBottom(xScale).ticks(5).tickFormat(d => (Number(d) > 0 ? '+' : '') + Number(d).toFixed(1))
  )
    .call(ax => ax.select('.domain').attr('stroke', '#e2e8f0'))
    .call(ax => ax.selectAll('text').attr('font-size', 10).attr('fill', '#94a3b8'))
    .call(ax => ax.selectAll('.tick line').attr('stroke', '#e2e8f0'))

  // 两侧标注
  svg.append('text').attr('x', m.left - 4).attr('y', H - 6)
    .attr('text-anchor', 'end').attr('font-size', 10).attr('fill', INDUSTRY_COLORS.fishing).attr('font-weight', 600)
    .text('← 渔业偏向')
  svg.append('text').attr('x', m.left + iw + 4).attr('y', H - 6)
    .attr('text-anchor', 'start').attr('font-size', 10).attr('fill', INDUSTRY_COLORS.tourism).attr('font-weight', 600)
    .text('旅游偏向 →')
}

const ro = new ResizeObserver(draw)
onMounted(() => { ro.observe(el.value!); draw() })
onUnmounted(() => ro.disconnect())
watch(() => props.data, draw, { deep: true })
</script>
<style scoped>.bias-chart { width: 100%; }</style>

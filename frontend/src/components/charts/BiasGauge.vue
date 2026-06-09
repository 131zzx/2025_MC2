<!--
  偏见仪表盘
  bias_index > 0  → 偏向渔业（Fishing）
  bias_index < 0  → 偏向旅游（Tourism）
  bias_index = 0  → 中立
-->
<template>
  <div class="gauge-wrap">
    <svg ref="svgEl" :width="W" :height="H" />
    <div class="gauge-label">
      <span class="lbl-fishing">渔业 ←</span>
      <span class="lbl-center">中立</span>
      <span class="lbl-tourism">→ 旅游</span>
    </div>
    <div class="gauge-value" :style="{ color: valueColor }">
      {{ displayVal }}
    </div>
    <div class="gauge-desc">{{ desc }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import * as d3 from 'd3'

const props = defineProps<{
  /** -1 ~ 1，正值=渔业偏向，负值=旅游偏向 */
  value: number
  label: string
  color: string
}>()

const W = 240, H = 140
const svgEl = ref<SVGElement>()

const clampedVal = computed(() => Math.max(-1, Math.min(1, props.value)))

/** 色彩 */
const valueColor = computed(() => {
  if (clampedVal.value > 0.15) return '#f59e0b'
  if (clampedVal.value < -0.15) return '#3b82f6'
  return '#94a3b8'
})

const displayVal = computed(() => {
  const v = clampedVal.value
  const sign = v > 0 ? '+' : ''
  return `偏差指数 ${sign}${v.toFixed(3)}`
})

const desc = computed(() => {
  const v = clampedVal.value
  if (v > 0.3) return '明显偏向渔业，数据集可靠性受影响'
  if (v > 0.1) return '轻微偏向渔业'
  if (v < -0.3) return '明显偏向旅游，数据集可靠性受影响'
  if (v < -0.1) return '轻微偏向旅游'
  return '相对中立'
})

function draw() {
  if (!svgEl.value) return
  const svg = d3.select(svgEl.value)
  svg.selectAll('*').remove()

  const cx = W / 2, cy = H - 20
  const r  = 90
  const startAngle = -Math.PI * 0.85
  const endAngle   =  Math.PI * 0.85

  // 渐变背景弧（渔业→中立→旅游）
  const arcBg = d3.arc<any>().innerRadius(r - 22).outerRadius(r)

  // 3 段颜色：渔业区(金)  中立区(灰)  旅游区(蓝)
  const segments = [
    { s: startAngle,           e: startAngle + (endAngle - startAngle) / 3, color: '#78350f' },
    { s: startAngle + (endAngle - startAngle) / 3, e: endAngle - (endAngle - startAngle) / 3, color: '#1e3a5f' },
    { s: endAngle - (endAngle - startAngle) / 3,   e: endAngle,              color: '#1e3a5f' },
  ]

  // 用线性渐变替代分段颜色 → 更好看的渐变弧
  const defs = svg.append('defs')
  const grad = defs.append('linearGradient').attr('id', 'gaugeGrad')
    .attr('x1', '0%').attr('y1', '0%').attr('x2', '100%').attr('y2', '0%')
  grad.append('stop').attr('offset', '0%').attr('stop-color', '#f59e0b').attr('stop-opacity', .8)
  grad.append('stop').attr('offset', '40%').attr('stop-color', '#374151')
  grad.append('stop').attr('offset', '60%').attr('stop-color', '#374151')
  grad.append('stop').attr('offset', '100%').attr('stop-color', '#3b82f6').attr('stop-opacity', .8)

  // 外圈弧
  const outerArc = d3.arc<any>().innerRadius(r - 22).outerRadius(r)
    .startAngle(startAngle).endAngle(endAngle)
  svg.append('path').attr('d', outerArc(null))
    .attr('fill', 'url(#gaugeGrad)')
    .attr('transform', `translate(${cx},${cy})`)

  // 刻度线
  const ticks = d3.range(startAngle, endAngle + 0.01, (endAngle - startAngle) / 8)
  svg.append('g').attr('transform', `translate(${cx},${cy})`).selectAll('line')
    .data(ticks).join('line')
    .attr('x1', a => (r - 23) * Math.sin(a)).attr('y1', a => -(r - 23) * Math.cos(a))
    .attr('x2', a => (r - 10) * Math.sin(a)).attr('y2', a => -(r - 10) * Math.cos(a))
    .attr('stroke', '#f1f5f9').attr('stroke-width', 1.5)

  // 指针角度：value映射到 startAngle ~ endAngle
  const needleAngle = startAngle + (clampedVal.value + 1) / 2 * (endAngle - startAngle)
  const nx = (r - 12) * Math.sin(needleAngle)
  const ny = -(r - 12) * Math.cos(needleAngle)

  const g = svg.append('g').attr('transform', `translate(${cx},${cy})`)

  // 指针
  g.append('line')
    .attr('x1', 0).attr('y1', 0)
    .attr('x2', nx).attr('y2', ny)
    .attr('stroke', '#1e293b')
    .attr('stroke-width', 3)
    .attr('stroke-linecap', 'round')

  // 指针中心圆
  g.append('circle').attr('r', 7)
    .attr('fill', '#1e293b').attr('stroke', '#ffffff').attr('stroke-width', 2)

  // 标签
  svg.append('text').attr('x', cx - r + 8).attr('y', cy + 14)
    .attr('text-anchor', 'middle').attr('font-size', 9).attr('fill', '#d97706').text('渔业')
  svg.append('text').attr('x', cx + r - 8).attr('y', cy + 14)
    .attr('text-anchor', 'middle').attr('font-size', 9).attr('fill', '#2563eb').text('旅游')

  // 数据集名
  svg.append('text').attr('x', cx).attr('y', 16)
    .attr('text-anchor', 'middle').attr('font-size', 13).attr('font-weight', 700)
    .attr('fill', props.color).text(props.label)
}

onMounted(draw)
watch(() => props.value, draw)
</script>

<style scoped>
.gauge-wrap { display: flex; flex-direction: column; align-items: center; padding: 8px 0; }
.gauge-label {
  display: flex; justify-content: space-between; width: 180px;
  font-size: 10px; color: #94a3b8; margin-top: 4px;
}
.lbl-fishing { color: #d97706; }
.lbl-tourism { color: #2563eb; }
.lbl-center  { color: #94a3b8; }
.gauge-value { font-size: 16px; font-weight: 700; margin-top: 6px; }
.gauge-desc  { font-size: 11px; color: #64748b; margin-top: 4px; text-align: center; max-width: 200px; }
</style>

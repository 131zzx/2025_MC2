<template>
  <div ref="el" class="d3-chart" />
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as d3 from 'd3'
import type { NodeTypeCountItem } from '../../types'
import { DATASET_LABELS, DATASET_COLORS } from '../../types'

const props = defineProps<{ data: NodeTypeCountItem[] }>()
const el = ref<HTMLElement>()

const DATASETS = ['filah', 'trout', 'journalist'] as const

const NODE_LABELS: Record<string, string> = {
  trip:                  '行程 (trip)',
  place:                 '地点 (place)',
  discussion:            '讨论 (discussion)',
  plan:                  '计划 (plan)',
  topic:                 '议题 (topic)',
  meeting:               '会议 (meeting)',
  'entity.organization': '组织',
  'entity.person':       '人物',
}

function draw() {
  if (!el.value || !props.data.length) return
  el.value.innerHTML = ''

  // 收集所有出现的 node_type，按记者数据集数量降序排列
  const types = [...new Set(props.data.map(d => d.node_type))]
    .sort((a, b) => {
      const va = props.data.find(d => d.node_type === a && d.dataset === 'journalist')?.count ?? 0
      const vb = props.data.find(d => d.node_type === b && d.dataset === 'journalist')?.count ?? 0
      return vb - va
    })

  const W = el.value.clientWidth || 560
  const rowH = 28      // 每个 dataset 一行的高度
  const groupGap = 14  // 每个 type 之间的间距
  const groupH = DATASETS.length * rowH + groupGap
  const nTypes = types.length
  const margin = { top: 16, right: 100, bottom: 32, left: 160 }
  const H = margin.top + nTypes * groupH + margin.bottom
  const iw = W - margin.left - margin.right
  const ih = H - margin.top - margin.bottom

  const svg = d3.select(el.value).append('svg').attr('width', W).attr('height', H)
  const g   = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

  // 最大值用于 X 轴
  const maxVal = d3.max(props.data, d => d.count) ?? 1
  const x = d3.scaleLinear().domain([0, maxVal]).range([0, iw]).nice()

  // 每种节点类型组的 Y 起点
  const typeY = (i: number) => i * groupH

  // 垂直网格线
  g.append('g').attr('class', 'grid')
    .call(d3.axisBottom(x).ticks(5).tickSize(ih).tickFormat(() => ''))
    .attr('transform', 'translate(0,0)')
    .call(ax => ax.select('.domain').remove())
    .call(ax => ax.selectAll('line').attr('stroke', '#f1f5f9').attr('stroke-dasharray', '3,3'))

  // 交替行背景
  types.forEach((_, i) => {
    if (i % 2 === 0) {
      g.append('rect')
        .attr('x', -8).attr('y', typeY(i) - 4)
        .attr('width', iw + 8).attr('height', groupH - groupGap + 8)
        .attr('fill', '#f8fafc').attr('rx', 4)
    }
  })

  // 每种节点类型
  types.forEach((type, ti) => {
    const baseY = typeY(ti)

    // 类型标签
    g.append('text')
      .attr('x', -12).attr('y', baseY + (DATASETS.length * rowH) / 2 + 4)
      .attr('text-anchor', 'end')
      .attr('font-size', 11).attr('font-weight', 600).attr('fill', '#374151')
      .text(NODE_LABELS[type] ?? type)

    // 每个数据集的条
    DATASETS.forEach((ds, di) => {
      const item = props.data.find(d => d.node_type === type && d.dataset === ds)
      const val = item?.count ?? 0
      const barY = baseY + di * rowH + 2
      const color = DATASET_COLORS[ds]

      // 轨道
      g.append('rect')
        .attr('x', 0).attr('y', barY)
        .attr('width', iw).attr('height', rowH - 6)
        .attr('fill', '#f1f5f9').attr('rx', 4)

      // 条形
      if (val > 0) {
        g.append('rect')
          .attr('x', 0).attr('y', barY)
          .attr('width', x(val)).attr('height', rowH - 6)
          .attr('fill', color).attr('rx', 4).attr('opacity', 0.85)
          .append('title')
          .text(`${DATASET_LABELS[ds]}: ${val} 个 ${NODE_LABELS[type] ?? type}`)

        // 数值标签（值较小时放在条外）
        const labelX = x(val) > 34 ? x(val) - 4 : x(val) + 4
        const anchor = x(val) > 34 ? 'end' : 'start'
        const labelColor = x(val) > 34 ? '#ffffff' : '#475569'
        g.append('text')
          .attr('x', labelX).attr('y', barY + (rowH - 6) / 2 + 4)
          .attr('text-anchor', anchor).attr('font-size', 9).attr('font-weight', 700)
          .attr('fill', labelColor).text(val)
      } else {
        g.append('text')
          .attr('x', 5).attr('y', barY + (rowH - 6) / 2 + 4)
          .attr('font-size', 9).attr('fill', '#cbd5e1').text('0')
      }
    })
  })

  // X 轴
  g.append('g').attr('transform', `translate(0,${ih})`)
    .call(d3.axisBottom(x).ticks(5))
    .call(ax => ax.select('.domain').attr('stroke', '#e2e8f0'))
    .call(ax => ax.selectAll('text').attr('fill', '#94a3b8').attr('font-size', 10))
    .call(ax => ax.selectAll('line').attr('stroke', '#e2e8f0'))

  // 右侧图例
  const lx = iw + 12
  DATASETS.forEach((ds, i) => {
    const ly = 20 + i * 22
    svg.append('rect')
      .attr('x', margin.left + lx).attr('y', margin.top + ly - 8)
      .attr('width', 12).attr('height', 12).attr('rx', 3)
      .attr('fill', DATASET_COLORS[ds]).attr('opacity', 0.85)
    svg.append('text')
      .attr('x', margin.left + lx + 16).attr('y', margin.top + ly + 2)
      .attr('font-size', 11).attr('fill', '#475569').attr('font-weight', 500)
      .text(DATASET_LABELS[ds])
  })
}

const ro = new ResizeObserver(draw)
onMounted(() => { ro.observe(el.value!); draw() })
watch(() => props.data, draw, { deep: true })
onUnmounted(() => ro.disconnect())
</script>

<style scoped>
.d3-chart { width: 100%; }
</style>
